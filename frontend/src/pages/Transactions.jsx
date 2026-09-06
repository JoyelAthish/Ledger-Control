import { useEffect, useState } from 'react'
import { Search } from 'lucide-react'
import PageHeader from '../components/PageHeader.jsx'
import Pagination from '../components/Pagination.jsx'
import LoadingState from '../components/LoadingState.jsx'
import EmptyState from '../components/EmptyState.jsx'
import { getTransactions } from '../api/client.js'

const TABS = [
  { id: 'store', label: 'Store ledger' },
  { id: 'gateway', label: 'Gateway (Razorpay)' },
  { id: 'bank', label: 'Bank statement' },
  { id: 'exceptions', label: 'Exceptions' },
]

function prettifyColumn(col) {
  return col.replaceAll('_', ' ')
}

function formatCell(value) {
  if (value === null || value === undefined || value === '') return <span className="text-faint">—</span>
  if (typeof value === 'number') {
    return <span className="font-mono tabular">{value.toLocaleString('en-IN')}</span>
  }
  return String(value)
}

export default function Transactions() {
  const [tab, setTab] = useState('store')
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const pageSize = 25

  useEffect(() => {
    setPage(1)
    setSearch('')
  }, [tab])

  useEffect(() => {
    setLoading(true)
    setError(null)
    const params = { page, page_size: pageSize }
    if (search.trim()) params.search = search.trim()
    getTransactions(tab, params)
      .then(setData)
      .catch((e) => setError(e?.response?.data?.detail || 'Could not load transactions.'))
      .finally(() => setLoading(false))
  }, [tab, page, search])

  return (
    <div>
      <PageHeader
        title="Transactions"
        description="Raw records from every source feeding the reconciliation engine."
      />

      <div className="px-8 py-6">
        <div className="mb-4 flex items-center gap-1 border-b border-line">
          {TABS.map((t) => (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              className={`border-b-2 px-3.5 py-2.5 text-[13px] transition-colors ${
                tab === t.id
                  ? 'border-accent text-paper'
                  : 'border-transparent text-muted hover:text-paper'
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>

        <div className="rounded-md2 border border-line bg-ink-900 shadow-panel">
          <div className="flex items-center justify-between border-b border-line px-4 py-3">
            <div className="flex items-center gap-1.5 rounded-md2 border border-line bg-ink-800 px-2.5 py-1.5">
              <Search size={13} className="text-faint" />
              <input
                value={search}
                onChange={(e) => {
                  setPage(1)
                  setSearch(e.target.value)
                }}
                placeholder="Search this table"
                className="w-56 bg-transparent text-[12.5px] text-paper placeholder:text-faint focus:outline-none"
              />
            </div>
            {data && <p className="text-[12px] text-faint">{data.total.toLocaleString('en-IN')} rows</p>}
          </div>

          {loading && <LoadingState label="Loading records…" />}
          {error && !loading && (
            <div className="p-4">
              <EmptyState variant="error" title="Couldn't load this table" description={error} />
            </div>
          )}

          {!loading && !error && data && data.results.length === 0 && (
            <div className="p-4">
              <EmptyState title="No matching rows" description="Try a different search term." />
            </div>
          )}

          {!loading && !error && data && data.results.length > 0 && (
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr className="text-[11px] text-faint">
                    {data.columns.map((col) => (
                      <th key={col} className="whitespace-nowrap px-4 py-2.5 font-medium capitalize">
                        {prettifyColumn(col)}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {data.results.map((row, i) => (
                    <tr key={i} className="border-t border-line hover:bg-ink-800">
                      {data.columns.map((col) => (
                        <td key={col} className="whitespace-nowrap px-4 py-2.5 text-[12.5px] text-paper">
                          {formatCell(row[col])}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {!loading && !error && data && (
            <Pagination page={page} pageSize={pageSize} total={data.total} onPageChange={setPage} />
          )}
        </div>
      </div>
    </div>
  )
}
