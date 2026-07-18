import './ConfirmDialog.css'

function ConfirmDialog({
  isOpen,
  title,
  message,
  confirmLabel = 'Confirmer',
  cancelLabel = 'Annuler',
  confirmVariant = 'danger',
  loading = false,
  onConfirm,
  onCancel,
}) {
  if (!isOpen) {
    return null
  }

  return (
    <div
      className="confirm-dialog-overlay"
      role="presentation"
      onMouseDown={(event) => {
        if (
          event.target === event.currentTarget &&
          !loading
        ) {
          onCancel()
        }
      }}
    >
      <section
        className="confirm-dialog"
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="confirm-dialog-title"
        aria-describedby="confirm-dialog-message"
      >
        <div className="confirm-dialog-icon">
          !
        </div>

        <h2 id="confirm-dialog-title">
          {title}
        </h2>

        <p id="confirm-dialog-message">
          {message}
        </p>

        <div className="confirm-dialog-actions">
          <button
            type="button"
            className="confirm-dialog-cancel"
            onClick={onCancel}
            disabled={loading}
          >
            {cancelLabel}
          </button>

          <button
            type="button"
            className={`confirm-dialog-confirm confirm-${confirmVariant}`}
            onClick={onConfirm}
            disabled={loading}
          >
            {loading
              ? 'Traitement...'
              : confirmLabel}
          </button>
        </div>
      </section>
    </div>
  )
}

export default ConfirmDialog