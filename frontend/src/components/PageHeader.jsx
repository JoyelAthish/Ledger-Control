export default function PageHeader({ title, description, actions }) {
  return (
    <div className="flex items-start justify-between border-b border-line px-8 py-6">
      <div>
        <h1 className="text-[19px] font-semibold tracking-tight text-paper">{title}</h1>
        {description && <p className="mt-1 text-[13px] text-muted">{description}</p>}
      </div>
      {actions && <div className="flex items-center gap-2">{actions}</div>}
    </div>
  )
}
