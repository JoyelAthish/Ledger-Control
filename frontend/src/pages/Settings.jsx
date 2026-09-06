import { useEffect, useState } from 'react'
import { CheckCircle2, XCircle, Trash2, RefreshCw, KeyRound } from 'lucide-react'
import PageHeader from '../components/PageHeader.jsx'
import LoadingState from '../components/LoadingState.jsx'
import { getHealth, clearCache } from '../api/client.js'

function Row({ label, value, ok }) {
  return (
    <div className="flex items-center justify-between border-b border-line py-3 last:border-b-0">
      <p className="text-[13px] text-muted">{label}</p>
      <div className="flex items-center gap-1.5">
        {ok !== undefined &&
          (ok ? <CheckCircle2 size={14} className="text-risk-low" /> : <XCircle size={14} className="text-risk-high" />)}
        <p className="text-[13px] text-paper">{value}</p>
      </div>
    </div>
  )
}

export default function Settings() {
  const [health, setHealth] = useState(null)
  const [loading, setLoading] = useState(true)
  const [confirmingClear, setConfirmingClear] = useState(false)
  const [clearing, setClearing] = useState(false)
  const [justCleared, setJustCleared] = useState(false)

  const load = () => {
    setLoading(true)
    getHealth()
      .then(setHealth)
      .finally(() => setLoading(false))
  }

  useEffect(load, [])

  const handleClear = async () => {
    setClearing(true)
    try {
      await clearCache()
      setJustCleared(true)
      load()
      setTimeout(() => setJustCleared(false), 2500)
    } finally {
      setClearing(false)
      setConfirmingClear(false)
    }
  }

  return (
    <div>
      <PageHeader title="Settings" description="System health, AI cache, and engine configuration." />

      <div className="grid max-w-3xl grid-cols-1 gap-5 px-8 py-6">
        <div className="rounded-md2 border border-line bg-ink-900 p-5 shadow-panel">
          <div className="mb-1 flex items-center justify-between">
            <p className="text-[13.5px] font-medium text-paper">System health</p>
            <button
              onClick={load}
              className="flex items-center gap-1.5 rounded-md2 border border-line px-2.5 py-1.5 text-[12px] text-muted hover:bg-ink-700 hover:text-paper"
            >
              <RefreshCw size={12} />
              Refresh
            </button>
          </div>

          {loading && <LoadingState label="Checking system…" />}

          {health && !loading && (
            <div className="mt-2">
              <Row label="API status" value={health.status} ok={health.status === 'ok'} />
              <Row label="Reconciliation engine" value={health.reconciliation_engine} />
              <Row label="AI model" value={health.ai_model} />
              <Row
                label="Gemini API key"
                value={health.gemini_key_configured ? 'Configured' : 'Missing'}
                ok={health.gemini_key_configured}
              />
              <Row label="Data source" value={health.data_source} ok={health.data_source === 'ok'} />
            </div>
          )}
        </div>

        <div className="rounded-md2 border border-line bg-ink-900 p-5 shadow-panel">
          <p className="mb-1 text-[13.5px] font-medium text-paper">AI resolution cache</p>
          <p className="mb-4 text-[12.5px] text-muted">
            Cached diagnoses and dispute emails avoid re-calling Gemini for exceptions you've already resolved.
          </p>

          {health && (
            <div className="mb-4 flex items-center gap-3 rounded-md2 border border-line bg-ink-800 px-4 py-3">
              <div className="flex h-8 w-8 items-center justify-center rounded-md2 bg-accent/15">
                <KeyRound size={14} className="text-accent" />
              </div>
              <div>
                <p className="font-mono text-[17px] tabular text-paper">
                  {health.cache_status?.cached_ticket_count ?? 0}
                </p>
                <p className="text-[11.5px] text-faint">cached tickets</p>
              </div>
            </div>
          )}

          {!confirmingClear ? (
            <button
              onClick={() => setConfirmingClear(true)}
              className="flex items-center gap-1.5 rounded-md2 border border-risk-high/30 bg-risk-highSoft px-3 py-2 text-[12.5px] font-medium text-risk-high hover:bg-risk-high/20"
            >
              <Trash2 size={13} />
              Clear cache
            </button>
          ) : (
            <div className="flex items-center gap-2">
              <p className="text-[12.5px] text-muted">Clear all cached resolutions? This can't be undone.</p>
              <button
                onClick={handleClear}
                disabled={clearing}
                className="rounded-md2 bg-risk-high px-3 py-1.5 text-[12.5px] font-medium text-white hover:opacity-90 disabled:opacity-60"
              >
                {clearing ? 'Clearing…' : 'Confirm clear'}
              </button>
              <button
                onClick={() => setConfirmingClear(false)}
                className="rounded-md2 border border-line px-3 py-1.5 text-[12.5px] text-muted hover:bg-ink-700"
              >
                Cancel
              </button>
            </div>
          )}

          {justCleared && <p className="mt-3 text-[12px] text-risk-low">Cache cleared.</p>}
        </div>
      </div>
    </div>
  )
}
