import { useState } from 'react'
import './App.css'

function App() {
  const [showPassword, setShowPassword] = useState(false)
  const [screen, setScreen] = useState('login')
  const [consentAccepted, setConsentAccepted] = useState(false)

  if (screen === 'chat') {
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
          <div className="login-card consent-card">
            <p className="eyebrow">YOUR SUPPORT SPACE</p>

            <h1>How are you feeling today?</h1>

            <p className="login-subtitle">
              You can use this space to reflect, talk through what is on your
              mind, or ask for support between therapy sessions.
            </p>

            <div className="consent-content">
              <div className="consent-item">
                <h3>Your conversation will appear here</h3>
                <p>
                  This is the beginning of your conversation. Once the AI
                  connection is added, messages between you and the support
                  assistant will appear in this area.
                </p>
              </div>
            </div>

            <button
              type="button"
              className="forgot-password"
              onClick={() => setScreen('reminder')}
            >
              Back
            </button>
          </div>
        </section>
      </main>
    )
  }

  if (screen === 'reminder') {
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
          <div className="login-card consent-card">
            <p className="eyebrow">BEFORE YOU START CHATTING</p>

            <h1>A Quick Reminder</h1>

            <p className="login-subtitle">
              This space is here to support you between therapy sessions.
            </p>

            <div className="consent-content">
              <div className="consent-item">
                <h3>Share only what feels comfortable</h3>
                <p>
                  You choose what you want to discuss. You do not have to share
                  anything you are not comfortable sharing.
                </p>
              </div>

              <div className="consent-item">
                <h3>Use this space for non-emergency support</h3>
                <p>
                  The AI can help with general reflection, coping strategies,
                  and supportive conversation, but it is not a replacement for
                  your therapist.
                </p>
              </div>

              <div className="consent-item">
                <h3>Your therapist remains part of your care</h3>
                <p>
                  Your assigned therapist may review your conversations and
                  remains the person responsible for clinical decisions and
                  follow-up.
                </p>
              </div>

              <div className="consent-item">
                <h3>Get immediate help during a crisis</h3>
                <p>
                  If you are in immediate danger or experiencing an emergency,
                  call 911 or go to the nearest emergency room. You can also
                  call or text 988 for crisis support.
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
          <div className="login-card consent-card">
            <p className="eyebrow">BEFORE YOU BEGIN</p>

            <h1>AI Disclosure and Consent</h1>

            <p className="login-subtitle">
              Please review this information before using the AI support chat.
            </p>

            <div className="consent-content">
              <div className="consent-item">
                <h3>This is an AI support tool</h3>
                <p>
                  The AI is not a therapist and does not replace care from your
                  licensed mental health professional.
                </p>
              </div>

              <div className="consent-item">
                <h3>It does not provide diagnosis or treatment</h3>
                <p>
                  The AI is designed to provide supportive conversation and
                  general wellness guidance. It does not diagnose conditions,
                  provide treatment, or make clinical decisions.
                </p>
              </div>

              <div className="consent-item">
                <h3>Your therapist may review your conversations</h3>
                <p>
                  Conversations are stored as part of this clinician-connected
                  experience. Your assigned therapist may review your
                  conversations when appropriate.
                </p>
              </div>

              <div className="consent-item">
                <h3>Safety concerns may be flagged</h3>
                <p>
                  Messages that may indicate a safety concern can be flagged
                  for review by your assigned therapist. The AI does not make
                  the final clinical decision.
                </p>
              </div>

              <div className="consent-item">
                <h3>This is not an emergency service</h3>
                <p>
                  If you are in immediate danger or experiencing an emergency,
                  call 911 or go to the nearest emergency room. You can also
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
                I have read and understand the information above, and I agree
                to use the clinician-connected AI support chat.
              </span>
            </label>

            <button
              type="button"
              className="sign-in-button"
              disabled={!consentAccepted}
              onClick={() => setScreen('reminder')}
            >
              Continue
            </button>

            <button
              type="button"
              className="forgot-password"
              onClick={() => {
                setConsentAccepted(false)
                setScreen('login')
              }}
            >
              Decline and Go Back
            </button>
          </div>
        </section>
      </main>
    )
  }

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

            <button
              type="button"
              className="sign-in-button"
              onClick={() => setScreen('consent')}
            >
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