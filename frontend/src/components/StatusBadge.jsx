import { statusLabel } from '../utils/formatters'

export default function StatusBadge({ status }) {
  const s = status || 'open'
  return (
    <span className={`badge badge-status-${s}`}>
      {statusLabel(s)}
    </span>
  )
}
