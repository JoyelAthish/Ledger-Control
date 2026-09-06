export default function LoadingState({ label = 'Loading…' }) {
  return (
    <div className="flex h-64 flex-col items-center justify-center gap-3 text-muted">
      <div className="h-5 w-5 animate-spin rounded-full border-2 border-line border-t-accent" />
      <p className="text-[13px]">{label}</p>
    </div>
  )
}
