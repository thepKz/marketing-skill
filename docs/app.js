const pageState = {
  archiveFilter: 'all',
  archiveLimit: 16,
  dialogItems: [],
  dialogIndex: 0,
};

const assetList = Array.isArray(window.SHOWCASE_ASSETS) ? window.SHOWCASE_ASSETS : [];
const meta = window.SHOWCASE_META || { published: assetList.length, internalReferences: 0 };

document.querySelectorAll('[data-published-count]').forEach((node) => { node.textContent = meta.published || assetList.length; });
document.querySelectorAll('[data-reference-count]').forEach((node) => { node.textContent = meta.internalReferences || 0; });

const toast = document.querySelector('.toast');
let toastTimer;
function showToast(message = 'Đã copy.') {
  if (!toast) return;
  toast.textContent = message;
  toast.classList.add('is-visible');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove('is-visible'), 1800);
}

document.querySelectorAll('.copy-button').forEach((button) => {
  button.addEventListener('click', async () => {
    const text = button.dataset.copy || '';
    try {
      await navigator.clipboard.writeText(text);
      showToast('Đã copy.');
    } catch {
      const helper = document.createElement('textarea');
      helper.value = text;
      helper.style.position = 'fixed';
      helper.style.opacity = '0';
      document.body.appendChild(helper);
      helper.select();
      document.execCommand('copy');
      helper.remove();
      showToast('Đã copy.');
    }
  });
});

const dialog = document.querySelector('.lightbox');
const dialogImage = dialog?.querySelector('img');
const dialogCaption = dialog?.querySelector('figcaption');

function updateDialog() {
  const item = pageState.dialogItems[pageState.dialogIndex];
  if (!item || !dialogImage || !dialogCaption) return;
  dialogImage.src = item.src;
  dialogImage.alt = item.alt || item.caption || '';
  dialogCaption.textContent = item.caption || '';
}

function openDialog(items, index = 0) {
  if (!dialog) return;
  pageState.dialogItems = items;
  pageState.dialogIndex = Math.max(0, Math.min(index, items.length - 1));
  updateDialog();
  dialog.showModal();
}

function moveDialog(direction) {
  if (pageState.dialogItems.length < 2) return;
  pageState.dialogIndex = (pageState.dialogIndex + direction + pageState.dialogItems.length) % pageState.dialogItems.length;
  updateDialog();
}

function bindStaticImageTriggers() {
  const triggers = [...document.querySelectorAll('.image-trigger')];
  const items = triggers.map((trigger) => ({
    src: trigger.dataset.image,
    alt: trigger.querySelector('img')?.alt || '',
    caption: trigger.dataset.caption || '',
  }));
  triggers.forEach((trigger, index) => trigger.addEventListener('click', () => openDialog(items, index)));
}

dialog?.querySelector('.lightbox-close')?.addEventListener('click', () => dialog.close());
dialog?.querySelector('.lightbox-prev')?.addEventListener('click', () => moveDialog(-1));
dialog?.querySelector('.lightbox-next')?.addEventListener('click', () => moveDialog(1));
dialog?.addEventListener('click', (event) => { if (event.target === dialog) dialog.close(); });
document.addEventListener('keydown', (event) => {
  if (!dialog?.open) return;
  if (event.key === 'ArrowLeft') moveDialog(-1);
  if (event.key === 'ArrowRight') moveDialog(1);
});

const archiveGrid = document.querySelector('[data-archive-grid]');
const archiveStatus = document.querySelector('[data-archive-status]');
const archiveMore = document.querySelector('[data-archive-more]');

function filteredAssets() {
  if (pageState.archiveFilter === 'all') return assetList;
  return assetList.filter((asset) => asset.category === pageState.archiveFilter);
}

function renderArchive() {
  if (!archiveGrid) return;
  const filtered = filteredAssets();
  const visible = filtered.slice(0, pageState.archiveLimit);
  archiveGrid.innerHTML = visible.map((asset, index) => `
    <figure class="archive-item" data-fit="${asset.fit || 'cover'}">
      <button type="button" data-archive-index="${index}" aria-label="Mở ${asset.title}">
        <img src="${asset.src}" alt="${asset.title}" loading="lazy" width="${asset.width || 1}" height="${asset.height || 1}" />
      </button>
      <figcaption><span>${asset.title}</span><span>${asset.category}</span></figcaption>
    </figure>
  `).join('');

  archiveGrid.querySelectorAll('[data-archive-index]').forEach((button) => {
    button.addEventListener('click', () => {
      const items = visible.map((asset) => ({ src: asset.src, alt: asset.title, caption: `${asset.title} · ${asset.category}` }));
      openDialog(items, Number(button.dataset.archiveIndex));
    });
  });

  if (archiveStatus) archiveStatus.textContent = `${Math.min(visible.length, filtered.length)} / ${filtered.length} output`;
  if (archiveMore) archiveMore.hidden = visible.length >= filtered.length;
}

document.querySelectorAll('[data-filter]').forEach((button) => {
  button.addEventListener('click', () => {
    pageState.archiveFilter = button.dataset.filter;
    pageState.archiveLimit = 16;
    document.querySelectorAll('[data-filter]').forEach((item) => item.classList.toggle('is-active', item === button));
    renderArchive();
  });
});

archiveMore?.addEventListener('click', () => {
  pageState.archiveLimit += 16;
  renderArchive();
});

const menuButtons = [...document.querySelectorAll('[data-menu-target]')];
const menuWorks = [...document.querySelectorAll('.menu-work')];
menuButtons.forEach((button) => {
  button.addEventListener('click', () => {
    const target = document.getElementById(button.dataset.menuTarget);
    menuButtons.forEach((item) => item.classList.toggle('is-active', item === button));
    target?.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'center' });
  });
});

if ('IntersectionObserver' in window && menuWorks.length) {
  const observer = new IntersectionObserver((entries) => {
    const visible = entries.filter((entry) => entry.isIntersecting).sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
    if (!visible) return;
    menuButtons.forEach((button) => button.classList.toggle('is-active', button.dataset.menuTarget === visible.target.id));
  }, { rootMargin: '-20% 0px -55% 0px', threshold: [0.15, 0.4, 0.7] });
  menuWorks.forEach((item) => observer.observe(item));
}

const header = document.querySelector('[data-header]');
function updateHeader() {
  header?.classList.toggle('is-scrolled', scrollY > 24);
}
addEventListener('scroll', updateHeader, { passive: true });
updateHeader();

function initMotion() {
  const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduceMotion || !window.gsap) return;
  const gsap = window.gsap;
  const ScrollTrigger = window.ScrollTrigger;
  if (ScrollTrigger) gsap.registerPlugin(ScrollTrigger);

  gsap.timeline({ defaults: { ease: 'power3.out' } })
    .from('.hero-copy > *', { y: 22, autoAlpha: 0, duration: .72, stagger: .08 })
    .from('.hero-frame-main', { clipPath: 'inset(0 100% 0 0)', duration: 1 }, '-=.55')
    .from('.hero-frame-tall, .hero-frame-small', { y: 28, autoAlpha: 0, duration: .75, stagger: .12 }, '-=.55');

  if (!ScrollTrigger) return;
  gsap.to('.scroll-progress', { width: '100%', ease: 'none', scrollTrigger: { start: 'top top', end: 'max', scrub: .15 } });
  gsap.utils.toArray('.reveal').forEach((element) => {
    gsap.from(element, { y: 32, autoAlpha: 0, duration: .85, ease: 'power3.out', scrollTrigger: { trigger: element, start: 'top 86%', once: true } });
  });
  gsap.utils.toArray('.menu-work button').forEach((media) => {
    gsap.from(media, { clipPath: 'inset(8% 0 8% 0)', duration: 1, ease: 'power2.out', scrollTrigger: { trigger: media, start: 'top 84%', once: true } });
  });
}

bindStaticImageTriggers();
renderArchive();
initMotion();
