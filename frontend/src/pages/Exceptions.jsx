import { useState } from 'react'
import PageHeader from '../components/PageHeader.jsx'
import ExceptionQueue from '../components/ExceptionQueue.jsx'
import ExceptionDetailPanel from '../components/ExceptionDetailPanel.jsx'

export default function Exceptions() {
  const [activeOrder, setActiveOrder] = useState(null)
  const [statusOverrides, setStatusOverrides] = useState({})

  return (
    <div>
      <PageHeader
        title="Exceptions"
        description="Every unreconciled order, ranked by risk. Click a row to diagnose and draft a dispute."
      />
      <div className="px-8 py-6">
        <ExceptionQueue
          pageSize={20}
          showIssueFilter
          onRowClick={setActiveOrder}
          statusOverrides={statusOverrides}
        />
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
