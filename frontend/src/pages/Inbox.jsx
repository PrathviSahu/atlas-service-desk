import { useState, useEffect, useCallback } from 'react'
import { getRequests } from '../services/api'
import PriorityBadge from '../components/PriorityBadge'
import StatusBadge from '../components/StatusBadge'
import ChannelBadge from '../components/ChannelBadge'
import { formatRelative, formatDateTime } from '../utils/formatters'

const FILTERS = [
  { key: 'all',               label: 'All' },
  { key: 'urgent',            label: '🔴 Urgent',            params: { priority: 'urgent' } },
  { key: 'unassigned',        label: 'Unassigned',           params: { flag: 'unassigned' } },
  { key: 'needs_clarification', label: '⚠ Needs Clarification', params: { flag: 'needs_clarification' } },
  { key: 'duplicate',         label: 'Duplicates',           params: { flag: 'duplicate' } },
  { key: 'waiting',           label: 'Waiting',              params: { status: 'waiting' } },
  { key: 'resolved',          label: 'Resolved',             params: { status: 'resolved' } },
]

export default function Inbox({ onOpenRequest }) {
  const [requests, setRequests] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [activeFilter, setActiveFilter] = useState('all')

  const load = useCallback(async (filterKey) => {
    setLoading(true)
    setError(null)
    try {
      const filter = FILTERS.find(f => f.key === filterKey) || FILTERS[0]
      const params = filter.params || {}
      const data = await getRequests(params)
      setRequests(data)
    } catch (e) {
      setError('Failed to load requests. Is the backend running?')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load(activeFilter) }, [activeFilter, load])

  const handleFilter = (key) => {
    setActiveFilter(key)
  }

  return (
    <>
      <div className="page-header">
        <h1>Request Inbox</h1>
        <button className="btn btn-secondary" onClick={() => load(activeFilter)}>↻ Refresh</button>
      </div>

      <div className="filter-bar" role="group" aria-label="Request filters">
        {FILTERS.map(f => (
          <button
            key={f.key}
            className={`filter-btn ${activeFilter === f.key ? 'active' : ''}`}
            onClick={() => handleFilter(f.key)}
            id={`filter-${f.key}`}
          >
            {f.label}
          </button>
        ))}
      </div>

      <div className="card">
        {loading && <div className="loading-text">Loading requests…</div>}
        {error && <div className="error-state">⚠ {error}</div>}

        {!loading && !error && requests.length === 0 && (
          <div className="empty-state">
            <p>No requests match this filter.</p>
          </div>
        )}

        {!loading && !error && requests.length > 0 && (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Customer</th>
                  <th>Channel</th>
                  <th>Request</th>
                  <th>Received</th>
                  <th>Priority</th>
                  <th>Status</th>
                  <th>Technician</th>
                  <th>Flags</th>
                </tr>
              </thead>
              <tbody>
                {requests.map(r => (
                  <tr
                    key={r.id}
                    onClick={() => onOpenRequest(r.id)}
                    title="Click to open"
                    id={`row-${r.id}`}
                  >
                    <td className="td-id">{r.id}</td>
                    <td>{r.customer_id}</td>
                    <td><ChannelBadge channel={r.channel} /></td>
                    <td className="td-message">
                      <div className="td-message-text" title={r.message}>
                        {r.message}
                      </div>
                    </td>
                    <td title={formatDateTime(r.received_at)} style={{ whiteSpace: 'nowrap', color: 'var(--color-text-muted)', fontSize: 12 }}>
                      {formatRelative(r.received_at)}
                    </td>
                    <td><PriorityBadge priority={r.priority} /></td>
                    <td><StatusBadge status={r.status} /></td>
                    <td style={{ color: r.technician_id ? 'var(--color-text)' : 'var(--color-text-dim)', fontFamily: 'monospace', fontSize: 12 }}>
                      {r.technician_id || '—'}
                    </td>
                    <td>
                      <div className="td-flags">
                        {r.needs_clarification && <span className="badge badge-warn">⚠ Clarify</span>}
                        {r.is_duplicate && <span className="badge badge-dup">Duplicate</span>}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </>
  )
}
