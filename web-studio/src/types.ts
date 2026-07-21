export type LaneId = 'clear' | 'signature' | 'departure'
export type ProviderId = 'openai' | 'midjourney' | 'flux' | 'ideogram' | 'firefly'
export type SubjectMode = 'product' | 'human' | 'hybrid'
export type IndustryId =
  | 'beauty'
  | 'fashion'
  | 'food-cpg'
  | 'saas-b2b'
  | 'ecommerce'
  | 'hospitality'
  | 'wellness'
  | 'local-service'
  | 'creator-education'
  | 'other'

export interface StudioForm {
  project: string
  product: string
  objective: string
  audience: string
  market: string
  offer: string
  proof: string
  productTruth: string
  brandNotes: string
  antiReferences: string
  referenceNotes: string
  industry: IndustryId
  provider: ProviderId
  subjectMode: SubjectMode
  lane: LaneId | 'auto'
  channels: string[]
  ratio: string
  kpopDefault: boolean
}

export interface CreativeLane {
  id: LaneId
  name: string
  idea: string
  headline: string
  visualGrammar: string
  hero: string
  proof: string
  bestChannel: string
  risk: string
}

export interface AssetRow {
  id: string
  lane: LaneId
  channel: string
  deliverable: string
  ratio: string
  stage: string
  hypothesis: string
  status: 'planned'
}

export interface PreflightItem {
  label: string
  detail: string
  status: 'pass' | 'warning' | 'blocker'
}

export interface GeneratedCampaign {
  generatedAt: string
  truth: {
    confirmed: string[]
    inferred: string[]
    unknown: string[]
  }
  campaign: {
    tension: string
    desiredBelief: string
    statement: string
    mechanism: string
    proof: string
    cta: string
    recommendedLane: LaneId
  }
  lanes: CreativeLane[]
  assets: AssetRow[]
  masterPrompt: string
  compiledPrompt: string
  website: string[]
  qa: string[]
  preflight: {
    score: number
    verdict: string
    items: PreflightItem[]
  }
  brandDna: string
}
