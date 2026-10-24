
import { useState } from 'react'
import './ChatScreen.css'
import './HistoryPanel.css'
import HistoryPanel from './HistoryPanel'

const API_URL = 'http://127.0.0.1:8000'

function ChatScreen() {
  const [message, setMessage] = useState('')
  const [showHistory, setShowHistory] = useState(false)
  const [messages, setMessages] = useState([])
  const [chatId, setChatId] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleSend(event) {
    event.preventDefault()

    const trimmedMessage = message.trim()
    if (!trimmedMessage || loading) return

    const token = sessionStorage.getItem('access_token')

    if (!token) {
      setError('Your session has expired. Please log in again.')
      return
    }

    setError('')
    setLoading(true)

    const userMessage = {
      id: `user-${Date.now()}`,
      sender: 'user',
      text: trimmedMessage,
    }

    // Show the patient's message immediately.
    setMessages((current) => [...current, userMessage])
    setMessage('')

    try {
      let activeChatId = chatId

      // Create a conversation the first time the patient sends a message.
      if (activeChatId === null) {
        const createResponse = await fetch(`${API_URL}/chat`, {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })

        const createData = await createResponse.json()

        if (!createResponse.ok) {
          throw new Error(
            typeof createData.detail === 'string'
              ? createData.detail
              : 'Unable to start a conversation.',
          )
        }

        activeChatId = createData.id
        setChatId(activeChatId)
      }

      // Send the message to the authenticated backend.
      const response = await fetch(
        `${API_URL}/chat/${activeChatId}/messages`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ content: trimmedMessage }),
        },
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          typeof data.detail === 'string'
            ? data.detail
            : 'Unable to send your message. Please try again.',
        )
      }

      setMessages((current) => [
        ...current,
        {
          id: `assistant-${Date.now()}`,
          sender: 'ai',
          text: data.assistant_message,
        },
      ])
    } catch (err) {
      setError(
        err instanceof TypeError
          ? 'Could not connect to the backend. Check that FastAPI is running on port 8000.'
          : err.message || 'Something went wrong. Please try again.',
      )

      // Keep the patient's message visible so it isn't lost.
    } finally {
      setLoading(false)
    }
  }

  function handleNewConversation() {
    setMessages([])
    setMessage('')
    setChatId(null)
    setError('')
    setShowHistory(false)
  }

  return (
    <main className="chat-page">
      <header className="chat-header">
        <div className="chat-brand">
          <img
            src="/anchored-support-services-logo.png"
            alt="Anchored Support Services"
            className="chat-logo"
          />

          <div>
            <p className="chat-brand-name">
              Anchored Support Services
            </p>
            <p className="chat-brand-subtitle">
              Clinician-Connected AI Support
            </p>
          </div>
        </div>

        <div className="chat-header-actions">
          {messages.length > 0 && (
            <button
              type="button"
              className="chat-secondary-button"
              onClick={handleNewConversation}
              disabled={loading}
            >
              New Conversation
            </button>
          )}

          <button
            type="button"
            className="chat-secondary-button"
            onClick={() => setShowHistory(true)}
          >
            History
          </button>
        </div>
      </header>

      <div className="chat-layout">
        <section className="chat-workspace">
          <div className="chat-intro">
            <p className="chat-eyebrow">YOUR SUPPORT SPACE</p>
            <h1>How are you feeling today?</h1>
            <p>
              Welcome back. Start a new conversation or continue
              one from your history.
            </p>
          </div>

          <div className="chat-window">
            {messages.length === 0 ? (
              <div className="chat-empty-state">
                <p>
                  When you are ready, share what is on your mind.
                </p>
              </div>
            ) : (
              <div className="message-list">
                {messages.map((chatMessage) => (
                  <div
                    key={chatMessage.id}
                    className={
                      chatMessage.sender === 'user'
                        ? 'message-row user-message-row'
                        : 'message-row ai-message-row'
                    }
                  >
                    <div
                      className={
                        chatMessage.sender === 'user'
                          ? 'message-bubble user-message'
                          : 'message-bubble ai-message'
                      }
                    >
                      <span className="message-label">
                        {chatMessage.sender === 'user'
                          ? 'You'
                          : 'AI Support'}
                      </span>
                      <p>{chatMessage.text}</p>
                    </div>
                  </div>
                ))}

                {loading && (
                  <p role="status" aria-live="polite">
                    AI Support is preparing a response...
                  </p>
                )}
              </div>
            )}

            {error && (
              <p className="chat-error" role="alert">
                {error}
              </p>
            )}

            <form className="chat-input-area" onSubmit={handleSend}>
              <textarea
                value={message}
                onChange={(event) => setMessage(event.target.value)}
                placeholder="Share what’s on your mind..."
                rows="3"
                disabled={loading}
              />

              <button
                type="submit"
                className="chat-send-button"
                disabled={!message.trim() || loading}
              >
                {loading ? 'Sending...' : 'Send'}
              </button>
            </form>
          </div>

          <div className="chat-safety-note">
            <strong>Need immediate help?</strong>
            <span>
              {' '}
              This AI support tool is not an emergency service.
              Call 911 for an emergency or call or text 988 for
              crisis support.
            </span>
          </div>
        </section>

        {showHistory && (
          <HistoryPanel onClose={() => setShowHistory(false)} />
        )}
      </div>
    </main>
  )
}

export default ChatScreen
