function LoadingSpinner({ message = 'Chargement en cours...' }) {
  return (
    <div className="loading-spinner" role="status">
      <div className="spinner" aria-hidden="true" />
      <p>{message}</p>
    </div>
  )
}

export default LoadingSpinner