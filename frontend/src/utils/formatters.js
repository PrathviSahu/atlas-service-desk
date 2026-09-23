export function formatDateTime(iso) {
  if (!iso) return '—'
  const d = new Date(iso)
  return d.toLocaleString('en-GB', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

export function formatRelative(iso) {
  if (!iso) return '—'
  const now = new Date('2026-10-01T09:00:00') // fictional clock
  const then = new Date(iso)
  const diffMs = now - then
  const diffHrs = diffMs / (1000 * 60 * 60)
  if (diffHrs < 1) return `${Math.round(diffMs / 60000)}m ago`
  if (diffHrs < 24) return `${Math.round(diffHrs)}h ago`
  return `${Math.round(diffHrs / 24)}d ago`
}

export function priorityDot(priority) {
  const map = {
    urgent: '🔴',
    high: '🟠',
    normal: '🟢',
    low: '⚪',
  }
  return map[priority] || '⚪'
}

export function statusLabel(status) {
  const map = {
    open: 'Open',
    assigned: 'Assigned',
    in_progress: 'In Progress',
    waiting: 'Waiting',
    resolved: 'Resolved',
    closed: 'Closed',
  }
  return map[status] || status
}

export function channelIcon(channel) {
  const map = {
    email: '✉',
    whatsapp: '💬',
    phone: '📞',
  }
  return map[channel] || '?'
}

export function initials(name) {
  if (!name) return '?'
  return name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2)
}
