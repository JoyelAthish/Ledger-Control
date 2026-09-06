import { useEffect, useState } from 'react'
import { Wallet, AlertTriangle, FlameKindling, PercentCircle } from 'lucide-react'
import PageHeader from '../components/PageHeader.jsx'
import KpiCard from '../components/KpiCard.jsx'
import ExceptionQueue from '../components/ExceptionQueue.jsx'
import ExceptionDetailPanel from '../components/ExceptionDetailPanel.jsx'
import LoadingState from '../components/LoadingState.jsx'
import EmptyState from '../components/EmptyState.jsx'
import { getDashboard } from '../api/client.js'
import { formatINR, formatNumber, formatPct } from '../lib/format.js'

export default function Dashboard() {
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [activeOrder, setActiveOrder] = useState(null)
  const [statusOverrides, setStatusOverrides] = useState({})

  useEffect(() => {
    getDashboard()
      .then(setSummary)
      .catch((e) => setError(e?.response?.data?.detail || 'Could not load dashboard summary.'))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div>
      <PageHeader
        title="Dashboard"
        description="Reconciliation health across store ledger, gateway, and bank data."
      />

      <div className="px-8 py-6">
        {loading && <LoadingState label="Loading dashboard…" />}
        {error && !loading && (
          <EmptyState variant="error" title="Couldn't load the dashboard" description={error} />
        )}

        {summary && !loading && (
          <>
            <div className="flex flex-col gap-3 sm:flex-row">
              <KpiCard
                label="Total orders"
                value={formatNumber(summary.total_orders)}
                sub={`${formatPct(summary.match_rate_pct)} auto-matched, no review needed`}
                accentColor="#4C7CF3"
                icon={Wallet}
              />
              <KpiCard
                label="Flagged exceptions"
                value={formatNumber(summary.flagged_exceptions)}
                sub="Awaiting reconciliation review"
                accentColor="#F0A83C"
                icon={AlertTriangle}
              />
              <KpiCard
                label="High-priority cases"
                value={formatNumber(summary.high_priority_cases)}
                sub="Risk level HIGH — review first"
                accentColor="#F1546B"
                icon={FlameKindling}
              />
              <KpiCard
                label="Total disputed amount"
                value={formatINR(summary.total_disputed_amount, { compact: true })}
                sub={formatINR(summary.total_disputed_amount)}
                accentColor="#34C77B"
                icon={PercentCircle}
              />
            </div>

            <div className="mt-6">
              <ExceptionQueue
                title="Exception priority queue"
                pageSize={10}
                onRowClick={setActiveOrder}
                statusOverrides={statusOverrides}
              />
            </div>
          </>
        )}
      </div>

      {activeOrder && (
        <ExceptionDetailPanel
          orderId={activeOrder}
          onClose={() => setActiveOrder(null)}
          onStatusChange={(orderId, status) =>
            setStatusOverrides((prev) => ({ ...prev, [orderId]: status }))
          }
        />
      )}
    </div>
  )
}
