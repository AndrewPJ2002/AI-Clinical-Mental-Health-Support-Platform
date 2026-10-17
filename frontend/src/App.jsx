import { useState } from 'react'
import './App.css'

function App() {
  const [showPassword, setShowPassword] = useState(false)

  return (
    <main className="app-page">
      <header className="brand-header">
        <button
          type="button"
          className="menu-button"
          aria-label="Open navigation"
        >
          <span></span>
          <span></span>
          <span></span>
        </button>

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
          <p className="eyebrow">PATIENT ACCESS</p>

          <h1>Welcome Back</h1>

          <p className="login-subtitle">
            Sign in to continue to your support space.
          </p>

          <form className="login-form">
            <label htmlFor="email">Email</label>

            <input
              id="email"
              type="email"
              placeholder="you@example.com"
            />

            <label htmlFor="password">Password</label>

            <div className="password-field">
              <input
                id="password"
                type={showPassword ? 'text' : 'password'}
                placeholder="Enter your password"
              />

              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowPassword(!showPassword)}
                aria-label={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? (
                  <svg viewBox="0 0 24 24" aria-hidden="true">
                    <path d="M3 3l18 18M10.6 10.6a2 2 0 002.8 2.8M9.9 4.2A10.8 10.8 0 0112 4c5.5 0 9 5 9 5a17.5 17.5 0 01-3.1 3.5M6.2 6.2C4.2 7.5 3 9 3 9s3.5 5 9 5c1.3 0 2.5-.3 3.6-.7" />
                  </svg>
                ) : (
                  <svg viewBox="0 0 24 24" aria-hidden="true">
                    <path d="M3 12s3.5-5 9-5 9 5 9 5-3.5 5-9 5-9-5-9-5z" />
                    <circle cx="12" cy="12" r="2.5" />
                  </svg>
                )}
              </button>
            </div>

            <button type="button" className="sign-in-button">
              Sign In
            </button>
          </form>

          <button type="button" className="forgot-password">
            Forgot password?
          </button>

          <p className="account-prompt">
            Don't have an account?
          </p>

          <button type="button" className="create-account">
            Create Account
          </button>
        </div>
      </section>
    </main>
  )
}

export default App