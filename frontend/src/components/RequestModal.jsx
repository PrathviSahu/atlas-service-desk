import { useState, useEffect, useCallback } from 'react'
import {
  getRequest, updateRequest,
  getDuplicateCandidates, getTechnicians, getPrioritySuggestion
} from '../services/api'
import PriorityBadge from './PriorityBadge'
import StatusBadge from './StatusBadge'
import ChannelBadge from './ChannelBadge'
import { formatDateTime, formatRelative } from '../utils/formatters'

const STATUSES = ['open', 'assigned', 'in_progress', 'waiting', 'resolved', 'closed']
const PRIORITIES = ['urgent', 'high', 'normal', 'low']

export default function RequestModal({ requestId, onClose, onUpdated }) {
  const [req, setReq] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)
  const [technicians, setTechnicians] = useState([])
  const [dupCandidates, setDupCandidates] = useState([])
  const [suggestion, setSuggestion] = useState(null)

  // editable fields
  const [priority, setPriority] = useState('')
  const [status, setStatus] = useState('')
  const [techId, setTechId] = useState('')
  const [notes, setNotes] = useState('')

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const [data, techs, dups] = await Promise.all([
        getRequest(requestId),
        getTechnicians(),
        getDuplicateCandidates(requestId),
      ])
      setReq(data)
      setPriority(data.priority)
      setStatus(data.status)
      setTechId(data.technician_id || '')
      setNotes(data.notes || '')
      setTechnicians(techs)
      setDupCandidates(dups)
      // Get priority suggestion
      const sugg = await getPrioritySuggestion(data.message)
      setSuggestion(sugg)
    } catch (e) {
      setError('Failed to load request.')
    } finally {
      setLoading(false)
    }
  }, [requestId])

  useEffect(() => { load() }, [load])

  // Sync editable dropdowns from any server-returned record
  const syncFromUpdated = (updated) => {
    setReq(updated)
    setPriority(updated.priority)
    setStatus(updated.status)
    setTechId(updated.technician_id || '')
    setNotes(updated.notes || '')
  }

  const handleSave = async () => {
    setSaving(true)
    setError(null)
    try {
      const updates = { priority, status, notes }
      if (techId) {
        updates.technician_id = techId
        if (status === 'open') updates.status = 'assigned'
      }
      const updated = await updateRequest(requestId, updates)
      syncFromUpdated(updated)
      onUpdated && onUpdated(updated)
    } catch (e) {
      setError(e.response?.data?.error || 'Save failed.')
    } finally {
      setSaving(false)
    }
  }

  const handleMarkDuplicate = async (dupId) => {
    setSaving(true)
    try {
      const updated = await updateRequest(requestId, {
        is_duplicate: true,
        duplicate_of: dupId,
        status: 'closed',
      })
      syncFromUpdated(updated)
      setDupCandidates([])
      onUpdated && onUpdated(updated)
    } catch (e) {
      setError('Failed to mark duplicate.')
    } finally {
      setSaving(false)
    }
  }

  const handleRemoveDuplicate = async () => {
    setSaving(true)
    try {
      const updated = await updateRequest(requestId, {
        is_duplicate: false,
        duplicate_of: null,
        status: 'open',
      })
      syncFromUpdated(updated)
      onUpdated && onUpdated(updated)
    } catch (e) {
      setError('Failed to remove duplicate.')
    } finally {
      setSaving(false)
    }
  }

  const handleMarkClarified = async () => {
    setSaving(true)
    try {
      const updated = await updateRequest(requestId, {
        needs_clarification: false,
        missing_information: [],
      })
      syncFromUpdated(updated)
      onUpdated && onUpdated(updated)
    } catch (e) {
      setError('Failed to update.')
    } finally {
      setSaving(false)
    }
  }

  // Close on Escape
  useEffect(() => {
    const handler = (e) => { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [onClose])

  return (
    <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="modal" role="dialog" aria-modal="true">
        <div className="modal-header">
          <h2>
            <span style={{ fontFamily: 'monospace', color: 'var(--color-text-muted)' }}>
              {requestId}
            </span>
            {req && (
              <span style={{ marginLeft: 12 }}>
                <PriorityBadge priority={req.priority} />
              </span>
            )}
          </h2>
          <button className="modal-close" onClick={onClose} aria-label="Close">✕</button>
        </div>

        <div className="modal-body">
          {loading && <div className="loading-text">Loading…</div>}
          {error && <div className="alert alert-error"><span className="alert-icon">⚠</span> {error}</div>}

          {req && !loading && (
            <>
              {/* Flags */}
              {req.is_duplicate && (
                <div className="alert alert-dup" style={{ marginBottom: 14 }}>
                  <span className="alert-icon">⚠</span>
                  <div className="alert-content">
                    <div className="alert-title">Marked as Duplicate</div>
                    {req.duplicate_of && <div>Duplicate of <strong>{req.duplicate_of}</strong></div>}
                    <button
                      className="btn btn-sm btn-secondary"
                      style={{ marginTop: 8 }}
                      onClick={handleRemoveDuplicate}
                      disabled={saving}
                    >
                      Remove duplicate status
                    </button>
                  </div>
                </div>
              )}

              {req.needs_clarification && req.missing_information?.length > 0 && (
                <div className="alert alert-warn" style={{ marginBottom: 14 }}>
                  <span className="alert-icon">⚠</span>
                  <div className="alert-content">
                    <div className="alert-title">Needs Clarification</div>
                    <ul style={{ margin: '4px 0 8px 16px', fontSize: 12 }}>
                      {req.missing_information.map(m => <li key={m}>{m}</li>)}
                    </ul>
                    <button
                      className="btn btn-sm btn-secondary"
                      onClick={handleMarkClarified}
                      disabled={saving}
                    >
                      Mark as clarified
                    </button>
                  </div>
                </div>
              )}

              {/* Message */}
              <div className="section-title">Request Message</div>
              <div className="message-box">"{req.message}"</div>

              {/* Priority suggestion */}
              {suggestion && suggestion.suggested !== req.priority && (
                <div className="suggestion-box" style={{ marginBottom: 14 }}>
                  💡 <strong>Priority suggestion:</strong> {suggestion.suggested.toUpperCase()} — {suggestion.reason}
                  <small style={{ display: 'block', marginTop: 4, color: 'var(--color-text-dim)' }}>
                    Rule-based heuristic, not AI. You can override below.
                  </small>
                </div>
              )}

              {/* Detail grid */}
              <div className="detail-grid">
                <div className="detail-field">
                  <div className="detail-field__label">Customer</div>
                  <div className="detail-field__value">{req.customer_id}</div>
                </div>
                <div className="detail-field">
                  <div className="detail-field__label">Channel</div>
                  <div className="detail-field__value"><ChannelBadge channel={req.channel} /></div>
                </div>
                <div className="detail-field">
                  <div className="detail-field__label">Received</div>
                  <div className="detail-field__value" title={formatDateTime(req.received_at)}>
                    {formatRelative(req.received_at)} <span style={{ color: 'var(--color-text-dim)', fontSize: 11 }}>({formatDateTime(req.received_at)})</span>
                  </div>
                </div>
                <div className="detail-field">
                  <div className="detail-field__label">Current Status</div>
                  <div className="detail-field__value"><StatusBadge status={req.status} /></div>
                </div>
              </div>

              <hr className="divider" />

              {/* Editable fields */}
              <div className="form-group">
                <label className="form-label" htmlFor={`priority-${requestId}`}>Priority</label>
                <select
                  id={`priority-${requestId}`}
                  className="form-select"
                  value={priority}
                  onChange={e => setPriority(e.target.value)}
                >
                  {PRIORITIES.map(p => (
                    <option key={p} value={p}>{p.charAt(0).toUpperCase() + p.slice(1)}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor={`status-${requestId}`}>Status</label>
                <select
                  id={`status-${requestId}`}
                  className="form-select"
                  value={status}
                  onChange={e => setStatus(e.target.value)}
                >
                  {STATUSES.map(s => (
                    <option key={s} value={s}>{s.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase())}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor={`tech-${requestId}`}>Assign Technician</label>
                <select
                  id={`tech-${requestId}`}
                  className="form-select"
                  value={techId}
                  onChange={e => setTechId(e.target.value)}
                >
                  <option value="">— Unassigned —</option>
                  {technicians.map(t => (
                    <option key={t.id} value={t.id}>{t.name} ({t.id}) — {t.assigned_count} open</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor={`notes-${requestId}`}>Notes</label>
                <textarea
                  id={`notes-${requestId}`}
                  className="form-textarea"
                  value={notes}
                  onChange={e => setNotes(e.target.value)}
                  placeholder="Add coordinator notes…"
                  maxLength={1000}
                />
              </div>

              {/* Duplicate candidates */}
              {dupCandidates.length > 0 && !req.is_duplicate && (
                <>
                  <hr className="divider" />
                  <div className="section-title" style={{ color: 'var(--color-duplicate)', marginBottom: 10 }}>
                    ⚠ Possible Duplicate Requests
                  </div>
                  {dupCandidates.map(c => (
                    <div key={c.id} className="dup-candidate">
                      <div className="dup-candidate__header">
                        <span className="dup-candidate__id">{c.id}</span>
                        <span className="tag">Same customer: {c.customer_id}</span>
                      </div>
                      <div className="dup-candidate__meta">
                        Shared keywords: {c.shared_keywords.join(', ')}
                      </div>
                      <div className="dup-candidate__snippet">"{c.message_snippet}…"</div>
                      <div className="dup-candidate__actions">
                        <button
                          className="btn btn-sm btn-danger"
                          onClick={() => handleMarkDuplicate(c.id)}
                          disabled={saving}
                          id={`mark-dup-${requestId}-${c.id}`}
                        >
                          Mark as duplicate of {c.id}
                        </button>
                      </div>
                    </div>
                  ))}
                </>
              )}

              {/* Notes from original seed */}
              {req.notes && (
                <>
                  <hr className="divider" />
                  <div className="section-title">Coordinator Notes</div>
                  <div style={{ fontSize: 13, color: 'var(--color-text-muted)', marginTop: 6 }}>
                    {req.notes}
                  </div>
                </>
              )}
            </>
          )}
        </div>

        {req && !loading && (
          <div className="modal-footer">
            <button className="btn btn-secondary" onClick={onClose}>Cancel</button>
            <button
              className="btn btn-primary"
              onClick={handleSave}
              disabled={saving}
              id={`save-${requestId}`}
            >
              {saving ? 'Saving…' : 'Save Changes'}
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
