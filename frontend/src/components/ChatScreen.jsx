import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import './ChatScreen.css'
import './HistoryPanel.css'
import HistoryPanel from './HistoryPanel'

const API_URL = 'http://127.0.0.1:8000'

function ChatScreen({ onLogout }) {
  const [message, setMessage] = useState('')
  const [showHistory, setShowHistory] = useState(false)
  const [messages, setMessages] = useState([])
  const [chatId, setChatId] = useState(null)
  const [loading, setLoading] = useState(false)
  const [loadingConversation, setLoadingConversation] = useState(false)
  const [error, setError] = useState('')

  const hasConversation = messages.length > 0

  async function handleSend(event) {
    event.preventDefault()

    const trimmedMessage = message.trim()

    if (!trimmedMessage || loading || loadingConversation) return

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

    setMessages((current) => [...current, userMessage])
    setMessage('')

    try {
      let activeChatId = chatId

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

      const response = await fetch(
        `${API_URL}/chat/${activeChatId}/messages`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            content: trimmedMessage,
          }),
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
    } finally {
      setLoading(false)
    }
  }

  async function handleSelectConversation(selectedChatId) {
    if (loadingConversation) return

    const token = sessionStorage.getItem('access_token')

    if (!token) {
      setError('Your session has expired. Please log in again.')
      return
    }

    setError('')
    setLoadingConversation(true)

    try {
      const response = await fetch(
        `${API_URL}/chat/${selectedChatId}`,
        {
          method: 'GET',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        },
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          typeof data.detail === 'string'
            ? data.detail
            : 'Unable to load this conversation.',
        )
      }

      const loadedMessages = (data.messages ?? []).map(
        (savedMessage) => ({
          id: `saved-${savedMessage.id}`,
          sender: savedMessage.sender,
          text: savedMessage.content,
        }),
      )

      setChatId(data.id)
      setMessages(loadedMessages)
      setMessage('')
      setError('')
      setShowHistory(false)
    } catch (err) {
      setError(
        err instanceof TypeError
          ? 'Could not connect to the backend. Check that FastAPI is running on port 8000.'
          : err.message || 'Unable to load this conversation.',
      )
    } finally {
      setLoadingConversation(false)
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
          <div className="chat-logo-frame">
            <img
              src="/anchored-support-services-logo.png"
              alt="Anchored Support Services"
              className="chat-logo"
            />
          </div>

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
          {hasConversation && (
            <button
              type="button"
              className="chat-secondary-button"
              onClick={handleNewConversation}
              disabled={loading || loadingConversation}
            >
              New Conversation
            </button>
          )}

          <button
            type="button"
            className="chat-secondary-button"
            onClick={() => setShowHistory(true)}
            disabled={loadingConversation}
          >
            History
          </button>

          <button
            type="button"
            className="chat-secondary-button"
            onClick={onLogout}
          >
            Sign Out
          </button>
        </div>
      </header>

      <div className="chat-layout">
        <section
          className={
            hasConversation
              ? 'support-shell conversation-mode'
              : 'support-shell'
          }
        >
          {!hasConversation && (
            <div className="support-shell-heading">
              <p className="chat-eyebrow">
                YOUR SPACE
              </p>

              <h1>How are you feeling today?</h1>
            </div>
          )}

          {hasConversation && (
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
                  {chatMessage.sender === 'ai' && (
                    <div className="ai-avatar-frame">
                      <img
                        src="/anchored-support-services-logo.png"
                        alt="Anchored Support Services AI"
                        className="ai-avatar"
                      />
                    </div>
                  )}

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
                        : 'Anchored AI'}
                    </span>

                    {chatMessage.sender === 'user' ? (
                      <p>{chatMessage.text}</p>
                    ) : (
                      <div className="ai-message-content">
                        <ReactMarkdown>
                          {chatMessage.text}
                        </ReactMarkdown>
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {loading && (
                <div className="message-row ai-message-row">
                  <div className="ai-avatar-frame">
                    <img
                      src="/anchored-support-services-logo.png"
                      alt=""
                      aria-hidden="true"
                      className="ai-avatar"
                    />
                  </div>

                  <div
                    className="ai-thinking"
                    role="status"
                    aria-live="polite"
                  >
                    Anchored AI is preparing a response...
                  </div>
                </div>
              )}
            </div>
          )}

          {error && (
            <p
              className="chat-error"
              role="alert"
            >
              {error}
            </p>
          )}

          <form
            className={
              hasConversation
                ? 'chat-composer active-composer'
                : 'chat-composer welcome-composer'
            }
            onSubmit={handleSend}
          >
            <textarea
              value={message}
              onChange={(event) =>
                setMessage(event.target.value)
              }
              placeholder={
                hasConversation
                  ? 'Continue the conversation...'
                  : 'Share what’s on your mind...'
              }
              rows={hasConversation ? 3 : 4}
              disabled={loading || loadingConversation}
            />

            <button
              type="submit"
              className="chat-send-button"
              disabled={
                !message.trim() ||
                loading ||
                loadingConversation
              }
            >
              {loading ? 'Sending...' : 'Send'}
            </button>
          </form>

          <div className="support-safety">
            <strong>Need immediate help?</strong>

            <span>
              {' '}
              This AI tool is not an emergency service. Call 911 for an
              emergency or call or text 988 for crisis support.
            </span>
          </div>
        </section>

        {showHistory && (
          <HistoryPanel
            onClose={() => setShowHistory(false)}
            onSelectConversation={handleSelectConversation}
          />
        )}
      </div>
    </main>
  )
}

export default ChatScreen