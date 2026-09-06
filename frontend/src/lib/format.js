export function formatINR(value, { compact = false } = {}) {
  const n = Number(value ?? 0)
  if (compact) {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      notation: 'compact',
      maximumFractionDigits: 1,
    }).format(n)
  }
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 2,
  }).format(n)
}

export function formatNumber(value) {
  return new Intl.NumberFormat('en-IN').format(Number(value ?? 0))
}

export function formatPct(value) {
  return `${Number(value ?? 0).toFixed(2)}%`
}

export const ISSUE_LABELS = {
  MISSING_GATEWAY_PAYOUT: 'Missing gateway payout',
  PAYMENT_FAILED: 'Payment failed',
  FEE_OVERCHARGE_ANOMALY: 'Fee overcharge anomaly',
  BANK_DEPOSIT_SHORTFALL: 'Bank deposit shortfall',
  ORPHAN_BANK_CREDIT: 'Orphan bank credit',
}

export function issueLabel(type) {
  return ISSUE_LABELS[type] || type?.replaceAll('_', ' ').toLowerCase() || 'Unknown'
}

export function initials(name) {
  if (!name) return '??'
  const parts = name.trim().split(/\s+/)
  return (parts[0]?.[0] || '') + (parts[1]?.[0] || '')
}
