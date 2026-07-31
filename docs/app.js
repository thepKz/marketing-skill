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
    vi: { title: 'Content operating engine', description: 'Chuyển insight audience thành pillar, format, lịch sản xuất, repurposing graph và chuỗi nội dung dẫn tới hành động.', deliverables: ['Câu hỏi của audience và content pillars', 'Sơ đồ tái sử dụng từ hero ra biến thể', 'Social, SEO và email briefs', 'Cadence, owner và measurement'], request: 'Dùng $marketing-minthep để xây content engine từ product truth và audience: pillars, hero assets, repurposing graph, social/SEO/email briefs, cadence, CTA và measurement contract.' },
    en: { title: 'Content operating engine', description: 'Turn audience insight into pillars, formats, a production cadence, a repurposing graph, and content sequences that drive action.', deliverables: ['Audience questions and content pillars', 'Hero-to-derivative repurposing graph', 'Social, SEO, and email briefs', 'Cadence, owners, and measurement'], request: 'Use $marketing-minthep to build a content engine from the product truth and audience: pillars, hero assets, a repurposing graph, social/SEO/email briefs, cadence, CTAs, and a measurement contract.' },
  },
  pr: {
    vi: { title: 'Launch & earned media', description: 'Tìm newsworthiness thật, xây launch narrative, press assets, founder POV và paid/owned continuity mà không bịa proof.', deliverables: ['Newsworthiness gate và press angle', 'Announcement, pitch và Q&A', 'Founder content và spokesperson brief', 'Launch asset matrix và measurement'], request: 'Dùng $marketing-minthep để tạo launch và PR system. Kiểm tra newsworthiness trước, sau đó xây press angle, announcement, targeted pitch, founder POV, Q&A, asset matrix và measurement. Không bịa claim hoặc proof.' },
    en: { title: 'Launch and earned media', description: 'Find genuine newsworthiness and build a launch narrative, press assets, founder POV, and paid/owned continuity without fabricated proof.', deliverables: ['Newsworthiness gate and press angle', 'Announcement, pitch, and Q&A', 'Founder content and spokesperson brief', 'Launch asset matrix and measurement'], request: 'Use $marketing-minthep to create a launch and PR system. Gate newsworthiness first, then build a press angle, announcement, targeted pitch, founder POV, Q&A, asset matrix, and measurement. Do not fabricate claims or proof.' },
  },
  virtual: {
    // Was "impression options before facial design", which stopped being true when the adjectives
    // became a parameter table. A person described as "warm, elegant" renders as a different face
    // every time; a person described in numbers with an id over them renders as the same one twice.
    vi: { title: 'Virtual-person bible', description: 'Thiết kế một người ảo trưởng thành mô tả bằng số đo thay vì tính từ, tỷ lệ cơ thể lành mạnh, có id để render lại đúng người đó ở ảnh sau.', deliverables: ['Bảng tham số đo được, không phải tính từ', 'Trục nào khóa cứng, trục nào được đổi', 'Makeup, pose và capture grammar', 'Kiểm tra drift: trục khóa nào đã bị xê dịch'], request: 'Dùng $marketing-minthep để thiết kế một virtual adult cho [brand/use case]. Cho tôi bảng tham số bằng số đo kèm person_id, ghi rõ trục nào khóa và trục nào được phép đổi, sau đó makeup/styling grammar, 4–5 visual branches và rejection gates. Ảnh sau phải kiểm được là cùng một người.' },
    en: { title: 'Virtual-person bible', description: 'Design a fictional adult specified in measurements rather than adjectives, with healthy proportions and an id that renders the same person again in the next photo.', deliverables: ['A measurable parameter sheet, not adjectives', 'Which axes are locked and which may vary', 'Makeup, pose, and capture grammar', 'A drift check: which locked axis moved'], request: 'Use $marketing-minthep to design a fictional adult for [brand/use case]. Give me the parameter sheet in measurements with a person_id, state which axes are locked and which may vary, then makeup and styling grammar, 4–5 visual branches, and rejection gates. The next photo has to be checkable as the same person.' },
  },
  menu: {
    vi: { title: 'Menu & food visual system', description: 'Biến một món ăn hoặc ảnh món có sẵn thành menu có logic: định vị, nhóm món, hierarchy, giá, wireframe và prompt chụp.', deliverables: ['Ba hướng menu để chọn', 'Thứ tự thông tin và cách đặt giá', 'Shot list ảnh và hình vẽ', 'Crop cho bản in, QR và social'], request: 'Dùng $marketing-minthep cho món bún bò trong ảnh đính kèm. Hãy nghiên cứu bối cảnh quán và khách văn phòng, đề xuất 3 hướng menu (hiện đại, truyền thống, premium), wireframe từng hướng, thứ tự món, cách đặt giá, palette, shot list và prompt hình ảnh. Trả về file Markdown.' },
    en: { title: 'Menu and food visual system', description: 'Turn one dish or food reference into a menu system with positioning, hierarchy, pricing, wireframes, and a photo brief.', deliverables: ['Menu direction options', 'Information hierarchy and pricing', 'Photo / illustration shot list', 'Print, QR, and social crops'], request: 'Use $marketing-minthep for the attached bowl of bun bo hue. Research the venue and office-lunch audience, propose three menu directions (modern, traditional, premium), wireframes, item order, pricing presentation, palette, shot list, and image prompts. Return Markdown files.' },
  },
  photoshoot: {
    vi: { title: 'Photoshoot art direction', description: 'Lập concept chụp hoàn chỉnh từ bố cục, lens, ánh sáng, bề mặt, màu, đạo cụ đến shot list và tiêu chí chọn ảnh.', deliverables: ['Moodboard và luật bố cục', 'Công thức sáng và đổ bóng', 'Kế hoạch set, đạo cụ, chất liệu', 'Shot list kèm phương án dự phòng'], request: 'Dùng $marketing-minthep với ảnh sản phẩm/ref đính kèm. Hãy xây art direction cho một buổi photoshoot: concept, bố cục, lens, camera angle, màu sắc, chất liệu, ánh sáng và đổ bóng. Tạo shot list, prompt theo từng frame, độ phân giải đầu ra và checklist reject.' },
    en: { title: 'Photoshoot art direction', description: 'Plan a complete shoot across composition, lens, light, surfaces, palette, props, shot list, and image-selection criteria.', deliverables: ['Moodboard and composition rules', 'Lighting and shadow recipe', 'Set, prop, and material plan', 'Shot list with alternates'], request: 'Use $marketing-minthep with the attached product/reference images. Build a full photoshoot art direction: concept, composition, lens, camera angle, palette, materials, lighting, and shadows. Return a shot list, per-frame prompts, output resolution, and reject checklist.' },
  },
  video: {
    vi: { title: 'Video campaign brief', description: 'Chuyển campaign hoặc key visual thành storyboard, nhịp dựng, âm thanh, frame list và prompt video có thể sản xuất.', deliverables: ['Option concept 15s và 30s', 'Storyboard theo từng beat', 'Chuyển động camera và hướng máy', 'Thông số dựng, caption và xuất file'], request: 'Dùng $marketing-minthep để chuyển campaign này thành video 15s và 30s. Đề xuất 3 concept, storyboard theo beat, chuyển động camera, ánh sáng, âm thanh, caption, frame đầu/cuối, prompt video và thông số xuất cho TikTok, Reels, YouTube.' },
    en: { title: 'Video campaign brief', description: 'Turn a campaign or key visual into a producible storyboard, edit rhythm, sound direction, frame list, and video prompts.', deliverables: ['15s / 30s concept options', 'Storyboard and beat sheet', 'Camera and motion direction', 'Edit, caption, and delivery specs'], request: 'Use $marketing-minthep to turn this campaign into 15s and 30s videos. Propose three concepts, beat-by-beat storyboards, camera motion, light, sound, captions, opening/closing frames, video prompts, and delivery specs for TikTok, Reels, and YouTube.' },
  },
  edit: {
    vi: { title: 'Edit ảnh có kiểm soát', description: 'Sửa makeup, outfit, nền hoặc mood từ ảnh ref mà vẫn khóa identity, sản phẩm, ánh sáng và tỷ lệ.', deliverables: ['Edit contract: đổi gì / khóa gì / mask gì', 'Prompt cho từng phiên bản trước và sau', 'QA giữ đúng identity và đúng sản phẩm', 'Crop xuất cho từng kênh'], request: 'Dùng $marketing-minthep để chỉnh ảnh đính kèm. Hãy hỏi tôi phần cần đổi nếu chưa rõ, sau đó tạo edit contract: change, lock, mask, match, reject; prompt cho từng phiên bản và crop xuất cho web, social, marketplace. Bật image edit mode.' },
    en: { title: 'Controlled image edit', description: 'Change makeup, outfit, background, or mood from a reference while locking identity, product, lighting, and proportions.', deliverables: ['Edit contract: change / lock / mask', 'Before–after prompt variants', 'Identity and product fidelity QA', 'Export crops for each channel'], request: 'Use $marketing-minthep to edit the attached image. Ask only what is unclear, then create an edit contract with change, lock, mask, match, and reject rules; prompts for each version; and channel crops for web, social, and marketplace. Enable image edit mode.' },
  },
  // The four below are the decision questions, and they were missing from this grid while the tools
  // that answer them shipped months ago. A tool nobody can find from the front page is a tool that
  // does not exist, which is the same defect the README had until it was recounted. Each request
  // string names the script on purpose: these four answers are arithmetic, and a plausible number
  // recalled from memory looks exactly like a computed one once it is written down.
  pricing: {
    vi: { title: 'Giá, khuyến mãi và ROAS hòa vốn', description: 'Tính xem một mức giảm giá thật sự lấy đi bao nhiêu lợi nhuận và phải bán thêm bao nhiêu để bù, trước khi treo banner sale.', deliverables: ['Contribution mỗi đơn và tỷ lệ trên giá', 'ROAS hòa vốn: dưới mức này là bán lỗ', 'Số lần đơn phải tăng để giữ nguyên lãi', 'Trần CAC, và trần nào đang chặn'], request: 'Dùng $marketing-minthep. Giá bán [số], chi phí biến đổi mỗi đơn [số], tôi đang định giảm [số]%. Chạy scripts/price_offer.py rồi đọc kết quả: contribution, ROAS hòa vốn, số đơn phải tăng để bù, trần CAC. Đừng tính nhẩm, và nếu mức giảm này không gánh được thì nói thẳng.' },
    en: { title: 'Pricing, offers, and break-even ROAS', description: 'Work out what a discount actually costs and how many more units it takes to stay level, before the sale banner goes up.', deliverables: ['Contribution per unit and share of price', 'Break-even ROAS: below it, every sale loses', 'Unit multiple needed to hold gross profit', 'CAC ceilings, and which one binds'], request: 'Use $marketing-minthep. Price [number], variable cost per unit [number], planned discount [number]%. Run scripts/price_offer.py and read the result: contribution, break-even ROAS, the unit multiple needed to stay level, and the CAC ceiling. Do not hand-calculate it, and say plainly if the discount is not survivable.' },
  },
  measure: {
    vi: { title: 'Báo cáo KPI và balanced scorecard', description: 'Chọn đúng chỉ số để báo cáo, gắn mỗi chỉ số với một nguồn số và một người chịu trách nhiệm, rồi chấm xem kỳ này đạt hay không.', deliverables: ['Scorecard nhiều khối, không chỉ doanh thu', 'Mỗi metric có định nghĩa, nguồn, tần suất, owner', 'Ngưỡng đạt / cần xem lại / trượt', 'Chỉ số nào chưa chấm được, và thiếu gì'], request: 'Dùng $marketing-minthep để dựng scorecard cho [business]. Mỗi chỉ số phải có định nghĩa, nguồn số liệu, tần suất và owner. Sau đó chấm bằng scripts/score_kpi.py và nói thẳng chỉ số nào chưa đủ dữ liệu để chấm thay vì để trống cho đẹp bảng.' },
    en: { title: 'KPI reporting and balanced scorecard', description: 'Pick the metrics worth reporting, tie each to a data source and an owner, then score whether the period actually hit them.', deliverables: ['A scorecard with more than revenue on it', 'Every metric: definition, source, cadence, owner', 'Hit / review / miss thresholds', 'Which metrics cannot be scored yet, and why'], request: 'Use $marketing-minthep to build a scorecard for [business]. Every metric needs a definition, a data source, a cadence, and an owner. Then score it with scripts/score_kpi.py and say plainly which metrics lack the data to be scored, instead of leaving a tidy blank.' },
  },
  experiment: {
    vi: { title: 'Đọc kết quả A/B mà không tự lừa mình', description: 'Trước khi tin một biến thể thắng: test đã đủ lớn để nói lên điều gì chưa, còn thiếu bao nhiêu click, và mấy ngày nữa mới đọc được.', deliverables: ['Cỡ mẫu cần cho mức lift muốn thấy', 'Số click còn thiếu, đổi ra số ngày', 'Chênh lệch quan sát so với mức nhiễu', 'Từ chối công bố winner khi chưa đủ'], request: 'Dùng $marketing-minthep. Tôi đang chạy A/B [mô tả]: control [clicks/conversions], biến thể [clicks/conversions]. Chạy scripts/check_test_readout.py xem đã đọc được chưa. Nếu chưa thì cho tôi số click còn thiếu và số ngày, và đừng gọi tên người thắng.' },
    en: { title: 'Reading an A/B test honestly', description: 'Before believing a winner: is the test big enough to say anything yet, how many clicks short is it, and how many days is that.', deliverables: ['Sample size needed for the lift you want to see', 'Clicks still missing, converted into days', 'Observed gap against the noise floor', 'A refusal to name a winner while it is short'], request: 'Use $marketing-minthep. I am running an A/B test on [description]: control [clicks/conversions], variant [clicks/conversions]. Run scripts/check_test_readout.py to see whether it is readable yet. If it is not, give me the shortfall in clicks and days, and do not name a winner.' },
  },
  rewrite: {
    vi: { title: 'Viết lại bản nháp cho ra giọng người', description: 'Chữa một bản nháp đọc như máy dịch: nhịp câu đều tăm tắp, tính từ không ai kiểm chứng được, đại từ đổi giữa bài.', deliverables: ['Đo nhịp câu và độ lặp cách mở đầu', 'Đếm chi tiết kiểm chứng được trong bài', 'Bắt giọng dịch theo từng pattern có tên', 'Chốt một cách gọi khách và giữ suốt bài'], request: 'Dùng $marketing-minthep để sửa bản nháp đính kèm. Chạy scripts/check_specificity.py trước, rồi scripts/rewrite_human.py, rồi scripts/check_address_register.py nếu là tiếng Việt. Chỉ ra câu nào đối thủ nào cũng dùng được rồi sửa lại. Giữ nguyên fact, không thêm claim mới.' },
    en: { title: 'Rewriting a draft so it reads human', description: 'Repair a draft that reads translated: sentences all one length, adjectives nobody can check, and a form of address that changes mid-page.', deliverables: ['Sentence-rhythm and opening-repetition measurements', 'A count of the checkable details in the draft', 'Translation tells caught as named patterns', 'One form of address, decided and held'], request: 'Use $marketing-minthep to fix the attached draft. Run scripts/check_specificity.py first, then scripts/rewrite_human.py, then scripts/check_address_register.py for Vietnamese. Point at the sentences any competitor could ship unchanged and rewrite them. Keep the facts, add no new claims.' },
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

// The reference gallery used to carry a makeup/pose/candid/full-body/editorial filter bar over
// twenty scraped photographs. Seventeen of those had unresolved rights and were deleted; three
// Creative Commons images remain, and five filters over three items is a control that only ever
// hides things. The filter bar and its handler went with them.

const dialog = document.querySelector('.image-dialog');
const dialogImage = dialog?.querySelector('img');
const dialogCaption = dialog?.querySelector('p');
document.querySelectorAll('.image-open').forEach((button) => button.addEventListener('click', () => {
  if (!dialog || !dialogImage || !dialogCaption) return;
  dialogImage.src = button.dataset.image;
  dialogImage.alt = button.querySelector('img')?.alt || '';
  // The caption is an attribute, so the tree walker never sees it and the English edition used to
  // open every lightbox with a Vietnamese line under it. data-caption-en mirrors data-alt-en.
  const caption = currentLanguage === 'en' ? button.dataset.captionEn || button.dataset.caption : button.dataset.caption;
  dialogCaption.textContent = caption || '';
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
