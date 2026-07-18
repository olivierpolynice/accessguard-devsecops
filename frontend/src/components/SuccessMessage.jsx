import { useEffect } from 'react'
import './SuccessMessage.css'

function SuccessMessage({
  message,
  onClose,
  duration = 4000,
}) {
  useEffect(() => {
    if (!message || !onClose) {
      return undefined
    }

    const timeoutId = window.setTimeout(() => {
      onClose()
    }, duration)

    return () => {
      window.clearTimeout(timeoutId)
    }
  }, [message, duration, onClose])

  if (!message) {
    return null
  }

  return (
    <div
      className="success-alert"
      role="status"
      aria-live="polite"
    >
      <span
        className="success-alert-icon"
        aria-hidden="true"
      >
        ✓
      </span>

      <p>{message}</p>

      {onClose && (
        <button
          type="button"
          className="success-alert-close"
          onClick={onClose}
          aria-label="Fermer le message"
        >
          ×
        </button>
      )}
    </div>
  )
}

export default SuccessMessage