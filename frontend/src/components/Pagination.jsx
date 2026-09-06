import { ChevronLeft, ChevronRight } from 'lucide-react'

export default function Pagination({ page, pageSize, total, onPageChange }) {
  const totalPages = Math.max(1, Math.ceil(total / pageSize))
  const start = total === 0 ? 0 : (page - 1) * pageSize + 1
  const end = Math.min(total, page * pageSize)

  return (
    <div className="flex items-center justify-between border-t border-line px-4 py-3">
      <p className="text-[12px] text-muted">
        {total === 0 ? 'No results' : `${start}–${end} of ${total}`}
      </p>
      <div className="flex items-center gap-1">
        <button
          onClick={() => onPageChange(page - 1)}
          disabled={page <= 1}
          className="flex h-7 w-7 items-center justify-center rounded-md2 border border-line text-muted hover:bg-ink-700 disabled:opacity-30 disabled:hover:bg-transparent"
        >
          <ChevronLeft size={14} />
        </button>
        <span className="px-2 text-[12px] text-muted">
          {page} / {totalPages}
        </span>
        <button
          onClick={() => onPageChange(page + 1)}
          disabled={page >= totalPages}
          className="flex h-7 w-7 items-center justify-center rounded-md2 border border-line text-muted hover:bg-ink-700 disabled:opacity-30 disabled:hover:bg-transparent"
        >
          <ChevronRight size={14} />
        </button>
      </div>
    </div>
  )
}
