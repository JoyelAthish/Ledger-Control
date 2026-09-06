import { useEffect, useState } from 'react'
import { Search, ArrowUpDown } from 'lucide-react'
import RiskBadge from './RiskBadge.jsx'
import Pagination from './Pagination.jsx'
import LoadingState from './LoadingState.jsx'
import EmptyState from './EmptyState.jsx'
import { getExceptions } from '../api/client.js'
import { formatINR, issueLabel } from '../lib/format.js'

const RISK_LEVELS = ['HIGH', 'MEDIUM', 'LOW']
const ISSUE_TYPES = [
  'MISSING_GATEWAY_PAYOUT',
  'PAYMENT_FAILED',
  'FEE_OVERCHARGE_ANOMALY',
  'BANK_DEPOSIT_SHORTFALL',
  'ORPHAN_BANK_CREDIT',
]

const SORT_OPTIONS = [
  { value: 'priority_rank', label: 'Priority' },
  { value: 'discrepancy_amount', label: 'Discrepancy amount' },
  { value: 'order_id', label: 'Order ID' },
  { value: 'customer_name', label: 'Customer' },
]

export default function ExceptionQueue({ onRowClick, showIssueFilter = true, pageSize = 10, title, statusOverrides = {} }) {
  const [rows, setRows] = useState([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const [search, setSearch] = useState('')
  const [riskFilter, setRiskFilter] = useState([])
  const [issueFilter, setIssueFilter] = useState([])
  const [sortBy, setSortBy] = useState('priority_rank')
  const [sortDir, setSortDir] = useState('asc')

  useEffect(() => {
    setPage(1)
  }, [search, riskFilter, issueFilter, sortBy, sortDir])

  useEffect(() => {
    setLoading(true)
    setError(null)
    const params = {
      page,
      page_size: pageSize,
      sort_by: sortBy,
      sort_dir: sortDir,
    }
    if (search.trim()) params.search = search.trim()
    if (riskFilter.length) params.risk = riskFilter
    if (issueFilter.length) params.issue_type = issueFilter

    getExceptions(params)
      .then((d) => {
        setRows(d.results)
        setTotal(d.total)
      })
      .catch((e) => setError(e?.response?.data?.detail || 'Could not load exceptions.'))
      .finally(() => setLoading(false))
  }, [page, pageSize, search, riskFilter, issueFilter, sortBy, sortDir])

  const toggleRisk = (level) => {
    setRiskFilter((prev) => (prev.includes(level) ? prev.filter((l) => l !== level) : [...prev, level]))
  }

  const toggleSort = (col) => {
    if (sortBy === col) {
      setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'))
    } else {
      setSortBy(col)
      setSortDir('asc')
    }
  }

  return (
    <div className="rounded-md2 border border-line bg-ink-900 shadow-panel">
      <div className="flex flex-wrap items-center gap-2.5 border-b border-line px-4 py-3.5">
        {title && <p className="mr-auto text-[13.5px] font-medium text-paper">{title}</p>}

        <div className="flex items-center gap-1.5 rounded-md2 border border-line bg-ink-800 px-2.5 py-1.5">
          <Search size={13} className="text-faint" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search order or customer"
            className="w-44 bg-transparent text-[12.5px] text-paper placeholder:text-faint focus:outline-none"
          />
        </div>

        <div className="flex items-center gap-1">
          {RISK_LEVELS.map((level) => (
            <button
              key={level}
              onClick={() => toggleRisk(level)}
              className={`rounded-full border px-2.5 py-1 text-[11px] font-medium transition-colors ${
                riskFilter.includes(level)
                  ? 'border-accent/40 bg-accent/15 text-accent'
                  : 'border-line text-muted hover:bg-ink-700'
              }`}
            >
              {level}
            </button>
          ))}
        </div>

        {showIssueFilter && (
          <select
            multiple={false}
            value=""
            onChange={(e) => {
              const v = e.target.value
              if (!v) return
              setIssueFilter((prev) => (prev.includes(v) ? prev.filter((i) => i !== v) : [...prev, v]))
            }}
            className="rounded-md2 border border-line bg-ink-800 px-2.5 py-1.5 text-[12px] text-muted focus:outline-none"
          >
            <option value="">Filter issue type…</option>
            {ISSUE_TYPES.map((t) => (
              <option key={t} value={t}>
                {issueLabel(t)}
              </option>
            ))}
          </select>
        )}

        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          className="rounded-md2 border border-line bg-ink-800 px-2.5 py-1.5 text-[12px] text-muted focus:outline-none"
        >
          {SORT_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>
              Sort: {o.label}
            </option>
          ))}
        </select>
      </div>

      {issueFilter.length > 0 && (
        <div className="flex flex-wrap gap-1.5 border-b border-line px-4 py-2">
          {issueFilter.map((t) => (
            <button
              key={t}
              onClick={() => setIssueFilter((prev) => prev.filter((i) => i !== t))}
              className="rounded-full border border-accent/30 bg-accent/10 px-2 py-0.5 text-[11px] text-accent"
            >
              {issueLabel(t)} ×
            </button>
          ))}
        </div>
      )}

      {loading && <LoadingState label="Loading exceptions…" />}
      {error && !loading && <div className="p-4"><EmptyState variant="error" title="Couldn't load exceptions" description={error} /></div>}

      {!loading && !error && rows.length === 0 && (
        <div className="p-4">
          <EmptyState title="No exceptions match" description="Try adjusting your filters or search term." />
        </div>
      )}

      {!loading && !error && rows.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="text-[11px] text-faint">
                <th className="px-4 py-2.5 font-medium">
                  <button onClick={() => toggleSort('order_id')} className="inline-flex items-center gap-1 hover:text-muted">
                    Order <ArrowUpDown size={11} />
                  </button>
                </th>
                <th className="px-4 py-2.5 font-medium">Customer</th>
                <th className="px-4 py-2.5 font-medium">Issue</th>
                <th className="px-4 py-2.5 font-medium">Risk</th>
                <th className="px-4 py-2.5 font-medium text-right">
                  <button onClick={() => toggleSort('discrepancy_amount')} className="inline-flex items-center gap-1 hover:text-muted">
                    Discrepancy <ArrowUpDown size={11} />
                  </button>
                </th>
                <th className="px-4 py-2.5 font-medium">Status</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => {
                const status = statusOverrides[row.order_id]
                return (
                  <tr
                    key={row.order_id}
                    onClick={() => onRowClick?.(row.order_id)}
                    className="cursor-pointer border-t border-line transition-colors hover:bg-ink-800"
                  >
                    <td className="px-4 py-3 font-mono text-[12.5px] text-paper">{row.order_id}</td>
                    <td className="px-4 py-3 text-[13px] text-paper">{row.customer_name}</td>
                    <td className="px-4 py-3 text-[12.5px] text-muted">{issueLabel(row.issue_type)}</td>
                    <td className="px-4 py-3">
                      <RiskBadge level={row.risk_level} size="sm" />
                    </td>
                    <td className="px-4 py-3 text-right font-mono text-[13px] tabular text-risk-high">
                      {formatINR(row.discrepancy_amount)}
                    </td>
                    <td className="px-4 py-3 text-[12px]">
                      {status === 'approved' ? (
                        <span className="text-risk-low">Resolved</span>
                      ) : (
                        <span className="text-faint">Open</span>
                      )}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}

      {!loading && !error && (
        <Pagination page={page} pageSize={pageSize} total={total} onPageChange={setPage} />
      )}
    </div>
  )
}
