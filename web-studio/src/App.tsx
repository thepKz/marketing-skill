import { useEffect, useMemo, useState } from 'react'
import {
  campaignToMarkdown,
  campaignToJsonPayload,
  defaultForm,
  generateCampaign,
  industryLabels,
  manifestToCsv,
  providerLabels,
} from './engine'
import type { GeneratedCampaign, IndustryId, ProviderId, StudioForm, SubjectMode } from './types'
import './App.css'

type TabId = 'campaign' | 'prompt' | 'manifest' | 'qa' | 'brand'

const channels = ['meta', 'tiktok', 'google', 'linkedin', 'pinterest', 'web']
const publicAsset = (path: string) => `${import.meta.env.BASE_URL}${path.replace(/^\/+/, '')}`
const tabs: Array<[TabId, string]> = [
  ['campaign', 'Campaign'],
  ['prompt', 'Prompt'],
  ['manifest', 'Manifest'],
  ['qa', 'QA'],
  ['brand', 'Brand DNA'],
]

function downloadFile(filename: string, content: string, type: string) {
  const blob = new Blob([content], { type })
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = filename
  anchor.click()
  URL.revokeObjectURL(url)
}

function slugify(value: string) {
  return value
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '') || 'campaign'
}

function Field({
  label,
  value,
  onChange,
  placeholder,
  multiline = false,
  help,
}: {
  label: string
  value: string
  onChange: (value: string) => void
  placeholder?: string
  multiline?: boolean
  help?: string
}) {
  const id = `field-${label.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`
  return (
    <label className="field" htmlFor={id}>
      <span className="field-label">{label}</span>
      {multiline ? (
        <textarea id={id} value={value} placeholder={placeholder} onChange={(event) => onChange(event.target.value)} />
      ) : (
        <input id={id} value={value} placeholder={placeholder} onChange={(event) => onChange(event.target.value)} />
      )}
      {help && <span className="field-help">{help}</span>}
    </label>
  )
}

function Segmented<T extends string>({
  label,
  value,
  options,
  onChange,
}: {
  label: string
  value: T
  options: Array<[T, string]>
  onChange: (value: T) => void
}) {
  return (
    <fieldset className="segmented-field">
      <legend>{label}</legend>
      <div className="segmented-control">
        {options.map(([option, text]) => (
          <button
            className={value === option ? 'is-active' : ''}
            key={option}
            type="button"
            aria-pressed={value === option}
            onClick={() => onChange(option)}
          >
            {text}
          </button>
        ))}
      </div>
    </fieldset>
  )
}

function App() {
  const [form, setForm] = useState<StudioForm>(() => {
    const saved = localStorage.getItem('field-studio-form')
    return saved ? { ...defaultForm, ...JSON.parse(saved) } : defaultForm
  })
  const [result, setResult] = useState<GeneratedCampaign>(() => generateCampaign(form))
  const [activeTab, setActiveTab] = useState<TabId>('campaign')
  const [isGenerating, setIsGenerating] = useState(false)
  const [error, setError] = useState('')
  const [toast, setToast] = useState('')

  useEffect(() => {
    localStorage.setItem('field-studio-form', JSON.stringify(form))
  }, [form])

  useEffect(() => {
    if (!toast) return
    const timer = window.setTimeout(() => setToast(''), 1800)
    return () => window.clearTimeout(timer)
  }, [toast])

  const selectedLane = useMemo(
    () => result.lanes.find((lane) => lane.id === result.campaign.recommendedLane) ?? result.lanes[1],
    [result],
  )

  const update = <K extends keyof StudioForm>(key: K, value: StudioForm[K]) => {
    setForm((current) => ({ ...current, [key]: value }))
  }

  const toggleChannel = (channel: string) => {
    setForm((current) => {
      const exists = current.channels.includes(channel)
      const next = exists ? current.channels.filter((item) => item !== channel) : [...current.channels, channel]
      return { ...current, channels: next.length ? next : current.channels }
    })
  }

  const generate = () => {
    if (!form.project.trim() || !form.product.trim() || !form.objective.trim()) {
      setError('Cần tên project, sản phẩm và mục tiêu để tạo campaign.')
      return
    }
    setError('')
    setIsGenerating(true)
    window.setTimeout(() => {
      setResult(generateCampaign(form))
      setIsGenerating(false)
      setActiveTab('campaign')
      setToast('Campaign system đã được dựng lại')
    }, 520)
  }

  const copyText = async (content: string, message: string) => {
    await navigator.clipboard.writeText(content)
    setToast(message)
  }

  const projectSlug = slugify(form.project)
  const markdown = campaignToMarkdown(form, result)
  const jsonPayload = JSON.stringify(campaignToJsonPayload(form, result), null, 2)

  return (
    <div className="app-shell">
      <header className="top-rail">
        <a className="brand-mark" href="#top" aria-label="FIELD home">
          FIELD<span>/</span>01
        </a>
        <nav aria-label="Primary navigation">
          <a href="#studio">Studio</a>
          <a href="#system">System</a>
          <a href="#sources">Sources</a>
        </nav>
        <div className="system-state"><span aria-hidden="true" /> Local compiler / no API key</div>
      </header>

      <main id="top">
        <section className="hero-scene" aria-labelledby="hero-title">
          <div className="hero-copy">
            <p className="kicker">Marketing Creative Operating System</p>
            <h1 id="hero-title">Turn product truth into campaign material.</h1>
            <p className="hero-intro">
              Một brief đi vào. Campaign lanes, provider prompt, channel manifest, website sequence và QA đi ra.
              Không bịa claim. Không template AI.
            </p>
            <div className="hero-actions">
              <a className="button button-primary" href="#studio">Mở control room</a>
              <button className="button button-ghost" type="button" onClick={() => copyText('$marketing-creative-director', 'Đã copy tên skill')}>
                Copy $skill
              </button>
            </div>
          </div>

          <div className="hero-board" aria-label="Campaign workflow preview">
            <div className="board-status">
              <span>CAMPAIGN / LIVE BRIEF</span>
              <strong>{result.assets.length.toString().padStart(2, '0')} assets</strong>
            </div>
            <div className="board-grid">
              <div className="board-image board-image-main">
                <img src={publicAsset('images/product-serum.jpg')} alt="Skincare product reference on white fabric" />
                <span>REFERENCE / PRODUCT</span>
              </div>
              <div className="board-type">
                <span>RECOMMENDED LANE</span>
                <strong>{selectedLane.name}</strong>
                <p>{selectedLane.headline}</p>
              </div>
              <div className="board-image board-image-detail">
                <img src={publicAsset('images/makeup-tools.jpg')} alt="Makeup products arranged under direct light" />
                <span>MATERIAL / LIGHT</span>
              </div>
            </div>
            <svg className="process-line" viewBox="0 0 480 70" role="img" aria-label="Brief to campaign process">
              <path d="M8 34 H108 C132 34 130 10 158 10 H286 C314 10 310 57 338 57 H472" />
              <circle cx="8" cy="34" r="5" />
              <circle cx="158" cy="10" r="5" />
              <circle cx="338" cy="57" r="5" />
              <circle cx="472" cy="57" r="5" />
            </svg>
          </div>
        </section>

        <section className="studio" id="studio" aria-labelledby="studio-title">
          <aside className="brief-rail">
            <div className="section-heading">
              <span>INPUT / BRIEF</span>
              <h2 id="studio-title">Build from what is true.</h2>
            </div>

            <div className="form-section">
              <Field label="Project" value={form.project} onChange={(value) => update('project', value)} />
              <Field label="Sản phẩm" value={form.product} onChange={(value) => update('product', value)} />
              <Field label="Mục tiêu" value={form.objective} onChange={(value) => update('objective', value)} multiline />
              <Field label="Khách hàng" value={form.audience} onChange={(value) => update('audience', value)} multiline />
              <Field label="Product truth" value={form.productTruth} onChange={(value) => update('productTruth', value)} multiline help="Chỉ ghi những gì đã được xác nhận." />
            </div>

            <details open>
              <summary>Strategy and proof</summary>
              <div className="form-section detail-fields">
                <Field label="Thị trường" value={form.market} onChange={(value) => update('market', value)} />
                <Field label="Offer" value={form.offer} onChange={(value) => update('offer', value)} multiline />
                <Field label="Proof" value={form.proof} onChange={(value) => update('proof', value)} multiline />
                <Field label="Brand cues" value={form.brandNotes} onChange={(value) => update('brandNotes', value)} multiline />
                <Field label="Anti-references" value={form.antiReferences} onChange={(value) => update('antiReferences', value)} multiline />
              </div>
            </details>

            <details open>
              <summary>Production controls</summary>
              <div className="form-section detail-fields">
                <label className="field" htmlFor="industry">
                  <span className="field-label">Ngành</span>
                  <select id="industry" value={form.industry} onChange={(event) => update('industry', event.target.value as IndustryId)}>
                    {Object.entries(industryLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
                  </select>
                </label>
                <label className="field" htmlFor="provider">
                  <span className="field-label">Provider</span>
                  <select id="provider" value={form.provider} onChange={(event) => update('provider', event.target.value as ProviderId)}>
                    {Object.entries(providerLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
                  </select>
                </label>
                <Segmented<SubjectMode>
                  label="Subject"
                  value={form.subjectMode}
                  options={[["product", "Product"], ["human", "Human"], ["hybrid", "Hybrid"]]}
                  onChange={(value) => update('subjectMode', value)}
                />
                <Segmented<StudioForm['lane']>
                  label="Lane"
                  value={form.lane}
                  options={[["auto", "Auto"], ["clear", "Clear"], ["signature", "Signature"], ["departure", "Departure"]]}
                  onChange={(value) => update('lane', value)}
                />
                <label className="field" htmlFor="ratio">
                  <span className="field-label">Master ratio</span>
                  <select id="ratio" value={form.ratio} onChange={(event) => update('ratio', event.target.value)}>
                    {['9:16', '4:5', '1:1', '16:9', 'wide web'].map((ratio) => <option key={ratio}>{ratio}</option>)}
                  </select>
                </label>
                <fieldset className="channel-field">
                  <legend>Channels</legend>
                  <div className="channel-list">
                    {channels.map((channel) => (
                      <label key={channel}>
                        <input type="checkbox" checked={form.channels.includes(channel)} onChange={() => toggleChannel(channel)} />
                        <span>{channel}</span>
                      </label>
                    ))}
                  </div>
                </fieldset>
                <label className="switch-row">
                  <input type="checkbox" checked={form.kpopDefault} onChange={(event) => update('kpopDefault', event.target.checked)} />
                  <span><strong>K-pop human default</strong><small>RAW iPhone, adult, realistic skin and plausible slim anatomy.</small></span>
                </label>
              </div>
            </details>

            {error && <p className="form-error" role="alert">{error}</p>}
            <button className="generate-button" type="button" onClick={generate} disabled={isGenerating}>
              <span>{isGenerating ? 'Compiling system...' : 'Build campaign system'}</span>
              <span aria-hidden="true">↗</span>
            </button>
          </aside>

          <div className="output-stage" id="system">
            <div className="output-toolbar">
              <div>
                <span>OUTPUT / {form.project}</span>
                <strong>{providerLabels[form.provider]}</strong>
              </div>
              <div className="toolbar-actions">
                <button type="button" onClick={() => copyText(markdown, 'Đã copy campaign Markdown')}>Copy</button>
                <button type="button" onClick={() => downloadFile(`${projectSlug}.md`, markdown, 'text/markdown')}>.MD</button>
                <button type="button" onClick={() => downloadFile(`${projectSlug}.json`, jsonPayload, 'application/json')}>.JSON</button>
              </div>
            </div>

            <div className="tab-list" role="tablist" aria-label="Campaign output views">
              {tabs.map(([id, label]) => (
                <button
                  key={id}
                  id={`tab-${id}`}
                  type="button"
                  role="tab"
                  aria-selected={activeTab === id}
                  aria-controls={`panel-${id}`}
                  className={activeTab === id ? 'is-active' : ''}
                  onClick={() => setActiveTab(id)}
                >
                  {label}
                </button>
              ))}
            </div>

            <div className={`output-content ${isGenerating ? 'is-loading' : ''}`} aria-live="polite" aria-busy={isGenerating}>
              {isGenerating ? (
                <div className="loading-state">
                  <span />
                  <span />
                  <span />
                  <p>Mapping truth → lanes → assets → provider prompt</p>
                </div>
              ) : (
                <>
                  {activeTab === 'campaign' && (
                    <section id="panel-campaign" role="tabpanel" aria-labelledby="tab-campaign" className="tab-panel campaign-panel">
                      <div className="campaign-hero">
                        <div className="campaign-hero-copy">
                          <span>{selectedLane.name} / RECOMMENDED</span>
                          <h3>{result.campaign.statement}</h3>
                          <p>{selectedLane.idea}</p>
                          <div className="campaign-meta">
                            <div><small>TENSION</small><strong>{result.campaign.tension}</strong></div>
                            <div><small>DESIRED BELIEF</small><strong>{result.campaign.desiredBelief}</strong></div>
                          </div>
                        </div>
                        <div className={`campaign-visual mode-${form.subjectMode}`}>
                          <img
                            src={publicAsset(form.subjectMode === 'product' ? 'images/product-serum.jpg' : 'images/human-natural.jpg')}
                            alt={form.subjectMode === 'product' ? 'Product reference preview' : 'Human reference preview'}
                          />
                          <div className="visual-label">REFERENCE / NOT GENERATED</div>
                          <div className="visual-seam" aria-hidden="true" />
                        </div>
                      </div>

                      <div className="truth-ledger">
                        <div><span>CONFIRMED</span>{result.truth.confirmed.map((item) => <p key={item}>{item}</p>)}</div>
                        <div><span>INFERRED</span>{result.truth.inferred.map((item) => <p key={item}>{item}</p>)}</div>
                        <div><span>UNKNOWN</span>{result.truth.unknown.length ? result.truth.unknown.map((item) => <p key={item}>{item}</p>) : <p>Không có unknown được ghi nhận.</p>}</div>
                      </div>

                      <div className="lane-stack">
                        {result.lanes.map((item, index) => (
                          <article key={item.id} className={`lane-card lane-${item.id} ${item.id === result.campaign.recommendedLane ? 'is-recommended' : ''}`}>
                            <div className="lane-index">0{index + 1}</div>
                            <div className="lane-body">
                              <span>{item.name}</span>
                              <h4>{item.headline}</h4>
                              <p>{item.idea}</p>
                              <dl>
                                <div><dt>Visual grammar</dt><dd>{item.visualGrammar}</dd></div>
                                <div><dt>Hero</dt><dd>{item.hero}</dd></div>
                                <div><dt>Risk</dt><dd>{item.risk}</dd></div>
                              </dl>
                            </div>
                          </article>
                        ))}
                      </div>

                      <div className="website-sequence">
                        <div className="section-heading compact"><span>ONE-PAGE WEBSITE</span><h3>Ad promise → proof → action.</h3></div>
                        <ol>{result.website.map((item) => <li key={item}>{item}</li>)}</ol>
                      </div>
                    </section>
                  )}

                  {activeTab === 'prompt' && (
                    <section id="panel-prompt" role="tabpanel" aria-labelledby="tab-prompt" className="tab-panel prompt-panel">
                      <div className="prompt-header">
                        <div><span>COMPILED FOR</span><h3>{providerLabels[form.provider]}</h3></div>
                        <button type="button" onClick={() => copyText(result.compiledPrompt, 'Đã copy provider prompt')}>Copy prompt</button>
                      </div>
                      <pre>{result.compiledPrompt}</pre>
                      <div className="prompt-note"><strong>Source of truth:</strong> master prompt được giữ provider-neutral; phần trên chỉ là execution layer.</div>
                    </section>
                  )}

                  {activeTab === 'manifest' && (
                    <section id="panel-manifest" role="tabpanel" aria-labelledby="tab-manifest" className="tab-panel manifest-panel">
                      <div className="manifest-head">
                        <div><span>PRODUCTION LINEAGE</span><h3>{result.assets.length} planned assets</h3></div>
                        <button type="button" onClick={() => downloadFile(`${projectSlug}-manifest.csv`, manifestToCsv(result.assets), 'text/csv')}>Download CSV</button>
                      </div>
                      <div className="table-wrap">
                        <table>
                          <thead><tr><th>ID</th><th>Lane</th><th>Channel</th><th>Deliverable</th><th>Ratio</th><th>Stage</th></tr></thead>
                          <tbody>{result.assets.map((asset) => <tr key={asset.id}><td>{asset.id}</td><td>{asset.lane}</td><td>{asset.channel}</td><td>{asset.deliverable}</td><td>{asset.ratio}</td><td>{asset.stage}</td></tr>)}</tbody>
                        </table>
                      </div>
                    </section>
                  )}

                  {activeTab === 'qa' && (
                    <section id="panel-qa" role="tabpanel" aria-labelledby="tab-qa" className="tab-panel qa-panel">
                      <div className="qa-score"><span>PRE-FLIGHT</span><strong>{result.preflight.score}</strong><small>{result.preflight.verdict}</small></div>
                      <div className="qa-list">
                        {result.preflight.items.map((item, index) => (
                          <div key={item.label} data-status={item.status}>
                            <span>{String(index + 1).padStart(2, '0')}</span>
                            <p><b>{item.label}</b>{item.detail}</p>
                            <strong>{item.status}</strong>
                          </div>
                        ))}
                      </div>
                      <div className="qa-checks">
                        <span>RENDER GATE / {result.qa.length} CRITICAL CHECKS</span>
                        <ol>{result.qa.map((item) => <li key={item}>{item}</li>)}</ol>
                      </div>
                      <div className="qa-warning"><strong>Không có ảnh được render trong web studio.</strong> Prompt phải được chạy qua provider và output phải được kiểm tra trước khi gọi production-ready.</div>
                    </section>
                  )}

                  {activeTab === 'brand' && (
                    <section id="panel-brand" role="tabpanel" aria-labelledby="tab-brand" className="tab-panel brand-panel">
                      <div className="prompt-header"><div><span>DURABLE CONTEXT</span><h3>BRAND.md</h3></div><button type="button" onClick={() => copyText(result.brandDna, 'Đã copy Brand DNA')}>Copy Brand DNA</button></div>
                      <pre>{result.brandDna}</pre>
                    </section>
                  )}
                </>
              )}
            </div>
          </div>
        </section>

        <section className="system-strip" aria-label="System capabilities">
          <div><strong>03</strong><span>creative lanes</span></div>
          <div><strong>05</strong><span>provider compilers</span></div>
          <div><strong>{result.assets.length.toString().padStart(2, '0')}</strong><span>channel assets</span></div>
          <div><strong>08</strong><span>critical QA checks</span></div>
        </section>
      </main>

      <footer id="sources">
        <div><strong>FIELD / 01</strong><p>Built from $marketing-creative-director V2 and $marketing-one-page-studio.</p></div>
        <div><span>Sample photography</span><a href="https://unsplash.com" target="_blank" rel="noreferrer">Unsplash references</a></div>
        <div><span>Execution</span><p>Local deterministic compiler. No campaign is published automatically.</p></div>
      </footer>

      {toast && <div className="toast" role="status">{toast}</div>}
    </div>
  )
}

export default App
