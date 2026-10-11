import React from 'react';

function LotusIcon() {
  return (
    <svg className="lotus-icon" viewBox="0 0 220 120" aria-label="Anchored Support logo" role="img">
      <g fill="none" stroke="#1b5ea8" strokeWidth="3.6" strokeLinecap="round" strokeLinejoin="round">
        <path d="M110 20C88 44 82 58 88 78C95 89 104 95 110 96C116 95 125 89 132 78C138 58 132 44 110 20Z"/>
        <path d="M110 26C92 34 81 45 76 64C71 80 77 92 90 98C99 90 105 79 111 66C116 78 124 90 134 98C147 92 153 80 148 64C143 45 132 34 110 26Z"/>
        <path d="M110 34C100 48 96 59 96 72C96 85 102 94 110 100C118 94 124 85 124 72C124 59 120 48 110 34Z"/>
        <path d="M76 66C58 62 44 69 32 86C45 95 61 98 75 95C74 84 73 75 76 66Z"/>
        <path d="M144 66C162 62 176 69 188 86C175 95 159 98 145 95C146 84 147 75 144 66Z"/>
        <path d="M92 78C74 86 59 101 52 116C72 120 90 114 100 101C99 93 96 86 92 78Z"/>
        <path d="M128 78C146 86 161 101 168 116C148 120 130 114 120 101C121 93 124 86 128 78Z"/>
      </g>
      <circle cx="110" cy="70" r="7" fill="none" stroke="#1b5ea8" strokeWidth="3.6"/>
    </svg>
  );
}

function ChatIcon() {
  return (
    <svg className="feature-icon" viewBox="0 0 64 64" aria-hidden="true">
      <g fill="none" stroke="currentColor" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M18 18h28a6 6 0 0 1 6 6v14a6 6 0 0 1-6 6H38l-8 8v-8H18a6 6 0 0 1-6-6V24a6 6 0 0 1 6-6Z"/>
        <circle cx="24" cy="31" r="2.5" fill="currentColor" stroke="none"/>
        <circle cx="32" cy="31" r="2.5" fill="currentColor" stroke="none"/>
        <circle cx="40" cy="31" r="2.5" fill="currentColor" stroke="none"/>
      </g>
    </svg>
  );
}

function ReviewIcon() {
  return (
    <svg className="feature-icon" viewBox="0 0 64 64" aria-hidden="true">
      <g fill="none" stroke="currentColor" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="31" cy="21" r="9"/>
        <path d="M17 47c3-8 10-12 14-12s11 4 14 12"/>
        <path d="M41 23l6 6M47 23l-6 6"/>
      </g>
    </svg>
  );
}

function SecurityIcon() {
  return (
    <svg className="feature-icon" viewBox="0 0 64 64" aria-hidden="true">
      <g fill="none" stroke="currentColor" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M32 14l16 6v12c0 10-6 18-16 22-10-4-16-12-16-22V20l16-6Z"/>
        <path d="M27 33l4 4 8-10"/>
      </g>
    </svg>
  );
}

export default function LoginPage() {
  return (
    <main className="login-page">
      <div className="login-shell">
        <div className="lotus-wrap">
          <LotusIcon />
        </div>

        <h1 className="title">
          <span className="title-line">Welcome to</span>
          <span className="title-line">Anchored Support</span>
        </h1>

        <p className="subtitle">
          AI chat with clinician oversight for support between sessions.
        </p>

        <div className="actions" aria-label="Authentication options">
          <a href="#!" className="action-btn">
            Sign In
          </a>
          <a href="#!" className="action-btn secondary">
            Create Account
          </a>
        </div>

        <div className="feature-grid">
          <div className="feature">
            <div className="feature-icon-wrap">
              <ChatIcon />
            </div>
            <p className="feature-copy">Get support and guidance between sessions.</p>
          </div>

          <div className="feature">
            <div className="feature-icon-wrap">
              <ReviewIcon />
            </div>
            <p className="feature-copy">Your therapist can review conversations if needed.</p>
          </div>

          <div className="feature">
            <div className="feature-icon-wrap">
              <SecurityIcon />
            </div>
            <p className="feature-copy">Your information is private and secure.</p>
          </div>
        </div>
      </div>
    </main>
  );
}
