import { useState, useEffect, useCallback } from 'react'
import { getDashboard, getTechnicians } from '../services/api'
import { initials } from '../utils/formatters'
import PriorityBadge from '../components/PriorityBadge'
import StatusBadge from '../components/StatusBadge'

export default function Dashboard({ onOpenRequest }) {
  const [data, setData] = useState(null)
  const [techs, setTechs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const [dash, t] = await Promise.all([getDashboard(), getTechnicians()])
      setData(dash)
      setTechs(t)
    } catch (e) {
      setError('Failed to load dashboard. Is the backend running?')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  if (loading) return <div className="loading-text">Loading dashboard…</div>
  if (error)   return <div className="error-state">⚠ {error}</div>
  if (!data)   return null

  const { stats, needs_attention } = data

  return (
    <>
      <div className="page-header">
        <h1>Operations Dashboard</h1>
        <button className="btn btn-secondary" onClick={load}>↻ Refresh</button>
      </div>

      {/* Stats */}
      <div className="stat-grid">
        <div className="stat-tile">
          <div className="stat-tile__value">{stats.total_open}</div>
          <div className="stat-tile__label">Open Requests</div>
        </div>
        <div className="stat-tile urgent">
          <div className="stat-tile__value">{stats.urgent}</div>
          <div className="stat-tile__label">Urgent</div>
        </div>
        <div className="stat-tile warning">
          <div className="stat-tile__value">{stats.unassigned}</div>
          <div className="stat-tile__label">Unassigned</div>
        </div>
        <div className="stat-tile accent">
          <div className="stat-tile__value">{stats.assigned}</div>
          <div className="stat-tile__label">Assigned</div>
        </div>
        <div className="stat-tile muted">
          <div className="stat-tile__value">{stats.waiting}</div>
          <div className="stat-tile__label">Waiting</div>
        </div>
        <div className="stat-tile warning">
          <div className="stat-tile__value">{stats.needs_clarification}</div>
          <div className="stat-tile__label">Needs Clarification</div>
        </div>
        <div className="stat-tile muted">
          <div className="stat-tile__value">{stats.duplicates}</div>
          <div className="stat-tile__label">Duplicates</div>
        </div>
      </div>

      <div className="dashboard-grid">
        {/* Needs Attention */}
        <div className="card">
          <div className="card-header">
            <h2>⚠ Needs Attention</h2>
          </div>
          {needs_attention.length === 0 ? (
            <div className="empty-state"><p>✓ No urgent items.</p></div>
          ) : (
            <div className="attention-list">
              {needs_attention.map(item => (
                <div
                  key={item.id}
                  className="attention-item"
                  onClick={() => onOpenRequest(item.id)}
                  role="button"
                  tabIndex={0}
                  onKeyDown={e => e.key === 'Enter' && onOpenRequest(item.id)}
                  id={`attention-${item.id}`}
                >
                  <span className="attention-item__id">{item.id}</span>
                  <span className="attention-item__message">{item.message_snippet}</span>
                  <div className="attention-item__badges">
                    <PriorityBadge priority={item.priority} />
                    <StatusBadge status={item.status} />
                    {item.needs_clarification && (
                      <span className="badge badge-warn">⚠ Clarify</span>
                    )}
                    {!item.technician_id && item.priority === 'urgent' && (
                      <span className="badge badge-warn">Unassigned</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Technician workload */}
        <div className="card">
          <div className="card-header">
            <h2>👷 Technician Workload</h2>
          </div>
          {techs.length === 0 ? (
            <div className="empty-state"><p>No technicians found.</p></div>
          ) : (
            <div className="tech-list">
              {techs.map(t => (
                <div key={t.id} className="tech-item">
                  <div className="tech-item__avatar">{initials(t.name)}</div>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <span className="tech-item__name">{t.name}</span>
                      <span className="tech-item__id">{t.id}</span>
                    </div>
                  </div>
                  <div className="tech-item__count">
                    {t.assigned_count} open {t.assigned_count === 1 ? 'request' : 'requests'}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  )
}
