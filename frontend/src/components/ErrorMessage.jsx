function ErrorMessage({ message, onRetry }) {
  if (!message) {
    return null
  }

  return (
    <div className="error-message" role="alert">
      <p>{message}</p>

      {onRetry && (
        <button type="button" onClick={onRetry}>
          Réessayer
        </button>
      )}
    </div>
  )
}

export default ErrorMessage