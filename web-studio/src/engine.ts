import type {
  AssetRow,
  CreativeLane,
  GeneratedCampaign,
  IndustryId,
  LaneId,
  ProviderId,
  StudioForm,
} from './types'

export const RAW_HUMAN_OPENING =
  'Create a completely RAW quality, unprocessed, unedited image with full iPhone camera quality.'

export const defaultForm: StudioForm = {
  project: 'Barrier Reset / Launch 01',
  product: 'Serum phục hồi hàng rào da',
  objective: 'Ra mắt sản phẩm và tạo nhu cầu mua thử',
  audience: 'Nữ 22-30 tại Việt Nam, routine nhiều active, da dễ khô căng',
  market: 'Việt Nam / Vietnamese',
  offer: 'Routine phục hồi tối giản; ưu đãi launch chưa xác nhận',
  proof: 'Cơ chế hỗ trợ hàng rào da; chờ dữ liệu thành phần và thử nghiệm',
  productTruth: 'Chai thủy tinh mờ xanh xám; chưa có packshot chính thức',
  brandNotes: 'Tactile, direct, precise. Không quá clinical hoặc luxury.',
  antiReferences: 'Petals, water splash, pastel pedestal, glass skin, fake clinical charts',
  referenceNotes: 'Ánh sáng cửa sổ thật, vật liệu giấy và kính mờ, bố cục lệch trục',
  industry: 'beauty',
  provider: 'openai',
  subjectMode: 'product',
  lane: 'auto',
  channels: ['meta', 'tiktok', 'web'],
  ratio: '4:5',
  kpopDefault: true,
}

type IndustryProfile = {
  tension: string
  desiredBelief: string
  mechanism: string
  proof: string
  antiReflex: string
  clear: Omit<CreativeLane, 'id' | 'name'>
  signature: Omit<CreativeLane, 'id' | 'name'>
  departure: Omit<CreativeLane, 'id' | 'name'>
}

const profiles: Record<IndustryId, IndustryProfile> = {
  beauty: {
    tension: 'Routine càng dài nhưng da chưa chắc càng ổn.',
    desiredBelief: 'Da cần đúng cơ chế phục hồi, không cần thêm một lớp hứa hẹn.',
    mechanism: 'Biến cơ chế hỗ trợ hàng rào da thành một hệ thống hình ảnh có thể nhìn thấy.',
    proof: 'Texture, cách dùng, thành phần và kết quả chỉ xuất hiện khi có bằng chứng thật.',
    antiReflex: 'Da nhựa, cánh hoa, splash nước, pedestal pastel và đồ họa clinical giả.',
    clear: {
      idea: 'Đặt sản phẩm và lợi ích vào một khoảnh khắc phục hồi dễ hiểu.',
      headline: 'Da ổn lại. Routine nhẹ đi.',
      visualGrammar: 'Kính mờ, ánh sáng cửa sổ, một lớp màng bảo vệ, nhiều khoảng thở.',
      hero: 'Packshot 3/4 lệch phải, copy field rõ bên trái, bóng tiếp xúc thật.',
      proof: 'Texture, routine tối giản và claim đã xác minh.',
      bestChannel: 'Meta 4:5 và landing hero.',
      risk: 'An toàn nhưng cần vật liệu và crop đủ riêng để không trở thành quảng cáo skincare trung bình.',
    },
    signature: {
      idea: 'Biến phục hồi thành một thao tác maintenance có thể nhận diện xuyên suốt campaign.',
      headline: 'Maintenance mode: ON.',
      visualGrammar: 'Đường nối safety-orange, lớp màng bán trong, typography thẳng và vật liệu thật.',
      hero: 'Sản phẩm nằm tại đúng điểm một lớp màng được nối lại, bố cục off-axis.',
      proof: 'Cơ chế sản phẩm đóng vai trò đường nối thay vì hiệu ứng trang trí.',
      bestChannel: 'TikTok, Reels và campaign page.',
      risk: 'Ngôn ngữ công nghiệp phải được tiết chế để vẫn phù hợp ngành beauty.',
    },
    departure: {
      idea: 'Phản biện cuộc đua glow và chuyển ưu tiên sang trạng thái ổn định.',
      headline: 'Không cần glow. Cần ổn.',
      visualGrammar: 'Typography chiếm khung, crop sản phẩm xâm nhập từ cạnh, ánh sáng cạnh cứng vừa phải.',
      hero: 'Headline lớn phía trên, chai đi vào từ góc dưới, không pedestal.',
      proof: 'Khối “làm gì / không hứa gì” tăng độ tin cậy.',
      bestChannel: 'TikTok awareness và social tests.',
      risk: 'Có thể quá trực diện với nhóm yêu thích hình ảnh beauty mềm mại.',
    },
  },
  fashion: {
    tension: 'Người mua nhìn thấy phong cách nhưng chưa cảm được chất liệu và cách món đồ sống trên cơ thể.',
    desiredBelief: 'Thiết kế đáng nhớ vì cấu trúc, chuyển động và cách mặc, không vì logo lớn.',
    mechanism: 'Dùng silhouette, detail macro và chuyển động vải làm bằng chứng.',
    proof: 'Fit, đường may, vật liệu, styling range và provenance.',
    antiReflex: 'Luxury haze, marble, model clone và pose catalog cứng.',
    clear: {
      idea: 'Cho sản phẩm đọc rõ từ silhouette đến chi tiết.',
      headline: 'Built to move. Cut to stay.',
      visualGrammar: 'Full-body, detail macro, ánh sáng thật và nhịp crop rõ.',
      hero: 'Một look chính chiếm khung, detail strip chạy dọc.',
      proof: 'Fit và construction.',
      bestChannel: 'Instagram 4:5 và web.',
      risk: 'Cần casting và styling tốt để không giống lookbook phổ thông.',
    },
    signature: {
      idea: 'Biến đường cắt của trang phục thành grid campaign.',
      headline: 'The cut writes the frame.',
      visualGrammar: 'Grid lệch, seam line, crop theo đường may và chuyển động vải.',
      hero: 'Một đường seam chia khung và điều khiển copy.',
      proof: 'Macro vật liệu gắn trực tiếp với silhouette.',
      bestChannel: 'Campaign web và carousel.',
      risk: 'Grid phải phục vụ sản phẩm, không trở thành đồ họa tự thân.',
    },
    departure: {
      idea: 'Bỏ pose hoàn chỉnh; chỉ cho thấy khoảnh khắc đang mặc, chỉnh và di chuyển.',
      headline: 'Not posed. In progress.',
      visualGrammar: 'Backstage crop, motion blur nhẹ, contact và fabric tension.',
      hero: 'Cảnh fitting hoặc venue arrival, không nhìn thẳng camera.',
      proof: 'Cách món đồ phản ứng trong tình huống thật.',
      bestChannel: 'TikTok và Stories.',
      risk: 'Raw vẫn phải giữ chất lượng sản phẩm và hierarchy.',
    },
  },
  'food-cpg': {
    tension: 'Bao bì được nhìn thấy nhưng cảm giác ăn và dịp sử dụng chưa đủ thật.',
    desiredBelief: 'Sản phẩm có texture, occasion và pack recognition đáng tin.',
    mechanism: 'Đặt packshot vào đúng khoảnh khắc mở, chạm, rót hoặc ăn.',
    proof: 'Texture, preparation, ingredient và packaging fidelity.',
    antiReflex: 'Nguyên liệu bay, splash bất khả thi, hơi nước giả và mặt bàn quá sạch.',
    clear: { idea: 'Pack rõ, texture gần, occasion cụ thể.', headline: 'Open the moment.', visualGrammar: 'Packshot + macro + bàn thật.', hero: 'Gói sản phẩm cạnh một serving thật, không floating.', proof: 'Texture và scale.', bestChannel: 'Meta và ecommerce.', risk: 'Cần food styling thật để không thành catalog.' },
    signature: { idea: 'Biến âm thanh và thao tác mở pack thành nhịp campaign.', headline: 'Crack. Pour. Gone.', visualGrammar: 'Sequence khung, crumbs thật, crop cận.', hero: 'Khoảnh khắc bao bì vừa mở chiếm khung.', proof: 'Tactile action.', bestChannel: 'TikTok.', risk: 'Không được hy sinh label recognition.' },
    departure: { idea: 'Không chụp “perfect serving”; chụp dấu vết sau khi dùng.', headline: 'Evidence it was good.', visualGrammar: 'Wrinkle pack, crumbs, dấu tay, ánh sáng cuối bữa.', hero: 'Aftermath có chủ đích.', proof: 'Usage truth.', bestChannel: 'Social awareness.', risk: 'Phải sạch và ngon, không bẩn hoặc phản cảm.' },
  },
  'saas-b2b': {
    tension: 'Người mua thấy nhiều feature nhưng không thấy quyết định hoặc artifact nào thay đổi.',
    desiredBelief: 'Giá trị nằm trong workflow và bằng chứng tạo ra, không trong dashboard trang trí.',
    mechanism: 'Cho thấy input, decision, output và audit trail.',
    proof: 'Artifact, time saved, risk reduced, integration và operator context.',
    antiReflex: 'Purple glow, floating nodes, fake dashboard và handshake.',
    clear: { idea: 'Một workflow, một output, một kết quả.', headline: 'From request to proof.', visualGrammar: 'Process rail và artifact thật.', hero: 'Command input nối trực tiếp tới output.', proof: 'Before/after workflow.', bestChannel: 'LinkedIn và web.', risk: 'Cần screenshot hoặc artifact đọc được.' },
    signature: { idea: 'Biến audit trail thành đường cấu trúc xuyên campaign.', headline: 'Every decision leaves proof.', visualGrammar: 'Ruled ledger, status line và document layers.', hero: 'Artifact stack với timeline bên cạnh.', proof: 'Traceability.', bestChannel: 'Web và sales enablement.', risk: 'Đừng biến thành fake telemetry.' },
    departure: { idea: 'Không show dashboard; show một quyết định hoàn tất.', headline: 'No dashboard. The decision.', visualGrammar: 'Một artifact lớn, annotation ngắn, nhiều khoảng trống.', hero: 'Output chiếm khung thay vì UI chrome.', proof: 'Result clarity.', bestChannel: 'LinkedIn single image.', risk: 'Cần giải thích đủ để người lạ hiểu.' },
  },
  ecommerce: {
    tension: 'Khách thấy sản phẩm nhưng vẫn thiếu scale, use case và lý do tin.',
    desiredBelief: 'Mỗi ảnh trả lời một câu hỏi mua hàng cụ thể.',
    mechanism: 'Dùng bộ ảnh có nhiệm vụ: hero, scale, macro, use, comparison, bundle.',
    proof: 'Fidelity, scale, material, use and return confidence.',
    antiReflex: 'Một ảnh crop mọi nơi, fake review và scarcity giả.',
    clear: { idea: 'Mỗi frame giải quyết một objection.', headline: 'See exactly what arrives.', visualGrammar: 'Packshot rõ, scale-in-hand, macro.', hero: 'Product 3/4 với thông tin sạch.', proof: 'Range và material.', bestChannel: 'PDP và Meta.', risk: 'Cần packshot chính xác.' },
    signature: { idea: 'Biến hành trình mở hộp thành hệ thống proof.', headline: 'From box to use.', visualGrammar: 'Sequence rail và cutaway.', hero: 'Bundle mở theo lớp.', proof: 'Included parts.', bestChannel: 'Carousel và web.', risk: 'Không over-package câu chuyện.' },
    departure: { idea: 'Đặt sản phẩm trong khoảnh khắc sử dụng không hoàn hảo nhưng thật.', headline: 'Already in use.', visualGrammar: 'Crop intrusion và context thật.', hero: 'Product giữa thao tác.', proof: 'Use truth.', bestChannel: 'TikTok.', risk: 'Giữ product recognition.' },
  },
  hospitality: {
    tension: 'Hình đẹp nhưng nơi chốn chưa có ký ức, nhịp di chuyển hoặc chi tiết địa phương.',
    desiredBelief: 'Trải nghiệm đáng nhớ vì cách ánh sáng, dịch vụ và không gian gặp nhau.',
    mechanism: 'Kể chuỗi arrival, room, service, local detail, departure.',
    proof: 'Place, service moment, spatial flow and local detail.',
    antiReflex: 'Infinity pool generic, beige luxury và lobby trống.',
    clear: { idea: 'Một ảnh quyết định cho mỗi lời hứa.', headline: 'Arrive somewhere specific.', visualGrammar: 'Full-bleed place photography.', hero: 'Arrival scene có người và scale.', proof: 'Spatial truth.', bestChannel: 'Web.', risk: 'Cần ảnh địa điểm thật.' },
    signature: { idea: 'Dùng đường đi của khách làm narrative.', headline: 'Follow the light in.', visualGrammar: 'Route line, chapter image, local material.', hero: 'Sequence từ cửa vào không gian.', proof: 'Journey.', bestChannel: 'Campaign page.', risk: 'Motion không được lấn trải nghiệm.' },
    departure: { idea: 'Không show room perfect; show khoảnh khắc service chuẩn bị.', headline: 'Before you arrive.', visualGrammar: 'Back-of-house crop, hands, material.', hero: 'Nhân viên hoàn thiện chi tiết.', proof: 'Service craft.', bestChannel: 'Social.', risk: 'Cần consent và authenticity.' },
  },
  wellness: {
    tension: 'Lời hứa bình yên thường mơ hồ và thiếu phương pháp.',
    desiredBelief: 'Sự thay đổi đến từ routine và support cụ thể.',
    mechanism: 'Cho thấy method, effort, recovery và progress.',
    proof: 'Routine adherence, coaching, equipment and supported outcomes.',
    antiReflex: 'Beige serenity, lá xanh, sunlight stripe và cơ thể bất khả thi.',
    clear: { idea: 'Method first, mood second.', headline: 'A routine you can repeat.', visualGrammar: 'Real session and annotated steps.', hero: 'Action rõ trong môi trường thật.', proof: 'Method.', bestChannel: 'Meta và web.', risk: 'Không overpromise outcome.' },
    signature: { idea: 'Biến nhịp thở hoặc interval thành cấu trúc campaign.', headline: 'Built around your real rhythm.', visualGrammar: 'Pace marks and recovery frames.', hero: 'Timeline gắn với người thật.', proof: 'Consistency.', bestChannel: 'App/web.', risk: 'Không pseudo-scientific.' },
    departure: { idea: 'Show rest as part of progress.', headline: 'Recovery is the work.', visualGrammar: 'Quiet post-effort imagery.', hero: 'Khoảnh khắc hồi phục thay vì peak performance.', proof: 'Recovery protocol.', bestChannel: 'Social.', risk: 'Cần rõ sản phẩm role.' },
  },
  'local-service': {
    tension: 'Khách thấy lời hứa chung nhưng chưa thấy ai làm, làm thế nào và ở đâu.',
    desiredBelief: 'Độ tin cậy đến từ quy trình, công cụ và bằng chứng địa phương.',
    mechanism: 'Show real staff, site, steps and finished work.',
    proof: 'Process transparency, local knowledge and case evidence.',
    antiReflex: 'Stock team, handshake, fake badge và skyline trang trí.',
    clear: { idea: 'Show the work before the claim.', headline: 'See how the job gets done.', visualGrammar: 'Process photo and proof ledger.', hero: 'Staff and real site.', proof: 'Case detail.', bestChannel: 'Google và web.', risk: 'Cần tài sản thật.' },
    signature: { idea: 'Biến checklist nghề nghiệp thành campaign grammar.', headline: 'Nothing hidden in the process.', visualGrammar: 'Marked steps and tool closeups.', hero: 'Checklist chạy cạnh action.', proof: 'Transparency.', bestChannel: 'Landing page.', risk: 'Đừng biến thành infographic khô.' },
    departure: { idea: 'Lead with the problem site, not smiling staff.', headline: 'Start with what is actually wrong.', visualGrammar: 'Before condition and annotation.', hero: 'Problem detail lớn.', proof: 'Diagnosis.', bestChannel: 'Search landing.', risk: 'Không fearmongering.' },
  },
  'creator-education': {
    tension: 'Người học thấy lời hứa nhưng không thấy phương pháp hoặc artifact sau khóa học.',
    desiredBelief: 'Giá trị nằm trong cách suy nghĩ và output có thể kiểm tra.',
    mechanism: 'Show notes, critique, iteration and learner work.',
    proof: 'Curriculum, method, artifact quality and learner output.',
    antiReflex: 'Laptop coffee stock, fake income, quote card và community screenshot rỗng.',
    clear: { idea: 'Show what the learner makes.', headline: 'Leave with the work.', visualGrammar: 'Artifact-led page.', hero: 'Output thật chiếm khung.', proof: 'Curriculum to output.', bestChannel: 'Web và LinkedIn.', risk: 'Cần artifact thật.' },
    signature: { idea: 'Biến critique marks thành visual language.', headline: 'Learn in the margin.', visualGrammar: 'Annotations, revisions and before/after.', hero: 'Draft được đánh dấu.', proof: 'Iteration.', bestChannel: 'Carousel.', risk: 'Giữ readability.' },
    departure: { idea: 'Không show success story; show a useful mistake.', headline: 'The mistake worth keeping.', visualGrammar: 'Failed draft and correction.', hero: 'One error, one lesson.', proof: 'Teaching method.', bestChannel: 'Social.', risk: 'Không làm giảm perceived quality.' },
  },
  other: {
    tension: 'Khách hàng thấy nhiều thông tin nhưng chưa thấy một quyết định đáng nhớ.',
    desiredBelief: 'Sản phẩm có một cơ chế rõ và một lý do cụ thể để chọn.',
    mechanism: 'Biến product mechanism thành visual grammar thay vì trang trí.',
    proof: 'Demonstration, process, comparison or supported evidence.',
    antiReflex: 'Generic trend aesthetics and interchangeable campaign templates.',
    clear: { idea: 'Product and proof first.', headline: 'Make the value visible.', visualGrammar: 'Strong hierarchy and one proof device.', hero: 'Subject plus evidence.', proof: 'Mechanism.', bestChannel: 'Web and paid social.', risk: 'Needs a sharper product truth.' },
    signature: { idea: 'Give the mechanism one ownable visual rule.', headline: 'The system behind the result.', visualGrammar: 'Recurring structural motif.', hero: 'Mechanism as composition.', proof: 'Repeatable behavior.', bestChannel: 'Campaign system.', risk: 'Motif must stay meaningful.' },
    departure: { idea: 'Break one category convention while preserving clarity.', headline: 'Do the useful thing differently.', visualGrammar: 'One controlled rule break.', hero: 'Unexpected crop or proof order.', proof: 'Contrast.', bestChannel: 'Awareness.', risk: 'State the test boundary.' },
  },
}

const channelAssets: Record<string, Array<[string, string, string]>> = {
  meta: [
    ['Feed hero', '4:5', 'consideration'],
    ['Story / Reel', '9:16', 'awareness'],
    ['Proof carousel', '1:1', 'retargeting'],
  ],
  tiktok: [
    ['Native hook', '9:16', 'awareness'],
    ['Proof cutdown', '9:16', 'consideration'],
  ],
  google: [
    ['Modular square', '1:1', 'consideration'],
    ['Landscape asset', '1.91:1', 'consideration'],
  ],
  linkedin: [
    ['Single image', '1:1', 'awareness'],
    ['Document carousel', '1:1', 'consideration'],
  ],
  pinterest: [
    ['Discovery pin', '2:3', 'awareness'],
    ['Idea pin', '9:16', 'consideration'],
  ],
  web: [
    ['Desktop hero', 'wide', 'consideration'],
    ['Mobile hero', '9:16', 'consideration'],
    ['Inline proof', '4:3', 'conversion'],
  ],
}

export const industryLabels: Record<IndustryId, string> = {
  beauty: 'Beauty / K-beauty',
  fashion: 'Fashion',
  'food-cpg': 'Food / CPG',
  'saas-b2b': 'SaaS / B2B',
  ecommerce: 'Ecommerce',
  hospitality: 'Hospitality',
  wellness: 'Wellness',
  'local-service': 'Local service',
  'creator-education': 'Creator / Education',
  other: 'Other',
}

export const providerLabels: Record<ProviderId, string> = {
  openai: 'OpenAI Images',
  midjourney: 'Midjourney',
  flux: 'Flux',
  ideogram: 'Ideogram',
  firefly: 'Adobe Firefly',
}

function lane(profile: IndustryProfile, id: LaneId): CreativeLane {
  const names = { clear: 'CLEAR', signature: 'SIGNATURE', departure: 'DEPARTURE' }
  return { id, name: names[id], ...profile[id] }
}

function createAssets(form: StudioForm, selected: LaneId): AssetRow[] {
  let index = 1
  return form.channels.flatMap((channel) =>
    (channelAssets[channel] ?? []).map(([deliverable, ratio, stage]) => ({
      id: `ASSET-${String(index++).padStart(3, '0')}`,
      lane: selected,
      channel,
      deliverable,
      ratio,
      stage,
      hypothesis:
        selected === 'clear'
          ? 'Clarity and product proof improve qualified action.'
          : selected === 'signature'
            ? 'An ownable mechanism-led grammar improves memory without losing clarity.'
            : 'A controlled category break increases stopping power without reducing trust.',
      status: 'planned',
    })),
  )
}

function buildMasterPrompt(form: StudioForm, selectedLane: CreativeLane): string {
  const humanOpening =
    form.subjectMode !== 'product' && form.kpopDefault
      ? `${RAW_HUMAN_OPENING}\n\nAdult fictional subject, Korean K-pop-inspired makeup, natural visible skin texture, plausible slender healthy idol-like silhouette, relaxed posture, realistic hands, hair and fabric.\n\n`
      : ''
  const subject =
    form.subjectMode === 'product'
      ? `${form.product}. Treat exact packaging as concept art unless a verified packshot is supplied.`
      : form.subjectMode === 'human'
        ? `One fictional adult interacting naturally with ${form.product}; candid behavior, no posed influencer smile.`
        : `A fictional adult using ${form.product} in a real moment; product remains recognizable and physically plausible.`

  return `${humanOpening}JOB
Create a ${form.ratio} marketing asset for ${form.objective}. The single idea is: ${selectedLane.idea}

REFERENCES AND LOCKS
Confirmed product truth: ${form.productTruth || 'Not supplied'}. Brand direction: ${form.brandNotes || 'Not supplied'}. Reference notes: ${form.referenceNotes || 'None supplied'}. Preserve any supplied product, identity, logo, label, color, material and claim locks exactly.

SUBJECT AND ACTION
${subject}

SCENE AND ART DIRECTION
${selectedLane.visualGrammar} ${selectedLane.hero}

COMPOSITION
Target ratio ${form.ratio}. Build an intentional typography-safe field and recompose for each channel instead of blind cropping. The first visual priority is ${form.product}.

CAMERA AND LIGHT
Use physically described camera distance, real light direction, controlled fill, believable contact shadows and coherent reflections. Avoid the phrase cinematic lighting unless the light behavior is specified.

REALISM AND MATERIALS
Preserve natural material response, scale, texture, anatomy and environmental contact. Keep the asset usable at full size and thumbnail size.

COPY SPACE
Headline to add in layout: "${selectedLane.headline}". Do not render legal, packaging or microcopy inside the generated image unless exact text is explicitly supplied.

DO NOT
${[
    profileFor(form).antiReflex,
    form.antiReferences || 'generic AI styling',
    'fake readable text, invented claims, watermark, product drift, anatomy errors, floating subjects or impossible physics',
  ]
    .map(cleanNegativeConstraint)
    .join('; ')}.`
}

function profileFor(form: StudioForm): IndustryProfile {
  return profiles[form.industry] ?? profiles.other
}

function cleanNegativeConstraint(value: string): string {
  return value
    .trim()
    .replace(/^(?:no|avoid|không)\s+/i, '')
    .replace(/[.!;\s]+$/g, '')
}

function compileProvider(prompt: string, provider: ProviderId): string {
  if (provider === 'openai') return `PROVIDER: OPENAI IMAGES\n\n${prompt}`
  if (provider === 'midjourney') {
    return `PROVIDER: MIDJOURNEY\n\n${prompt.replace(/\n+/g, ' ')}\n\nAdd current aspect-ratio and style parameters only after checking live Midjourney syntax. Packaging text and identity-critical edits require manual verification.`
  }
  if (provider === 'flux') {
    const negative = prompt.split('DO NOT')[1]?.trim() ?? 'product drift, fake text, anatomy errors'
    return `PROVIDER: FLUX\n\nPOSITIVE PROMPT\n${prompt.split('DO NOT')[0].replace(/\n+/g, ' ')}\n\nNEGATIVE PROMPT\n${negative}\n\nRecord the exact Flux model and host because controls vary.`
  }
  if (provider === 'ideogram') {
    return `PROVIDER: IDEOGRAM\n\n${prompt}\n\nTEXT CHECK\nPreserve quoted spelling, hierarchy, casing and placement. Inspect every character before publishing.`
  }
  return `PROVIDER: ADOBE FIREFLY\n\n${prompt}\n\nFINISHING\nSeparate style and composition references. Use masks for local edits and finish exact typography in Adobe design tools.`
}

function buildBrandDna(form: StudioForm, profile: IndustryProfile): string {
  return `# Brand DNA — ${form.project}

## Positioning
${form.product} for ${form.audience}. Objective: ${form.objective}.

## Product Truth
${form.productTruth || 'Unknown — must be confirmed before production.'}

## Voice
Direct, tactile, exact. Avoid generic marketing filler and unsupported certainty.

## Visual Grammar
${form.brandNotes || 'Mechanism-led composition, real materials and deliberate crops.'}

## Human Direction
Generated people default to fictional adults. ${form.kpopDefault ? 'When no direction conflicts: RAW iPhone quality, Korean K-pop-inspired makeup, realistic skin and plausible slender healthy anatomy.' : 'No default beauty styling enabled.'}

## Proof Rules
${form.proof || profile.proof}. Only supported evidence may become public copy.

## Anti-references
${profile.antiReflex}. ${form.antiReferences}

## Production
Preferred provider: ${providerLabels[form.provider]}. Channels: ${form.channels.join(', ')}.`
}

function buildPreflight(form: StudioForm) {
  const provisional = /\b(?:pending|unknown|unverified|tbc)\b|chưa|chờ|không xác nhận/i
  const items = []
  let score = 30

  if (!form.productTruth.trim()) {
    score -= 18
    items.push({ label: 'Product truth', detail: 'Thiếu product truth và identity locks.', status: 'blocker' as const })
  } else if (provisional.test(form.productTruth)) {
    score += 10
    items.push({ label: 'Product truth', detail: 'Có direction nhưng packshot hoặc geometry vẫn cần xác nhận.', status: 'warning' as const })
  } else {
    score += 20
    items.push({ label: 'Product truth', detail: 'Product truth đủ rõ để khóa concept.', status: 'pass' as const })
  }

  if (!form.proof.trim()) {
    items.push({ label: 'Proof', detail: 'Chưa có nguồn proof; không được chuyển mechanism thành claim.', status: 'blocker' as const })
  } else if (provisional.test(form.proof)) {
    score += 8
    items.push({ label: 'Proof', detail: 'Proof đang provisional; giữ wording ở mức mechanism.', status: 'warning' as const })
  } else {
    score += 20
    items.push({ label: 'Proof', detail: 'Proof đã có để kiểm tra claim trước production.', status: 'pass' as const })
  }

  if (form.brandNotes.trim() && form.antiReferences.trim()) {
    score += 15
    items.push({ label: 'Distinctiveness', detail: 'Brand cues và anti-references đã khóa category reflex.', status: 'pass' as const })
  } else {
    score += 5
    items.push({ label: 'Distinctiveness', detail: 'Bổ sung brand cues và anti-references để tránh output generic.', status: 'warning' as const })
  }

  if (!form.offer.trim() || provisional.test(form.offer)) {
    score += 2
    items.push({ label: 'Offer', detail: 'Offer chưa khóa; không đưa urgency hoặc ưu đãi vào public copy.', status: 'warning' as const })
  } else {
    score += 5
    items.push({ label: 'Offer', detail: 'Offer đủ rõ để nối campaign với CTA.', status: 'pass' as const })
  }

  score += Math.min(form.channels.length, 3) * 3 + 1
  items.push({
    label: 'Channel system',
    detail: `${form.channels.length} channel đã chọn; mỗi channel có deliverable và crop riêng.`,
    status: form.channels.length >= 2 ? ('pass' as const) : ('warning' as const),
  })

  const boundedScore = Math.max(0, Math.min(100, score))
  const hasBlocker = items.some((item) => item.status === 'blocker')
  const hasWarning = items.some((item) => item.status === 'warning')

  return {
    score: boundedScore,
    verdict: hasBlocker ? 'NOT READY' : hasWarning ? 'CONCEPT READY' : 'BRIEF LOCKED',
    items,
  }
}

export function generateCampaign(form: StudioForm): GeneratedCampaign {
  const profile = profileFor(form)
  const lanes = [lane(profile, 'clear'), lane(profile, 'signature'), lane(profile, 'departure')]
  const recommendedLane: LaneId = form.lane === 'auto' ? 'signature' : form.lane
  const selectedLane = lanes.find((item) => item.id === recommendedLane) ?? lanes[1]
  const assets = createAssets(form, recommendedLane)
  const masterPrompt = buildMasterPrompt(form, selectedLane)

  return {
    generatedAt: new Date().toISOString(),
    truth: {
      confirmed: [form.product, form.productTruth, form.audience, form.market].filter(Boolean),
      inferred: [
        form.lane === 'auto' ? 'Signature lane is recommended as the first production route.' : `User selected ${recommendedLane} lane.`,
        `Primary action is inferred from objective: ${form.objective}.`,
      ],
      unknown: [
        !form.proof ? 'Verified proof and claim sources.' : '',
        form.productTruth.toLowerCase().includes('chưa') ? 'Official packshot and exact packaging geometry.' : '',
        !form.offer ? 'Offer, price and launch terms.' : '',
      ].filter(Boolean),
    },
    campaign: {
      tension: profile.tension,
      desiredBelief: profile.desiredBelief,
      statement: selectedLane.headline,
      mechanism: profile.mechanism,
      proof: form.proof || profile.proof,
      cta: form.offer ? `Khám phá ${form.product}` : `Xem cách ${form.product} hoạt động`,
      recommendedLane,
    },
    lanes,
    assets,
    masterPrompt,
    compiledPrompt: compileProvider(masterPrompt, form.provider),
    website: [
      `Hero — ${selectedLane.headline} + sản phẩm + một hành động rõ.`,
      `Proof first — ${form.proof || 'chỉ dùng claim hoặc dữ liệu đã xác minh'}.`,
      `Tension — ${profile.tension}`,
      `Mechanism — ${profile.mechanism}`,
      `Demonstration — ${selectedLane.proof}`,
      'Use context — cho thấy sản phẩm trong khoảnh khắc thật, không dùng stock generic.',
      `Offer — ${form.offer || 'để trống cho tới khi được xác nhận'}.`,
      'Final action — lặp lại lời hứa, không lặp lại toàn bộ hero.',
    ],
    qa: [
      'Product, logo, label, material and identity locks remain exact.',
      'No invented claims, reviews, statistics, certifications or packaging text.',
      'Anatomy, hands, light, reflections, contact shadows, scale and perspective are plausible.',
      `Category reflex rejected: ${profile.antiReflex}`,
      'Headline, face and product remain safe in every required crop.',
      'Ad promise and landing-page first viewport agree.',
      'Rights, consent, source lineage and provider caveats are recorded.',
      'Rendered output is inspected before being called production-ready.',
    ],
    preflight: buildPreflight(form),
    brandDna: buildBrandDna(form, profile),
  }
}

export function campaignToMarkdown(form: StudioForm, result: GeneratedCampaign): string {
  const lanes = result.lanes
    .map(
      (item) =>
        `### ${item.name}\n\n${item.headline}\n\n- Idea: ${item.idea}\n- Visual grammar: ${item.visualGrammar}\n- Hero: ${item.hero}\n- Proof: ${item.proof}\n- Best channel: ${item.bestChannel}\n- Risk: ${item.risk}`,
    )
    .join('\n\n')
  const assets = result.assets
    .map((item) => `| ${item.id} | ${item.channel} | ${item.deliverable} | ${item.ratio} | ${item.stage} |`)
    .join('\n')

  return `# ${form.project}

## Truth

- Confirmed: ${result.truth.confirmed.join('; ') || 'None'}
- Inferred: ${result.truth.inferred.join('; ') || 'None'}
- Unknown: ${result.truth.unknown.join('; ') || 'None'}

## Campaign

- Tension: ${result.campaign.tension}
- Desired belief: ${result.campaign.desiredBelief}
- Statement: ${result.campaign.statement}
- Mechanism: ${result.campaign.mechanism}
- Proof: ${result.campaign.proof}
- CTA: ${result.campaign.cta}

## Lanes

${lanes}

## Asset Manifest

| ID | Channel | Deliverable | Ratio | Stage |
|---|---|---|---|---|
${assets}

## Provider Prompt

\`\`\`text
${result.compiledPrompt}
\`\`\`

## Website

${result.website.map((item) => `- ${item}`).join('\n')}

## QA

Pre-flight: ${result.preflight.score}/100 — ${result.preflight.verdict}

${result.preflight.items.map((item) => `- [${item.status.toUpperCase()}] ${item.label}: ${item.detail}`).join('\n')}

${result.qa.map((item) => `- ${item}`).join('\n')}
`
}

export function campaignToJsonPayload(form: StudioForm, result: GeneratedCampaign) {
  return {
    schema_version: '1.0',
    generated_at: result.generatedAt,
    project: form.project,
    provider: form.provider,
    truth: result.truth,
    campaign: {
      tension: result.campaign.tension,
      desired_belief: result.campaign.desiredBelief,
      statement: result.campaign.statement,
      mechanism: result.campaign.mechanism,
      proof: result.campaign.proof,
      cta: result.campaign.cta,
      recommended_lane: result.campaign.recommendedLane,
    },
    lanes: result.lanes.map((item) => ({
      id: item.id,
      name: item.name,
      idea: item.idea,
      headline: item.headline,
      visual_grammar: item.visualGrammar,
      hero: item.hero,
      proof: item.proof,
      best_channel: item.bestChannel,
      risk: item.risk,
    })),
    assets: result.assets,
    prompt: result.compiledPrompt,
    website: result.website,
    preflight: result.preflight,
    qa: result.qa,
    brand_dna: result.brandDna,
  }
}

export function manifestToCsv(rows: AssetRow[]): string {
  const header = ['asset_id', 'lane', 'channel', 'deliverable', 'ratio', 'stage', 'hypothesis', 'status']
  const escape = (value: string) => `"${value.replaceAll('"', '""')}"`
  return [
    header.join(','),
    ...rows.map((row) =>
      [row.id, row.lane, row.channel, row.deliverable, row.ratio, row.stage, row.hypothesis, row.status]
        .map((item) => escape(String(item)))
        .join(','),
    ),
  ].join('\n')
}
