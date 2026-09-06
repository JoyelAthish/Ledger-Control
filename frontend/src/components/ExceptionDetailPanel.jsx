import { useEffect, useState } from 'react'
import { X, Copy, Check, RefreshCcw, Sparkles, CheckCircle2, ArrowRight } from 'lucide-react'
import RiskBadge from './RiskBadge.jsx'
import LoadingState from './LoadingState.jsx'
import { formatINR, issueLabel } from '../lib/format.js'
import { getExceptionDetail, resolveException, regenerateException, approveException } from '../api/client.js'

function AmountCell({ label, value, tone = 'default' }) {
  const toneCls =
    tone === 'bad' ? 'text-risk-high' : tone === 'good' ? 'text-risk-low' : 'text-paper'
  return (
    <div className="flex-1 rounded-md2 border border-line bg-ink-800 px-3 py-3">
      <p className="text-[11px] text-faint">{label}</p>
      <p className={`mt-1 font-mono text-[15px] tabular ${toneCls}`}>{formatINR(value)}</p>
    </div>
  )
}

function CopyButton({ text, label }) {
  const [copied, setCopied] = useState(false)
  return (
    <button
      onClick={async () => {
        try {
          await navigator.clipboard.writeText(text || '')
          setCopied(true)
          setTimeout(() => setCopied(false), 1500)
        } catch {
          // clipboard unavailable — ignore
        }
      }}
      className="inline-flex items-center gap-1.5 rounded-md2 border border-line px-2.5 py-1.5 text-[12px] text-muted hover:bg-ink-700 hover:text-paper"
    >
      {copied ? <Check size={13} className="text-risk-low" /> : <Copy size={13} />}
      {copied ? 'Copied' : label}
    </button>
  )
}

export default function ExceptionDetailPanel({ orderId, onClose, onStatusChange }) {
  const [detail, setDetail] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [generating, setGenerating] = useState(false)
  const [busyAction, setBusyAction] = useState(null)

  const load = () => {
    setLoading(true)
    setError(null)
    getExceptionDetail(orderId)
      .then((d) => setDetail(d))
      .catch((e) => setError(e?.response?.data?.detail || 'Could not load this exception.'))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [orderId])

  const handleGenerate = async () => {
    setGenerating(true)
    try {
      const res = await resolveException(orderId, false)
      setDetail((d) => ({ ...d, ai_resolution: res }))
    } catch (e) {
      setError(e?.response?.data?.detail || 'Resolution generation failed.')
    } finally {
      setGenerating(false)
    }
  }

  const handleRegenerate = async () => {
    setBusyAction('regenerate')
    try {
      const res = await regenerateException(orderId)
      setDetail((d) => ({ ...d, ai_resolution: res }))
    } catch (e) {
      setError(e?.response?.data?.detail || 'Regeneration failed.')
    } finally {
      setBusyAction(null)
    }
  }

  const handleApprove = async () => {
    setBusyAction('approve')
    try {
      const res = await approveException(orderId)
      setDetail((d) => ({ ...d, ai_resolution: { ...d.ai_resolution, status: res.status } }))
      onStatusChange?.(orderId, res.status)
    } catch (e) {
      setError(e?.response?.data?.detail || 'Approve failed.')
    } finally {
      setBusyAction(null)
    }
  }

  const resolution = detail?.ai_resolution
  const isApproved = resolution?.status === 'approved'

  return (
    <div className="fixed inset-0 z-40 flex justify-end">
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />
      <div className="relative flex h-full w-full max-w-[520px] animate-slideIn flex-col border-l border-line bg-ink-900 shadow-2xl">
        <div className="flex items-start justify-between border-b border-line px-6 py-5">
          <div>
            <p className="font-mono text-[13px] text-faint">{orderId}</p>
            {detail && (
              <div className="mt-1.5 flex items-center gap-2">
                <p className="text-[15px] font-semibold text-paper">{detail.customer_name}</p>
                <RiskBadge level={detail.risk_level} size="sm" />
              </div>
            )}
          </div>
          <button onClick={onClose} className="rounded-md2 p-1.5 text-muted hover:bg-ink-700 hover:text-paper">
            <X size={17} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-6 py-5">
          {loading && <LoadingState label="Loading exception…" />}
          {error && !loading && (
            <div className="rounded-md2 border border-risk-high/30 bg-risk-highSoft px-4 py-3 text-[13px] text-risk-high">
              {error}
            </div>
          )}

          {detail && !loading && (
            <div className="space-y-6">
              <div>
                <p className="mb-2 text-[12px] font-medium text-muted">Issue</p>
                <div className="flex items-center justify-between rounded-md2 border border-line bg-ink-800 px-4 py-3">
                  <span className="text-[13.5px] text-paper">{issueLabel(detail.issue_type)}</span>
                  <span className="font-mono text-[14px] tabular text-risk-high">
                    {formatINR(detail.discrepancy_amount)}
                  </span>
                </div>
                {detail.description && (
                  <p className="mt-2 text-[12.5px] leading-relaxed text-muted">{detail.description}</p>
                )}
              </div>

              <div>
                <p className="mb-2 text-[12px] font-medium text-muted">Store → gateway → bank</p>
                <div className="flex items-center gap-2">
                  <AmountCell label="Store ledger" value={detail.store_amount} />
                  <ArrowRight size={14} className="shrink-0 text-faint" />
                  <AmountCell label="Gateway (Razorpay)" value={detail.gateway_amount} />
                  <ArrowRight size={14} className="shrink-0 text-faint" />
                  <AmountCell label="Bank deposit" value={detail.bank_amount} />
                </div>
                <div className="mt-2 flex items-center gap-2">
                  <AmountCell label="Gateway fee" value={detail.gateway_fee} />
                  <AmountCell label="Variance" value={detail.discrepancy_amount} tone="bad" />
                </div>
              </div>

              <div>
                <div className="mb-2 flex items-center justify-between">
                  <p className="text-[12px] font-medium text-muted">AI resolution package</p>
                  {resolution && (
                    <span
                      className={`rounded-full border px-2 py-0.5 text-[10.5px] font-medium ${
                        isApproved
                          ? 'border-risk-low/30 bg-risk-lowSoft text-risk-low'
                          : 'border-line bg-ink-700 text-muted'
                      }`}
                    >
                      {isApproved ? 'Approved · resolved' : 'Generated'}
                    </span>
                  )}
                </div>

                {!resolution && (
                  <button
                    onClick={handleGenerate}
                    disabled={generating}
                    className="flex w-full items-center justify-center gap-2 rounded-md2 bg-accent px-4 py-2.5 text-[13px] font-medium text-white transition-colors hover:bg-accent-hover disabled:opacity-60"
                  >
                    {generating ? (
                      <>
                        <div className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                        Generating diagnosis and dispute email…
                      </>
                    ) : (
                      <>
                        <Sparkles size={14} />
                        Generate resolution package
                      </>
                    )}
                  </button>
                )}

                {resolution && (
                  <div className="space-y-3">
                    <div className="rounded-md2 border border-line bg-ink-800 p-3.5">
                      <div className="mb-1.5 flex items-center justify-between">
                        <p className="text-[11.5px] font-medium text-muted">Root-cause diagnosis</p>
                        <CopyButton text={resolution.diagnosis} label="Copy" />
                      </div>
                      <p className="whitespace-pre-wrap text-[13px] leading-relaxed text-paper">
                        {resolution.diagnosis}
                      </p>
                    </div>

                    <div className="rounded-md2 border border-line bg-ink-800 p-3.5">
                      <div className="mb-1.5 flex items-center justify-between">
                        <p className="text-[11.5px] font-medium text-muted">Vendor dispute email</p>
                        <CopyButton text={resolution.email} label="Copy" />
                      </div>
                      <p className="whitespace-pre-wrap text-[13px] leading-relaxed text-paper">
                        {resolution.email}
                      </p>
                    </div>

                    <div className="flex items-center gap-2 pt-1">
                      <button
                        onClick={handleApprove}
                        disabled={isApproved || busyAction === 'approve'}
                        className="flex flex-1 items-center justify-center gap-1.5 rounded-md2 bg-risk-low px-3 py-2 text-[12.5px] font-medium text-ink-950 transition-opacity hover:opacity-90 disabled:opacity-50"
                      >
                        <CheckCircle2 size={14} />
                        {isApproved ? 'Marked resolved' : busyAction === 'approve' ? 'Approving…' : 'Approve · mark resolved'}
                      </button>
                      <button
                        onClick={handleRegenerate}
                        disabled={busyAction === 'regenerate'}
                        className="flex items-center justify-center gap-1.5 rounded-md2 border border-line px-3 py-2 text-[12.5px] text-muted hover:bg-ink-700 hover:text-paper disabled:opacity-50"
                      >
                        <RefreshCcw size={13} className={busyAction === 'regenerate' ? 'animate-spin' : ''} />
                        Regenerate
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
