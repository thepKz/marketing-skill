const toast = document.querySelector('.toast');
let toastTimer;
let currentLanguage = 'vi';
let activeUseCase = 'campaign';
let activePrompt = 'campaign';

const useCases = {
  campaign: {
    vi: { title: 'Campaign system', description: 'Biến một product truth thành campaign idea, ba creative lane và hệ asset xuyên suốt paid, social, landing page.', deliverables: ['Message ladder và big idea', 'Clear, Signature, Departure lanes', 'Paid, social, landing asset matrix', 'Prompt và QA cho từng visual'], request: 'Dùng $marketing-minthep ở system mode. Hãy biến product truth và ảnh ref đính kèm thành một campaign system gồm big idea, ba creative lane, message ladder, asset matrix, copy và prompt hình ảnh có QA.' },
    en: { title: 'Campaign system', description: 'Turn one product truth into a campaign idea, three creative lanes, and a connected asset system across paid, social, and landing pages.', deliverables: ['Message ladder and big idea', 'Clear, Signature, and Departure lanes', 'Paid, social, and landing asset matrix', 'Prompts and QA for every visual'], request: 'Use $marketing-minthep in system mode. Turn the attached product truth and references into a campaign system with a big idea, three creative lanes, a message ladder, an asset matrix, copy, and image prompts with QA.' },
  },
  commerce: {
    vi: { title: 'Commerce visual system', description: 'Tạo bộ hình ảnh và nội dung bán hàng nhất quán từ hero đến PDP, marketplace, catalog, social commerce và PR kit.', deliverables: ['Packshot và image sequence', 'PDP copy và objection handling', 'Marketplace crops và safe zones', 'SKU consistency và return-reduction proof'], request: 'Dùng $marketing-minthep để tạo commerce visual system cho sản phẩm đính kèm: packshot, PDP sequence, marketplace crops, listing copy, objection handling và QA khóa logo, label, shape, material.' },
    en: { title: 'Commerce visual system', description: 'Create a consistent sales-image and content system spanning hero, PDP, marketplace, catalog, social commerce, and PR kits.', deliverables: ['Packshot and image sequence', 'PDP copy and objection handling', 'Marketplace crops and safe zones', 'SKU consistency and return-reduction proof'], request: 'Use $marketing-minthep to create a commerce visual system for the attached product: packshots, a PDP sequence, marketplace crops, listing copy, objection handling, and QA that locks the logo, label, shape, and materials.' },
  },
  content: {
    vi: { title: 'Content operating engine', description: 'Chuyển insight audience thành pillar, format, lịch sản xuất, repurposing graph và chuỗi nội dung dẫn tới hành động.', deliverables: ['Audience questions và content pillars', 'Hero-to-derivative repurposing graph', 'Social, SEO và email briefs', 'Cadence, owner và measurement'], request: 'Dùng $marketing-minthep để xây content engine từ product truth và audience: pillars, hero assets, repurposing graph, social/SEO/email briefs, cadence, CTA và measurement contract.' },
    en: { title: 'Content operating engine', description: 'Turn audience insight into pillars, formats, a production cadence, a repurposing graph, and content sequences that drive action.', deliverables: ['Audience questions and content pillars', 'Hero-to-derivative repurposing graph', 'Social, SEO, and email briefs', 'Cadence, owners, and measurement'], request: 'Use $marketing-minthep to build a content engine from the product truth and audience: pillars, hero assets, a repurposing graph, social/SEO/email briefs, cadence, CTAs, and a measurement contract.' },
  },
  pr: {
    vi: { title: 'Launch & earned media', description: 'Tìm newsworthiness thật, xây launch narrative, press assets, founder POV và paid/owned continuity mà không bịa proof.', deliverables: ['Newsworthiness gate và press angle', 'Announcement, pitch và Q&A', 'Founder content và spokesperson brief', 'Launch asset matrix và measurement'], request: 'Dùng $marketing-minthep để tạo launch và PR system. Kiểm tra newsworthiness trước, sau đó xây press angle, announcement, targeted pitch, founder POV, Q&A, asset matrix và measurement. Không bịa claim hoặc proof.' },
    en: { title: 'Launch and earned media', description: 'Find genuine newsworthiness and build a launch narrative, press assets, founder POV, and paid/owned continuity without fabricated proof.', deliverables: ['Newsworthiness gate and press angle', 'Announcement, pitch, and Q&A', 'Founder content and spokesperson brief', 'Launch asset matrix and measurement'], request: 'Use $marketing-minthep to create a launch and PR system. Gate newsworthiness first, then build a press angle, announcement, targeted pitch, founder POV, Q&A, asset matrix, and measurement. Do not fabricate claims or proof.' },
  },
  virtual: {
    vi: { title: 'Virtual-person bible', description: 'Thiết kế một người ảo trưởng thành có sức hút, tỷ lệ cơ thể lành mạnh, đặc điểm nhận diện ổn định và nhiều nhánh hình ảnh có kiểm soát.', deliverables: ['Option cảm giác trước khi chọn mặt', 'Identity, body và styling locks', 'Makeup, pose và capture grammar', '4–5 branches cùng rejection gates'], request: 'Dùng $marketing-minthep để thiết kế một virtual adult. Trước tiên cho tôi các option về cảm giác và tác động thương hiệu; sau khi chọn, tạo identity bible, healthy body profile, makeup/styling grammar, 4–5 visual branches và rejection gates.' },
    en: { title: 'Virtual-person bible', description: 'Design an appealing fictional adult with healthy body proportions, stable identifying traits, and multiple controlled visual branches.', deliverables: ['Impression options before facial design', 'Identity, body, and styling locks', 'Makeup, pose, and capture grammar', '4–5 branches with rejection gates'], request: 'Use $marketing-minthep to design a fictional adult. First give me impression and brand-impact options; after selection, create an identity bible, healthy body profile, makeup and styling grammar, 4–5 visual branches, and rejection gates.' },
  },
};

const prompts = {
  campaign: {
    vi: `Dùng $marketing-minthep ở system mode.\nSản phẩm: [bạn bán gì]\nMục tiêu: [launch / bán / giáo dục / PR]\nAudience: [ai cần nó]\nKênh: [web / social / paid / marketplace]\n\nHãy map ảnh ref theo vai trò, đề xuất hướng tốt nhất, tạo bốn nhánh visual có kiểm soát và trả copy, asset plan, provider-ready prompts, QA gates cùng quyết định tiếp theo.`,
    en: `Use $marketing-minthep in system mode.\nProduct: [what you sell]\nGoal: [launch / sell / educate / PR]\nAudience: [who needs it]\nChannels: [web / social / paid / marketplace]\n\nMap my references by role, recommend the strongest direction, create four controlled visual branches, and return copy, an asset plan, provider-ready prompts, QA gates, and the next decision.`,
  },
  product: {
    vi: `Dùng $marketing-minthep cho sản phẩm trong ảnh đính kèm.\nKhóa: logo, label, hình dáng, tỷ lệ và vật liệu.\nMục đích: [PDP / marketplace / social / PR kit]\n\nTạo packshot hero và bốn biến thể chỉ đổi một trục mỗi lần. Trả composition spec, lighting, crop plan, prompt theo provider và QA product fidelity.`,
    en: `Use $marketing-minthep for the product in the attached images.\nLock: logo, label, shape, proportions, and materials.\nUse: [PDP / marketplace / social / PR kit]\n\nCreate one hero packshot and four variants that change one axis at a time. Return composition specs, lighting, crop plans, provider prompts, and product-fidelity QA.`,
  },
  person: {
    vi: `Dùng $marketing-minthep để tạo một người ảo trưởng thành cho [brand/use case].\nCảm giác mong muốn: [ấm áp / thông minh / sắc sảo / khác biệt]\nBody preference: mảnh khỏe mạnh, tỷ lệ tự nhiên, không extreme thinness.\n\nCho tôi option và trade-off trước. Sau khi chọn, tạo identity bible, styling, makeup, pose grammar và bốn nhánh visual nhất quán.`,
    en: `Use $marketing-minthep to create a fictional adult for [brand/use case].\nDesired impression: [warm / intelligent / precise / distinctive]\nBody preference: healthy slender build, natural proportions, no extreme thinness.\n\nGive me options and trade-offs first. After selection, create an identity bible, styling, makeup, pose grammar, and four consistent visual branches.`,
  },
  edit: {
    vi: `Dùng $marketing-minthep để edit người trưởng thành trong ảnh đính kèm. Tôi có quyền chỉnh sửa ảnh này.\nChỉ thay: [makeup / outfit].\nKhóa tuyệt đối: identity, facial geometry, skin tone, tuổi, biểu cảm, gaze, pose, body proportions, camera, crop và ánh sáng.\n\nTạo edit contract gồm change, lock, match, mask và reject. Nếu khuôn mặt drift, reject thay vì beautify.`,
    en: `Use $marketing-minthep to edit the adult in the attached image. I have permission to edit it.\nChange only: [makeup / outfit].\nAbsolute locks: identity, facial geometry, skin tone, age, expression, gaze, pose, body proportions, camera, crop, and lighting.\n\nCreate an edit contract with change, lock, match, mask, and reject rules. Reject facial drift instead of beautifying it.`,
  },
};

const translationMap = window.HANDBOOK_I18N?.en || {};
const textNodes = [];
const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
  acceptNode(node) {
    const parentTag = node.parentElement?.tagName;
    if (!node.nodeValue.trim() || ['SCRIPT', 'STYLE', 'CODE', 'PRE'].includes(parentTag)) return NodeFilter.FILTER_REJECT;
    return NodeFilter.FILTER_ACCEPT;
  },
});

while (walker.nextNode()) {
  const node = walker.currentNode;
  textNodes.push({ node, original: node.nodeValue, key: node.nodeValue.replace(/\s+/g, ' ').trim() });
}

const translatedAttributes = [...document.querySelectorAll('[data-alt-en]')].map((element) => ({ element, original: element.getAttribute('alt'), english: element.dataset.altEn }));
const translatedAriaLabels = [...document.querySelectorAll('[data-aria-en]')].map((element) => ({ element, original: element.getAttribute('aria-label'), english: element.dataset.ariaEn }));
const translatedMeta = [...document.querySelectorAll('meta[data-content-en]')].map((element) => ({ element, original: element.getAttribute('content'), english: element.dataset.contentEn }));

function renderUseCase() {
  const content = useCases[activeUseCase][currentLanguage];
  document.querySelector('[data-use-case-title]').textContent = content.title;
  document.querySelector('[data-use-case-description]').textContent = content.description;
  document.querySelector('[data-use-case-deliverables]').innerHTML = content.deliverables.map((item) => `<li>${item}</li>`).join('');
  const copyButton = document.querySelector('[data-use-case-copy]');
  copyButton.dataset.copy = content.request;
  copyButton.textContent = currentLanguage === 'en' ? 'Copy request' : 'Copy request mẫu';
}

function renderPrompt() {
  document.querySelector('#starter-prompt code').textContent = prompts[activePrompt][currentLanguage];
}

function setLanguage(language) {
  currentLanguage = language === 'en' ? 'en' : 'vi';
  document.documentElement.lang = currentLanguage;
  document.title = currentLanguage === 'en' ? 'Marketing-Minthep — Marketing and Visual Skill' : 'Marketing-Minthep — Marketing & Visual Skill';
  textNodes.forEach(({ node, original, key }) => {
    const leading = original.match(/^\s*/)?.[0] || '';
    const trailing = original.match(/\s*$/)?.[0] || '';
    node.nodeValue = currentLanguage === 'en' && translationMap[key] ? `${leading}${translationMap[key]}${trailing}` : original;
  });
  translatedAttributes.forEach(({ element, original, english }) => element.setAttribute('alt', currentLanguage === 'en' ? english : original));
  translatedAriaLabels.forEach(({ element, original, english }) => element.setAttribute('aria-label', currentLanguage === 'en' ? english : original));
  translatedMeta.forEach(({ element, original, english }) => element.setAttribute('content', currentLanguage === 'en' ? english : original));
  document.querySelectorAll('[data-language]').forEach((button) => button.setAttribute('aria-pressed', String(button.dataset.language === currentLanguage)));
  renderUseCase();
  renderPrompt();
  window.localStorage.setItem('marketing-minthep-language', currentLanguage);
}

function showToast(message) {
  if (!toast) return;
  toast.textContent = message;
  toast.classList.add('is-visible');
  window.clearTimeout(toastTimer);
  toastTimer = window.setTimeout(() => toast.classList.remove('is-visible'), 1800);
}

document.querySelectorAll('[data-language]').forEach((button) => button.addEventListener('click', () => setLanguage(button.dataset.language)));

document.querySelectorAll('[data-use-case]').forEach((button) => {
  button.addEventListener('click', () => {
    activeUseCase = button.dataset.useCase;
    document.querySelectorAll('[data-use-case]').forEach((item) => {
      item.setAttribute('aria-selected', String(item === button));
      item.tabIndex = item === button ? 0 : -1;
    });
    renderUseCase();
  });
  button.addEventListener('keydown', (event) => {
    if (!['ArrowDown', 'ArrowRight', 'ArrowUp', 'ArrowLeft'].includes(event.key)) return;
    event.preventDefault();
    const tabs = [...document.querySelectorAll('[data-use-case]')];
    const delta = ['ArrowDown', 'ArrowRight'].includes(event.key) ? 1 : -1;
    const target = tabs[(tabs.indexOf(button) + delta + tabs.length) % tabs.length];
    target.focus();
    target.click();
  });
});

document.querySelectorAll('[data-prompt-choice]').forEach((button) => {
  button.addEventListener('click', () => {
    activePrompt = button.dataset.promptChoice;
    document.querySelectorAll('[data-prompt-choice]').forEach((item) => {
      item.classList.toggle('is-active', item === button);
      item.setAttribute('aria-pressed', String(item === button));
    });
    renderPrompt();
  });
});

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
galleryButtons.forEach((button) => button.addEventListener('click', () => {
  const filter = button.dataset.galleryFilter;
  galleryButtons.forEach((item) => {
    item.classList.toggle('is-active', item === button);
    item.setAttribute('aria-pressed', String(item === button));
  });
  galleryCards.forEach((card) => { card.hidden = filter !== 'all' && !(card.dataset.tags?.split(/\s+/) || []).includes(filter); });
}));

const dialog = document.querySelector('.image-dialog');
const dialogImage = dialog?.querySelector('img');
const dialogCaption = dialog?.querySelector('p');
document.querySelectorAll('.image-open').forEach((button) => button.addEventListener('click', () => {
  if (!dialog || !dialogImage || !dialogCaption) return;
  dialogImage.src = button.dataset.image;
  dialogImage.alt = button.querySelector('img')?.alt || '';
  dialogCaption.textContent = button.dataset.caption || '';
  dialog.showModal();
}));
dialog?.querySelector('.dialog-close')?.addEventListener('click', () => dialog.close());
dialog?.addEventListener('click', (event) => {
  const bounds = dialog.getBoundingClientRect();
  const outside = event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom;
  if (outside) dialog.close();
});

const navLinks = [...document.querySelectorAll('.topbar nav a')];
const sections = navLinks.map((link) => document.querySelector(link.getAttribute('href'))).filter(Boolean);
if ('IntersectionObserver' in window) {
  const observer = new IntersectionObserver((entries) => {
    const visible = entries.filter((entry) => entry.isIntersecting).sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
    if (!visible) return;
    navLinks.forEach((link) => link.getAttribute('href') === `#${visible.target.id}` ? link.setAttribute('aria-current', 'true') : link.removeAttribute('aria-current'));
  }, { rootMargin: '-25% 0px -65% 0px', threshold: [0, 0.2, 0.5] });
  sections.forEach((section) => observer.observe(section));
}

const requestedLanguage = new URLSearchParams(window.location.search).get('lang');
setLanguage(requestedLanguage || window.localStorage.getItem('marketing-minthep-language') || 'vi');
