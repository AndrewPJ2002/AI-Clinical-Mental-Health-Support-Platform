import { useState } from 'react'
import './App.css'
import ChatScreen from './components/ChatScreen'

const API_URL = 'http://127.0.0.1:8000'

function App() {
  const [screen, setScreen] = useState('login')
  const [showPassword, setShowPassword] = useState(false)
  const [consentAccepted, setConsentAccepted] = useState(false)
  const [isRegistering, setIsRegistering] = useState(false)
  const [firstName, setFirstName] = useState('')
  const [lastName, setLastName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleConsentContinue() {
    const token = sessionStorage.getItem('access_token')

    if (!token) {
      alert('Please log in again.')
      setScreen('login')
      return
    }

    try {
      const response = await fetch(`${API_URL}/consent/acknowledge`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          disclosure_version: 'v1',
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Unable to save consent.')
      }

      console.log('Consent saved:', data)
      setScreen('chat')
    } catch (error) {
      console.error('Consent save failed:', error)
      alert(error.message || 'Unable to save consent. Please try again.')
    }
  }

  function resetMessages() {
    setError('')
    setLoading(false)
  }

  async function handleAuth(event) {
    event.preventDefault()
    setError('')

    if (isRegistering && password.length < 12) {
      setError('Your password must contain at least 12 characters.')
      return
    }

    setLoading(true)

    try {
      const endpoint = isRegistering ? '/auth/register' : '/auth/login'

      const payload = isRegistering
        ? {
            first_name: firstName.trim(),
            last_name: lastName.trim(),
            email: email.trim(),
            password,
          }
        : {
            email: email.trim(),
            password,
          }

      const response = await fetch(`${API_URL}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      })

      const data = await response.json()

      if (!response.ok) {
        const detail = data.detail

        throw new Error(
          typeof detail === 'string'
            ? detail
            : 'Please check your information and try again.',
        )
      }

      if (isRegistering) {
        setIsRegistering(false)
        setPassword('')
        setError('')
        setScreen('login')

        alert('Account created! Please sign in with your new credentials.')
      } else {
        sessionStorage.setItem('access_token', data.access_token)

        try {
          const consentResponse = await fetch(`${API_URL}/consent/status`, {
            method: 'GET',
            headers: {
              Authorization: `Bearer ${data.access_token}`,
            },
          })

          if (!consentResponse.ok) {
            throw new Error('Could not check your consent status.')
          }

          const consentData = await consentResponse.json()

          if (consentData.required) {
            setConsentAccepted(false)
            setScreen('consent')
          } else {
            setConsentAccepted(false)
            setScreen('chat')
          }
        } catch (error) {
          console.error('Consent status check failed:', error)
          alert('We could not verify your consent. Please try again.')
        }
      }
    } catch (err) {
      setError(
        err instanceof TypeError
          ? 'Could not connect to the backend. Check that FastAPI is running on port 8000.'
          : err.message,
      )
    } finally {
      setLoading(false)
    }
  }

  function logout() {
    sessionStorage.removeItem('access_token')

    setConsentAccepted(false)
    setPassword('')
    setError('')
    setScreen('login')
  }

  if (screen === 'chat') {
    return <ChatScreen />
  }

  if (screen === 'reminder') {
    return (
      <main className="app-page">
        <header className="brand-header">
          <h2 className="brand-name">
            Anchored Support Services
          </h2>

          <img
            src="/anchored-support-services-banner.png"
            alt="Anchored Support Services"
            className="brand-banner"
          />

          <p className="brand-tagline">
            Anchor Yourself in Healing and Community.
          </p>
        </header>

        <section className="login-section">
          <div className="login-card consent-card">
            <p className="eyebrow">
              BEFORE YOU START CHATTING
            </p>

            <h1>A Quick Reminder</h1>

            <p className="login-subtitle">
              This space is here to support you between therapy sessions.
            </p>

            <div className="consent-content">
              <div className="consent-item">
                <h3>Share only what feels comfortable</h3>

                <p>
                  You choose what you want to discuss. You do not have to
                  share anything you are not comfortable sharing.
                </p>
              </div>

              <div className="consent-item">
                <h3>Use this space for non-emergency support</h3>

                <p>
                  The AI can help with general reflection and coping
                  strategies, but it is not a replacement for your therapist.
                </p>
              </div>

              <div className="consent-item">
                <h3>Your therapist remains part of your care</h3>

                <p>
                  Your assigned therapist may review conversations when
                  appropriate and remains responsible for clinical decisions.
                </p>
              </div>

              <div className="consent-item">
                <h3>Get immediate help during a crisis</h3>

                <p>
                  If you are in immediate danger, call 911. In the US, call
                  or text 988 for crisis support.
                </p>
              </div>
            </div>

            <button
              type="button"
              className="sign-in-button"
              onClick={() => setScreen('chat')}
            >
              Start Chat
            </button>

            <button
              type="button"
              className="forgot-password"
              onClick={() => setScreen('consent')}
            >
              Back to Consent
            </button>
          </div>
        </section>
      </main>
    )
  }

  if (screen === 'consent') {
    return (
      <main className="app-page">
        <header className="brand-header">
          <h2 className="brand-name">
            Anchored Support Services
          </h2>

          <img
            src="/anchored-support-services-banner.png"
            alt="Anchored Support Services"
            className="brand-banner"
          />

          <p className="brand-tagline">
            Anchor Yourself in Healing and Community.
          </p>
        </header>

        <section className="login-section">
          <div className="login-card consent-card">
            <p className="eyebrow">
              BEFORE YOU BEGIN
            </p>

            <h1>AI Disclosure and Consent</h1>

            <p className="login-subtitle">
              Please review this information before using the AI support chat.
            </p>

            <div className="consent-content">
              <div className="consent-item">
                <h3>This is an AI support tool</h3>

                <p>
                  The AI is not a therapist and does not replace care from
                  your licensed mental health professional.
                </p>
              </div>

              <div className="consent-item">
                <h3>It does not provide diagnosis or treatment</h3>

                <p>
                  The AI provides supportive conversation and general
                  wellness guidance, not diagnosis, treatment, or clinical
                  decisions.
                </p>
              </div>

              <div className="consent-item">
                <h3>Your therapist may review your conversations</h3>

                <p>
                  Conversations may be stored as part of this
                  clinician-connected experience and reviewed by your
                  assigned therapist when appropriate.
                </p>
              </div>

              <div className="consent-item">
                <h3>Safety concerns may be flagged</h3>

                <p>
                  Messages indicating possible safety concerns may be
                  flagged for therapist review.
                </p>
              </div>

              <div className="consent-item">
                <h3>This is not an emergency service</h3>

                <p>
                  If you are in immediate danger, call 911. In the US,
                  call or text 988 for crisis support.
                </p>
              </div>
            </div>

            <label className="consent-checkbox">
              <input
                type="checkbox"
                checked={consentAccepted}
                onChange={(event) =>
                  setConsentAccepted(event.target.checked)
                }
              />

              <span>
                I have read and understand the information above, and I
                agree to use the clinician-connected AI support chat.
              </span>
            </label>

            <button
              type="button"
              className="sign-in-button"
              disabled={!consentAccepted}
              onClick={handleConsentContinue}
            >
              Continue
            </button>

            <button
              type="button"
              className="forgot-password"
              onClick={logout}
            >
              Sign Out
            </button>
          </div>
        </section>
      </main>
    )
  }

  return (
    <main className="app-page">
      <header className="brand-header">
        <h2 className="brand-name">
          Anchored Support Services
        </h2>

        <img
          src="/anchored-support-services-banner.png"
          alt="Anchored Support Services"
          className="brand-banner"
        />

        <p className="brand-tagline">
          Anchor Yourself in Healing and Community.
        </p>
      </header>

      <section className="login-section">
        <div className="login-card">
          <p className="eyebrow">
            PATIENT ACCESS
          </p>

          <h1>
            {isRegistering
              ? 'Create Your Account'
              : 'Welcome Back'}
          </h1>

          <p className="login-subtitle">
            {isRegistering
              ? 'Create an account to access your support space.'
              : 'Sign in to continue to your support space.'}
          </p>

          <form
            className="login-form"
            onSubmit={handleAuth}
          >
            {isRegistering && (
              <>
                <label htmlFor="firstName">
                  First name
                </label>

                <input
                  id="firstName"
                  type="text"
                  autoComplete="given-name"
                  value={firstName}
                  onChange={(event) =>
                    setFirstName(event.target.value)
                  }
                  required
                />

                <label htmlFor="lastName">
                  Last name
                </label>

                <input
                  id="lastName"
                  type="text"
                  autoComplete="family-name"
                  value={lastName}
                  onChange={(event) =>
                    setLastName(event.target.value)
                  }
                  required
                />
              </>
            )}

            <label htmlFor="email">
              Email
            </label>

            <input
              id="email"
              type="email"
              autoComplete="email"
              placeholder="you@example.com"
              value={email}
              onChange={(event) =>
                setEmail(event.target.value)
              }
              required
            />

            <label htmlFor="password">
              Password
            </label>

            <div className="password-field">
              <input
                id="password"
                type={showPassword ? 'text' : 'password'}
                autoComplete={
                  isRegistering
                    ? 'new-password'
                    : 'current-password'
                }
                placeholder={
                  isRegistering
                    ? 'At least 12 characters'
                    : 'Enter your password'
                }
                value={password}
                onChange={(event) =>
                  setPassword(event.target.value)
                }
                required
                minLength={isRegistering ? 12 : 1}
              />

              <button
                type="button"
                className="password-toggle"
                onClick={() =>
                  setShowPassword(!showPassword)
                }
                aria-label={
                  showPassword
                    ? 'Hide password'
                    : 'Show password'
                }
                title={
                  showPassword
                    ? 'Hide password'
                    : 'Show password'
                }
              >
                {showPassword ? (
                  <svg
                    viewBox="0 0 24 24"
                    aria-hidden="true"
                  >
                    <path d="M3 3l18 18" />
                    <path d="M10.6 10.6a2 2 0 0 0 2.8 2.8" />
                    <path d="M9.9 4.2A10.8 10.8 0 0 1 12 4c5.5 0 9 5 9 8a9.8 9.8 0 0 1-2.1 3.8" />
                    <path d="M6.6 6.6C4.4 8 3 10.2 3 12c0 3 3.5 8 9 8 1.6 0 3-.4 4.2-1" />
                  </svg>
                ) : (
                  <svg
                    viewBox="0 0 24 24"
                    aria-hidden="true"
                  >
                    <path d="M2.5 12s3.5-7 9.5-7 9.5 7 9.5 7-3.5 7-9.5 7-9.5-7-9.5-7z" />
                    <circle cx="12" cy="12" r="2.5" />
                  </svg>
                )}
              </button>
            </div>

            {error && (
              <p
                className="auth-error"
                role="alert"
              >
                {error}
              </p>
            )}

            <button
              type="submit"
              className="sign-in-button"
              disabled={loading}
            >
              {loading
                ? 'Please wait...'
                : isRegistering
                  ? 'Create Account'
                  : 'Sign In'}
            </button>
          </form>

          {!isRegistering && (
            <button
              type="button"
              className="forgot-password"
              onClick={() =>
                setError(
                  'Password reset is not implemented yet.',
                )
              }
            >
              Forgot password?
            </button>
          )}

          <p className="account-prompt">
            {isRegistering
              ? 'Already have an account?'
              : "Don't have an account?"}
          </p>

          <button
            type="button"
            className="create-account"
            onClick={() => {
              setIsRegistering(!isRegistering)
              resetMessages()
              setPassword('')
            }}
          >
            {isRegistering
              ? 'Sign In'
              : 'Create Account'}
          </button>
        </div>
      </section>
    </main>
  )
}

export default App