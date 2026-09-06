const STYLES = {
  HIGH: 'text-risk-high bg-risk-highSoft border-risk-high/30',
  MEDIUM: 'text-risk-medium bg-risk-mediumSoft border-risk-medium/30',
  LOW: 'text-risk-low bg-risk-lowSoft border-risk-low/30',
}

const DOT = {
  HIGH: 'bg-risk-high',
  MEDIUM: 'bg-risk-medium',
  LOW: 'bg-risk-low',
}

export default function RiskBadge({ level, size = 'md' }) {
  const cls = STYLES[level] || 'text-muted bg-ink-700 border-line'
  const dot = DOT[level] || 'bg-faint'
  const pad = size === 'sm' ? 'px-2 py-0.5 text-[11px]' : 'px-2.5 py-1 text-[12px]'
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full border font-medium ${pad} ${cls}`}>
      <span className={`h-1.5 w-1.5 rounded-full ${dot}`} />
      {level}
    </span>
  )
}
