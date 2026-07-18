export const statusConfig = {
  PENDING_MANAGER: {
    label: 'En attente',
    className: 'status-pending',
  },

  APPROVED: {
    label: 'Approuvée',
    className: 'status-approved',
  },

  REFUSED: {
    label: 'Refusée',
    className: 'status-rejected',
  },

  REJECTED: {
    label: 'Refusée',
    className: 'status-rejected',
  },

  GRANTED: {
    label: 'Accès attribué',
    className: 'status-active',
  },

  ACTIVE: {
    label: 'Actif',
    className: 'status-active',
  },

  REVOKED: {
    label: 'Révoqué',
    className: 'status-revoked',
  },

  INACTIVE: {
    label: 'Inactif',
    className: 'status-inactive',
  },
}

export function getStatusLabel(status) {
  return (
    statusConfig[status]?.label ||
    status ||
    'Statut inconnu'
  )
}

export function getStatusClass(status) {
  return (
    statusConfig[status]?.className ||
    'status-unknown'
  )
}