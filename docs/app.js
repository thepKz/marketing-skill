const toast = document.querySelector('.toast');
let toastTimer;
let currentLanguage = 'vi';

const translationMap = window.HANDBOOK_I18N?.en || {};
const textNodes = [];
const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
  acceptNode(node) {
    const parentTag = node.parentElement?.tagName;
    if (!node.nodeValue.trim() || ['SCRIPT', 'STYLE', 'CODE', 'PRE'].includes(parentTag)) {
      return NodeFilter.FILTER_REJECT;
    }
    return NodeFilter.FILTER_ACCEPT;
  },
});

while (walker.nextNode()) {
  const node = walker.currentNode;
  textNodes.push({
    node,
    original: node.nodeValue,
    key: node.nodeValue.replace(/\s+/g, ' ').trim(),
  });
}

const translatedAttributes = [...document.querySelectorAll('[data-alt-en]')].map((element) => ({
  element,
  original: element.getAttribute('alt'),
  english: element.dataset.altEn,
}));

const translatedAriaLabels = [...document.querySelectorAll('[data-aria-en]')].map((element) => ({
  element,
  original: element.getAttribute('aria-label'),
  english: element.dataset.ariaEn,
}));

const translatedMeta = [...document.querySelectorAll('meta[data-content-en]')].map((element) => ({
  element,
  original: element.getAttribute('content'),
  english: element.dataset.contentEn,
}));

function setLanguage(language) {
  currentLanguage = language === 'en' ? 'en' : 'vi';
  document.documentElement.lang = currentLanguage;
  document.title = currentLanguage === 'en' ? 'FIELD Manual — Marketing-Minthep' : 'FIELD Manual — Marketing-Minthep';

  textNodes.forEach(({ node, original, key }) => {
    if (currentLanguage === 'vi' || !translationMap[key]) {
      node.nodeValue = original;
      return;
    }
    const leading = original.match(/^\s*/)?.[0] || '';
    const trailing = original.match(/\s*$/)?.[0] || '';
    node.nodeValue = `${leading}${translationMap[key]}${trailing}`;
  });

  translatedAttributes.forEach(({ element, original, english }) => {
    element.setAttribute('alt', currentLanguage === 'en' ? english : original);
  });

  translatedAriaLabels.forEach(({ element, original, english }) => {
    element.setAttribute('aria-label', currentLanguage === 'en' ? english : original);
  });

  translatedMeta.forEach(({ element, original, english }) => {
    element.setAttribute('content', currentLanguage === 'en' ? english : original);
  });

  document.querySelectorAll('[data-language]').forEach((button) => {
    button.setAttribute('aria-pressed', String(button.dataset.language === currentLanguage));
  });
  window.localStorage.setItem('marketing-minthep-language', currentLanguage);
}

document.querySelectorAll('[data-language]').forEach((button) => {
  button.addEventListener('click', () => setLanguage(button.dataset.language));
});

const requestedLanguage = new URLSearchParams(window.location.search).get('lang');
setLanguage(requestedLanguage || window.localStorage.getItem('marketing-minthep-language') || 'vi');

function showToast(message) {
  if (!toast) return;
  toast.textContent = message;
  toast.classList.add('is-visible');
  window.clearTimeout(toastTimer);
  toastTimer = window.setTimeout(() => toast.classList.remove('is-visible'), 1800);
}

document.querySelectorAll('.copy-button').forEach((button) => {
  button.addEventListener('click', async () => {
    const target = button.dataset.copyTarget;
    const text = target ? document.querySelector(target)?.textContent.trim() : button.dataset.copy;
    if (!text) return;

    try {
      await navigator.clipboard.writeText(text);
      showToast(currentLanguage === 'en' ? 'Copied to clipboard.' : 'Đã copy vào clipboard.');
    } catch {
      showToast(currentLanguage === 'en' ? 'The browser blocked automatic copying.' : 'Trình duyệt không cho phép copy tự động.');
    }
  });
});

const galleryButtons = [...document.querySelectorAll('[data-gallery-filter]')];
const galleryCards = [...document.querySelectorAll('.reference-card')];

galleryButtons.forEach((button) => {
  button.addEventListener('click', () => {
    const filter = button.dataset.galleryFilter;
    galleryButtons.forEach((item) => item.classList.toggle('is-active', item === button));
    galleryCards.forEach((card) => {
      const tags = card.dataset.tags?.split(/\s+/) || [];
      card.hidden = filter !== 'all' && !tags.includes(filter);
    });
  });
});

const navLinks = [...document.querySelectorAll('.topbar nav a')];
const sections = navLinks.map((link) => document.querySelector(link.getAttribute('href'))).filter(Boolean);

if ('IntersectionObserver' in window) {
  const observer = new IntersectionObserver(
    (entries) => {
      const visible = entries.find((entry) => entry.isIntersecting);
      if (!visible) return;
      navLinks.forEach((link) => {
        const active = link.getAttribute('href') === '#' + visible.target.id;
        if (active) link.setAttribute('aria-current', 'true');
        else link.removeAttribute('aria-current');
      });
    },
    { rootMargin: '-25% 0px -65% 0px' },
  );
  sections.forEach((section) => observer.observe(section));
}
