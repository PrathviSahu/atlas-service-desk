import { priorityDot } from '../utils/formatters'

export default function PriorityBadge({ priority }) {
  const p = priority || 'normal'
  return (
    <span className={`badge badge-priority-${p}`}>
      {priorityDot(p)} {p.charAt(0).toUpperCase() + p.slice(1)}
    </span>
  )
}
