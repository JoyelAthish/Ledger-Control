import { NavLink } from 'react-router-dom'
import { LayoutGrid, AlertOctagon, LineChart, Layers, SlidersHorizontal, Radio } from 'lucide-react'
import { useEffect, useState } from 'react'
import { getHealth } from '../api/client.js'

const NAV_ITEMS = [
  { to: '/', label: 'Dashboard', icon: LayoutGrid, end: true },
  { to: '/exceptions', label: 'Exceptions', icon: AlertOctagon },
  { to: '/analytics', label: 'Analytics', icon: LineChart },
  { to: '/transactions', label: 'Transactions', icon: Layers },
  { to: '/settings', label: 'Settings', icon: SlidersHorizontal },
]

export default function Sidebar() {
  const [online, setOnline] = useState(null)

  useEffect(() => {
    let mounted = true
    getHealth()
      .then((h) => mounted && setOnline(h.status === 'ok'))
      .catch(() => mounted && setOnline(false))
    return () => {
      mounted = false
    }
  }, [])

  return (
    <aside className="flex h-full w-60 shrink-0 flex-col border-r border-line bg-ink-900">
      <div className="flex items-center gap-2.5 px-5 pb-5 pt-6">
        <div className="flex h-8 w-8 items-center justify-center rounded-md2 bg-accent/15">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M2 8h5l1.5-4 2 8L12 8h2" stroke="#4C7CF3" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </div>
        <div className="leading-tight">
          <p className="text-[13.5px] font-semibold tracking-tight text-paper">Ledger Control</p>
          <p className="text-[11px] text-faint">Finance reconciliation</p>
        </div>
      </div>

      <nav className="flex-1 space-y-0.5 px-3">
        {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              `group flex items-center gap-2.5 rounded-md2 px-3 py-2 text-[13.5px] transition-colors ${
                isActive
                  ? 'bg-accent/12 text-paper'
                  : 'text-muted hover:bg-ink-800 hover:text-paper'
              }`
            }
          >
            {({ isActive }) => (
              <>
                <Icon size={16} strokeWidth={2} className={isActive ? 'text-accent' : 'text-faint group-hover:text-muted'} />
                <span>{label}</span>
              </>
            )}
          </NavLink>
        ))}
      </nav>

      <div className="mx-3 mb-4 flex items-center gap-2 rounded-md2 border border-line bg-ink-800 px-3 py-2.5">
        <Radio
          size={13}
          className={online === null ? 'text-faint' : online ? 'text-risk-low' : 'text-risk-high'}
        />
        <div className="leading-tight">
          <p className="text-[12px] text-paper">
            {online === null ? 'Checking engine…' : online ? 'Engine online' : 'Engine unreachable'}
          </p>
          <p className="text-[10.5px] text-faint">Rule-based reconciliation</p>
        </div>
      </div>
    </aside>
  )
}
