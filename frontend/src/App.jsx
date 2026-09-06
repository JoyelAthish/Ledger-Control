import { Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Exceptions from './pages/Exceptions.jsx'
import Analytics from './pages/Analytics.jsx'
import Transactions from './pages/Transactions.jsx'
import Settings from './pages/Settings.jsx'

export default function App() {
  return (
    <div className="flex h-screen w-screen overflow-hidden bg-ink-950">
      <Sidebar />
      <main className="flex-1 overflow-y-auto">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/exceptions" element={<Exceptions />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/transactions" element={<Transactions />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </main>
    </div>
  )
}
