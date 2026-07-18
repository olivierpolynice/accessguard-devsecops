import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { loginUser } from '../services/api'
import ErrorMessage from '../components/ErrorMessage'
import LoadingSpinner from '../components/LoadingSpinner'

function Login() {
  const navigate = useNavigate()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()

    setError('')
    setIsLoading(true)

    try {
      const data = await loginUser(
        email.trim().toLowerCase(),
        password,
      )

      if (!data?.access_token) {
        throw new Error(
          'Le serveur n’a pas renvoyé de token d’accès.',
        )
      }

      localStorage.setItem(
        'access_token',
        data.access_token,
      )

      localStorage.setItem(
        'token_type',
        data.token_type || 'bearer',
      )

      navigate('/dashboard', {
        replace: true,
      })
    } catch (loginError) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('token_type')

      setError(
        loginError.message ||
          'Impossible de vous connecter.',
      )
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <main className="login-page">
      <section className="login-card">
        <div className="login-brand">
          <h1>AccessGuard</h1>
          <p>Gestion sécurisée des accès</p>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="email">
              Adresse email
            </label>

            <input
              id="email"
              type="email"
              value={email}
              onChange={(event) =>
                setEmail(event.target.value)
              }
              placeholder="utilisateur@asteriatech.local"
              autoComplete="email"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">
              Mot de passe
            </label>

            <input
              id="password"
              type="password"
              value={password}
              onChange={(event) =>
                setPassword(event.target.value)
              }
              placeholder="Votre mot de passe"
              autoComplete="current-password"
              required
            />
          </div>

          <ErrorMessage message={error} />

          <button
            className="login-button"
            type="submit"
            disabled={isLoading}
          >
            {isLoading
              ? 'Connexion...'
              : 'Se connecter'}
          </button>

          {isLoading && (
            <LoadingSpinner message="Vérification du compte..." />
          )}
        </form>
      </section>
    </main>
  )
}

export default Login