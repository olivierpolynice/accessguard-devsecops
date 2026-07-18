import './Monitoring.css'

const monitoringServices = [
  {
    name: 'Grafana',
    description:
      'Consultez les tableaux de bord et visualisez les métriques AccessGuard.',
    url: 'http://localhost:3000',
    buttonLabel: 'Ouvrir Grafana',
    className: 'grafana',
  },
  {
    name: 'Prometheus',
    description:
      'Interrogez les métriques collectées et vérifiez l’état des services.',
    url: 'http://localhost:9090',
    buttonLabel: 'Ouvrir Prometheus',
    className: 'prometheus',
  },
  {
    name: 'Métriques de l’API',
    description:
      'Consultez directement les métriques exposées par l’API AccessGuard.',
    url: 'http://localhost:8000/metrics',
    buttonLabel: 'Voir les métriques',
    className: 'metrics',
  },
  {
    name: 'État de l’API',
    description:
      'Vérifiez que l’API AccessGuard est démarrée et opérationnelle.',
    url: 'http://localhost:8000/health',
    buttonLabel: 'Vérifier l’API',
    className: 'health',
  },
]

function Monitoring() {
  return (
    <section className="page monitoring-page">
      <div className="monitoring-header">
        <div>
          <p className="monitoring-eyebrow">
            ADMINISTRATEUR SÉCURITÉ
          </p>

          <h1>Supervision</h1>

          <p className="monitoring-description">
            Accédez aux outils Grafana et Prometheus pour
            surveiller AccessGuard.
          </p>
        </div>
      </div>

      <div className="monitoring-grid">
        {monitoringServices.map((service) => (
          <article
            className={`monitoring-card ${service.className}`}
            key={service.name}
          >
            <div className="monitoring-status">
              <span
                className="monitoring-status-dot"
                aria-hidden="true"
              />

              Service de supervision
            </div>

            <h2>{service.name}</h2>

            <p>{service.description}</p>

            <a
              className="monitoring-link"
              href={service.url}
              target="_blank"
              rel="noopener noreferrer"
            >
              {service.buttonLabel}
            </a>
          </article>
        ))}
      </div>

      <aside className="monitoring-information">
        <h2>Informations</h2>

        <p>
          Les services de supervision doivent être démarrés
          avec Docker Compose. Si un lien ne fonctionne pas,
          vérifiez l’état des conteneurs.
        </p>

        <code>docker compose ps</code>
      </aside>
    </section>
  )
}

export default Monitoring