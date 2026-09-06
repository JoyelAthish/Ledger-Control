export default function KpiCard({ label, value, sub, accentColor = '#4C7CF3', icon: Icon }) {
  return (
    <div
      className="relative flex-1 rounded-md2 border border-line bg-ink-900 p-4 shadow-panel"
      style={{ borderLeftColor: accentColor, borderLeftWidth: '3px' }}
    >
      <div className="flex items-start justify-between">
        <p className="text-[12.5px] text-muted">{label}</p>
        {Icon && <Icon size={15} className="text-faint" />}
      </div>
      <p className="mt-2 font-mono text-[26px] font-medium leading-none tabular text-paper">{value}</p>
      {sub && <p className="mt-2 text-[11.5px] text-faint">{sub}</p>}
    </div>
  )
}
