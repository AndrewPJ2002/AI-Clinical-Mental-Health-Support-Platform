import { useEffect, useState } from 'react'

const API_URL = 'http://127.0.0.1:8000'

function HistoryPanel({ onClose, onSelectConversation }) {
  const [conversations, setConversations] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    async function loadConversations() {
      const token = sessionStorage.getItem('access_token')

      if (!token) {
        setError('Your session has expired. Please sign in again.')
        setLoading(false)
        return
      }

      try {
        const response = await fetch(`${API_URL}/chat`, {
          method: 'GET',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })

        const data = await response.json()

        if (!response.ok) {
          throw new Error(
            typeof data.detail === 'string'
              ? data.detail
              : 'Unable to load conversation history.',
          )
        }

        setConversations(data.conversations ?? [])
      } catch (err) {
        setError(
          err instanceof TypeError
            ? 'Could not connect to the backend.'
            : err.message || 'Unable to load conversation history.',
        )
      } finally {
        setLoading(false)
      }
    }

    loadConversations()
  }, [])

  function formatDate(dateValue) {
    if (!dateValue) {
      return ''
    }

    const date = new Date(dateValue)

    return date.toLocaleDateString('en-US', {
      month: 'long',
      day: 'numeric',
      year: 'numeric',
    })
  }

  return (
    <aside className="history-panel">
      <div className="history-header">
        <div>
          <p className="history-eyebrow">
            CONVERSATION HISTORY
          </p>

          <h2>Your Conversations</h2>
        </div>

        <button
          type="button"
          className="history-close-button"
          onClick={onClose}
          aria-label="Close conversation history"
        >
          ×
        </button>
      </div>

      <p className="history-description">
        Select a previous conversation to review it.
      </p>

      {loading && (
        <p className="history-description">
          Loading conversations...
        </p>
      )}

      {!loading && error && (
        <p className="history-description">
          {error}
        </p>
      )}

      {!loading && !error && conversations.length === 0 && (
        <p className="history-description">
          You do not have any previous conversations yet.
        </p>
      )}

      {!loading && !error && conversations.length > 0 && (
        <div className="history-list">
          {conversations.map((conversation) => (
            <button
              key={conversation.id}
              type="button"
              className="history-item"
              onClick={() =>
                onSelectConversation?.(conversation.id)
              }
            >
              <span className="history-date">
                {formatDate(conversation.started_at)}
              </span>

              <strong>
                {conversation.title}
              </strong>

              <span className="history-preview">
                {conversation.preview}
              </span>
            </button>
          ))}
        </div>
      )}
    </aside>
  )
}

export default HistoryPanel