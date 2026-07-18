import {
  getStatusClass,
  getStatusLabel,
} from '../utils/status'
import './StatusBadge.css'

function StatusBadge({
  status,
  label,
  className = '',
}) {
  const statusClass = getStatusClass(status)
  const statusLabel =
    label || getStatusLabel(status)

  return (
    <span
      className={`status-badge ${statusClass} ${className}`.trim()}
    >
      {statusLabel}
    </span>
  )
}

export default StatusBadge