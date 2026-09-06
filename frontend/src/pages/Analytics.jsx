import { useEffect, useState } from 'react'
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  PieChart,
  Pie,
  Cell,
  Legend,
} from 'recharts'
import PageHeader from '../components/PageHeader.jsx'
import LoadingState from '../components/LoadingState.jsx'
import EmptyState from '../components/EmptyState.jsx'
import { getAnalytics } from '../api/client.js'
import { formatINR, issueLabel } from '../lib/format.js'

const RISK_COLORS = { HIGH: '#F1546B', MEDIUM: '#F0A83C', LOW: '#34C77B' }

function ChartCard({ title, children, className = '' }) {
  return (
    <div className={`rounded-md2 border border-line bg-ink-900 p-5 shadow-panel ${className}`}>
      <p className="mb-4 text-[13.5px] font-medium text-paper">{title}</p>
      {children}
    </div>
  )
}

function TooltipCard({ active, payload, label, formatter }) {
  if (!active || !payload?.length) return null
  return (
    <div className="rounded-md2 border border-line bg-ink-800 px-3 py-2 text-[12px] shadow-panel">
      {label && <p className="mb-1 text-muted">{label}</p>}
      {payload.map((p, i) => (
        <p key={i} className="font-mono text-paper">
          {formatter ? formatter(p.value) : p.value}
        </p>
      ))}
    </div>
  )
}

export default function Analytics() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    getAnalytics()
      .then(setData)
      .catch((e) => setError(e?.response?.data?.detail || 'Could not load analytics.'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return (
    <div>
      <PageHeader title="Analytics" description="Where the money is going and which risks dominate." />
      <div className="px-8 py-6"><LoadingState label="Crunching numbers…" /></div>
    </div>
  )

  if (error) return (
    <div>
      <PageHeader title="Analytics" description="Where the money is going and which risks dominate." />
      <div className="px-8 py-6"><EmptyState variant="error" title="Couldn't load analytics" description={error} /></div>
    </div>
  )

  const lossData = data.loss_by_issue_type.map((d) => ({ ...d, label: issueLabel(d.issue_type) }))
  const riskData = data.exceptions_by_risk

  return (
    <div>
      <PageHeader title="Analytics" description="Where the money is going and which risks dominate." />
      <div className="grid grid-cols-1 gap-5 px-8 py-6 lg:grid-cols-5">
        <ChartCard title="Disputed amount by issue type" className="lg:col-span-3">
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={lossData} layout="vertical" margin={{ left: 8, right: 16 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#212940" horizontal={false} />
              <XAxis
                type="number"
                stroke="#4E586F"
                tick={{ fill: '#818CA3', fontSize: 11 }}
                tickFormatter={(v) => formatINR(v, { compact: true })}
              />
              <YAxis
                type="category"
                dataKey="label"
                width={150}
                stroke="#4E586F"
                tick={{ fill: '#818CA3', fontSize: 11.5 }}
              />
              <Tooltip
                cursor={{ fill: '#1A2032' }}
                content={<TooltipCard formatter={(v) => formatINR(v)} />}
              />
              <Bar dataKey="total_loss" fill="#4C7CF3" radius={[0, 4, 4, 0]} barSize={22} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Exceptions by risk level" className="lg:col-span-2">
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie
                data={riskData}
                dataKey="count"
                nameKey="risk_level"
                innerRadius={60}
                outerRadius={95}
                paddingAngle={3}
              >
                {riskData.map((entry) => (
                  <Cell key={entry.risk_level} fill={RISK_COLORS[entry.risk_level] || '#4E586F'} stroke="none" />
                ))}
              </Pie>
              <Tooltip content={<TooltipCard />} />
              <Legend
                iconType="circle"
                iconSize={8}
                formatter={(value) => <span style={{ color: '#818CA3', fontSize: 12 }}>{value}</span>}
              />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Top 10 exceptions by discrepancy" className="lg:col-span-5">
          <table className="w-full text-left">
            <thead>
              <tr className="text-[11px] text-faint">
                <th className="py-2 font-medium">Order</th>
                <th className="py-2 font-medium">Customer</th>
                <th className="py-2 font-medium">Issue</th>
                <th className="py-2 text-right font-medium">Amount</th>
              </tr>
            </thead>
            <tbody>
              {data.top_10_exceptions.map((row) => (
                <tr key={row.order_id} className="border-t border-line">
                  <td className="py-2.5 font-mono text-[12.5px] text-paper">{row.order_id}</td>
                  <td className="py-2.5 text-[13px] text-paper">{row.customer_name}</td>
                  <td className="py-2.5 text-[12.5px] text-muted">{issueLabel(row.issue_type)}</td>
                  <td className="py-2.5 text-right font-mono text-[13px] tabular text-risk-high">
                    {formatINR(row.discrepancy_amount)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </ChartCard>
      </div>
    </div>
  )
}
