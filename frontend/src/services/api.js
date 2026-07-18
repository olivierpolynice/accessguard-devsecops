const API_URL = 'http://localhost:8000'

const HTTP_ERROR_MESSAGES = {
  400: 'La demande envoyée est incorrecte.',
  401: 'Votre session a expiré. Veuillez vous reconnecter.',
  403: 'Vous n’avez pas l’autorisation nécessaire.',
  404: 'L’élément demandé est introuvable.',
  409: 'Cet élément existe déjà.',
  422: 'Certaines informations sont invalides.',
  500: 'Une erreur interne est survenue.',
}

export function getErrorMessage(status) {
  return (
    HTTP_ERROR_MESSAGES[status] ||
    'Une erreur inattendue est survenue.'
  )
}

async function readResponse(response) {
  const contentType =
    response.headers.get('content-type')

  if (contentType?.includes('application/json')) {
    return response.json()
  }

  return null
}

function getValidationDetails(data) {
  const detail = data?.detail

  if (!Array.isArray(detail)) {
    return ''
  }

  return detail
    .map((item) => {
      const field = Array.isArray(item.loc)
        ? item.loc
            .filter(
              (location) =>
                location !== 'body' &&
                location !== 'query' &&
                location !== 'path',
            )
            .join(' → ')
        : ''

      const message =
        item.msg || 'Valeur incorrecte'

      return field
        ? `${field} : ${message}`
        : message
    })
    .join(' | ')
}

function createHttpError(response, data) {
  const translatedMessage = getErrorMessage(
    response.status,
  )

  const validationDetails =
    response.status === 422
      ? getValidationDetails(data)
      : ''

  const error = new Error(
    validationDetails
      ? `${translatedMessage} ${validationDetails}`
      : translatedMessage,
  )

  error.status = response.status
  error.data = data

  return error
}

export async function loginUser(email, password) {
  let response

  try {
    response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email,
        password,
      }),
    })
  } catch {
    throw new Error(
      'Impossible de contacter le serveur. Vérifiez que l’API est démarrée.',
    )
  }

  const data = await readResponse(response)

  if (!response.ok) {
    throw createHttpError(response, data)
  }

  if (!data?.access_token) {
    throw new Error(
      'Le serveur n’a pas renvoyé de jeton de connexion.',
    )
  }

  return data
}

export async function apiRequest(
  path,
  options = {},
) {
  const token =
    localStorage.getItem('access_token')

  if (
    !token ||
    token === 'undefined' ||
    token === 'null'
  ) {
    localStorage.removeItem('access_token')
    localStorage.removeItem('token_type')

    const error = new Error(
      getErrorMessage(401),
    )

    error.status = 401

    throw error
  }

  const headers = new Headers(
    options.headers || {},
  )

  headers.set('Accept', 'application/json')
  headers.set(
    'Authorization',
    `Bearer ${token}`,
  )

  if (
    options.body !== undefined &&
    !(options.body instanceof FormData)
  ) {
    headers.set(
      'Content-Type',
      'application/json',
    )
  }

  let response

  try {
    response = await fetch(
      `${API_URL}${path}`,
      {
        ...options,
        headers,
      },
    )
  } catch {
    throw new Error(
      'Impossible de contacter le serveur. Vérifiez que l’API est démarrée.',
    )
  }

  const data = await readResponse(response)

  if (!response.ok) {
    if (response.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('token_type')
    }

    throw createHttpError(response, data)
  }

  return data
}

export function logoutUser() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('token_type')
}

export { API_URL }