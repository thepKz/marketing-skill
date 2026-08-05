import { readFile, readdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const docsDir = path.dirname(fileURLToPath(import.meta.url));
const generatedDir = path.join(docsDir, 'assets', 'generated');
const catalogPath = path.join(docsDir, '..', 'research_assets', 'instagram_style_reference_2026-07-31', 'catalog.csv');
const extensions = new Set(['.png', '.jpg', '.jpeg', '.webp', '.gif', '.svg']);

const titleOverrides = {
  'minthep-serum-packshot': 'Serum packshot',
  'minthep-beauty-campaign': 'Beauty campaign',
  'minthep-serum-key-visual': 'Amber key visual',
  'minthep-serum-material-study-v2': 'Serum material study',
  'minthep-serum-shadow-study-v2': 'Serum shadow study',
  'minthep-serum-lab-detail-v2': 'Serum PDP detail',
  'minthep-serum-ritual-v2': 'Serum ritual campaign',
  'minthep-serum-commerce-pair-v3': 'Serum commerce pair',
  'minthep-serum-carry-ritual-v3': 'Serum carry ritual',
  'minthep-serum-formula-macro-v3': 'Serum formula macro',
  'minthep-serum-window-shelf-v3': 'Serum window banner',
  'minthep-serum-campaign-wide-v4': 'Serum campaign master',
  'minthep-serum-retail-counter-v4': 'Serum retail counter',
  'minthep-serum-editorial-print-v4': 'Serum editorial print',
  'minthep-serum-unboxing-v4': 'Serum unboxing',
  'minthep-coffee-roastery-wide-v1': 'Coffee roastery campaign',
  'minthep-coffee-roast-date-detail-v1': 'Coffee roast-date proof',
  'minthep-coffee-local-delivery-v1': 'Coffee local delivery',
  'minthep-coffee-sample-tasting-v1': 'Coffee sample tasting',
  'minthep-fashion-look': 'Fashion look',
  'menu-atlas-street-grill': 'Street grill menu system',
  'menu-atlas-cafe-bakery': 'Cafe and bakery menu system',
  'menu-atlas-family-table': 'Family table menu system',
  'menu-atlas-fine-dining': 'Tasting menu system',
  'menu-atlas-cocktail-bar': 'Cocktail bar menu system',
  'menu-atlas-tea-dessert': 'Tea and dessert menu system',
  'menu-atlas-food-court-board': 'Food-court menu board system',
  'menu-atlas-delivery-mobile': 'Delivery mobile menu system',
  'menu-atlas-hotel-breakfast': 'Hotel breakfast menu system',
  'minthep-poster-material-study-v2': 'Material study poster',
  'minthep-poster-magazine-v3': 'Magazine poster system',
  'minthep-poster-surface-v1': 'Poster surface canvas',
  'refsheet-dial-margin': 'Margin dial sheet',
  'refsheet-frames': 'Placement frame sheet',
  'refsheet-lighting': 'Lighting setup sheet',
  'refsheet-palettes': 'Measured palette sheet',
  'refsheet-ratios': 'Publishing ratio sheet',
  'refsheet-reference': 'Reference analysis sheet',
};

function readPngSize(buffer) {
  if (buffer.length < 24 || buffer.toString('ascii', 1, 4) !== 'PNG') return null;
  return { width: buffer.readUInt32BE(16), height: buffer.readUInt32BE(20) };
}

function readSvgSize(source) {
  const viewBox = source.match(/viewBox=["']\s*[\d.-]+\s+[\d.-]+\s+([\d.]+)\s+([\d.]+)["']/i);
  if (viewBox) return { width: Number(viewBox[1]), height: Number(viewBox[2]) };
  const width = source.match(/width=["']([\d.]+)/i);
  const height = source.match(/height=["']([\d.]+)/i);
  return width && height ? { width: Number(width[1]), height: Number(height[1]) } : null;
}

async function dimensions(filePath, extension) {
  const buffer = await readFile(filePath);
  if (extension === '.png') return readPngSize(buffer) || { width: 1, height: 1 };
  if (extension === '.svg') return readSvgSize(buffer.toString('utf8')) || { width: 1, height: 1 };
  return { width: 1, height: 1 };
}

function categoryFor(stem) {
  if (stem.startsWith('minthep-serum-packshot')) return 'product';
  if (stem.startsWith('minthep-')) return 'campaign';
  if (stem.startsWith('refsheet-')) return 'systems';
  if (stem.includes('-post-')) return 'social';
  if (/food-ref|isolated|documentary|photoreal/.test(stem)) return 'photography';
  if (/menu|broadsheet|counter|lacquer|gallery|broth-map|hue-ledger|blueprint/.test(stem)) return 'artwork';
  return 'process';
}

function statusFor(stem) {
  if (/type-v\d|ref-v\d|hue-ledger-v\d|full-proof|reference-board/.test(stem)) return 'iteration';
  if (/food-ref|refsheet/.test(stem)) return 'reference';
  return 'output';
}

function titleFor(stem) {
  if (titleOverrides[stem]) return titleOverrides[stem];
  return stem
    .replace(/^minthep-/, '')
    .split('-')
    .map((word) => word === 'ai' ? 'AI' : word === 'v1' || word === 'v2' || word === 'v3' || word === 'v4' ? word.toUpperCase() : word)
    .join(' ')
    .replace(/^./, (letter) => letter.toUpperCase());
}

function selectedRank(stem) {
  const selected = [
    'minthep-serum-campaign-wide-v4',
    'minthep-coffee-roastery-wide-v1',
  ];
  const index = selected.indexOf(stem);
  return index === -1 ? 100 : index;
}

const files = (await readdir(generatedDir)).filter((file) => {
  const extension = path.extname(file).toLowerCase();
  const stem = path.basename(file, extension);
  return extensions.has(extension) && !stem.startsWith('bun-bo-');
});
const assets = await Promise.all(files.map(async (file) => {
  const extension = path.extname(file).toLowerCase();
  const stem = path.basename(file, extension);
  const size = await dimensions(path.join(generatedDir, file), extension);
  const ratio = size.width / size.height;
  return {
    id: stem,
    src: `./assets/generated/${file}`,
    title: titleFor(stem),
    category: categoryFor(stem),
    status: statusFor(stem),
    width: size.width,
    height: size.height,
    shape: ratio > 1.35 ? 'wide' : ratio < 0.76 ? 'tall' : 'standard',
    fit: extension === '.svg' || /menu|refsheet|post|blueprint|ledger|broth-map/.test(stem) ? 'contain' : 'cover',
    selected: selectedRank(stem) < 100,
    selectedRank: selectedRank(stem),
  };
}));

const compareText = (a, b) => a < b ? -1 : a > b ? 1 : 0;
assets.sort((a, b) => a.selectedRank - b.selectedRank || compareText(a.category, b.category) || compareText(a.title, b.title));

let internalReferences = 0;
try {
  const catalog = await readFile(catalogPath, 'utf8');
  internalReferences = Math.max(0, catalog.trim().split(/\r?\n/).length - 1);
} catch {
  internalReferences = 0;
}

const source = `// Generated by build-gallery-manifest.mjs. Do not edit by hand.\nwindow.SHOWCASE_META = ${JSON.stringify({ published: assets.length, internalReferences }, null, 2)};\nwindow.SHOWCASE_ASSETS = ${JSON.stringify(assets, null, 2)};\n`;
await writeFile(path.join(docsDir, 'gallery-manifest.js'), source, 'utf8');
console.log(`Wrote ${assets.length} published assets; ${internalReferences} internal references indexed.`);
