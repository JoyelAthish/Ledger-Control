import { AlertCircle, Inbox } from 'lucide-react'

export default function EmptyState({ title, description, variant = 'empty' }) {
  const Icon = variant === 'error' ? AlertCircle : Inbox
  return (
    <div className="flex h-64 flex-col items-center justify-center gap-2 rounded-md2 border border-dashed border-line px-6 text-center">
      <Icon size={22} className={variant === 'error' ? 'text-risk-high' : 'text-faint'} />
      <p className="text-[13.5px] font-medium text-paper">{title}</p>
      {description && <p className="max-w-sm text-[12.5px] text-muted">{description}</p>}
    </div>
  )
}
