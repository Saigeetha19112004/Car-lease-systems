import { useEffect, useState } from 'react'
import AdminLayout from '../../components/admin/Layout'

export default function ReportsPage() {
  const [summary, setSummary] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (!token) return
    fetch('/api/v1/admin/reports/summary', {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((r) => {
        if (!r.ok) throw new Error('failed')
        return r.json()
      })
      .then(setSummary)
      .catch((e) => setError(e.message))
  }, [])

  return (
    <AdminLayout>
      <h1>Admin Reports</h1>
      {error && <p style={{color:'red'}}>Error: {error}</p>}
      {summary ? (
        <div>
          <p>Cars: <strong>{summary.cars}</strong></p>
          <p>Leases: <strong>{summary.leases}</strong></p>
          <p>Payments: <strong>{summary.payments}</strong></p>
          <p>Users: <strong>{summary.users}</strong></p>
        </div>
      ) : (
        <p>Loading…</p>
      )}
    </AdminLayout>
  )
}