import { useState } from 'react'
import './ChatScreen.css'
import './HistoryPanel.css'
import HistoryPanel from './HistoryPanel'

function ChatScreen() {
  const [message, setMessage] = useState('')
  const [showHistory, setShowHistory] = useState(false)
  const [messages, setMessages] = useState([])

  function handleSend(event) {
    event.preventDefault()

    const trimmedMessage = message.trim()

    if (!trimmedMessage) return

    const userMessage = {
      id: Date.now(),
      sender: 'user',
      text: trimmedMessage,
    }

    setMessages((currentMessages) => [
      ...currentMessages,
      userMessage,
    ])

    setMessage('')

    setTimeout(() => {
      const temporaryAIResponse = {
        id: Date.now() + 1,
        sender: 'ai',
        text: 'Thanks for sharing that. The live AI response will appear here once the backend connection is added.',
      }

      setMessages((currentMessages) => [
        ...currentMessages,
        temporaryAIResponse,
      ])
    }, 500)
  }

  function handleNewConversation() {
    setMessages([])
    setMessage('')
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
            <p className="chat-eyebrow">
              YOUR SUPPORT SPACE
            </p>

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
              </div>
            )}

            <form
              className="chat-input-area"
              onSubmit={handleSend}
            >
              <textarea
                value={message}
                onChange={(event) =>
                  setMessage(event.target.value)
                }
                placeholder="Share what’s on your mind..."
                rows="3"
              />

              <button
                type="submit"
                className="chat-send-button"
                disabled={!message.trim()}
              >
                Send
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
          <HistoryPanel
            onClose={() => setShowHistory(false)}
          />
        )}
      </div>
    </main>
  )
}

export default ChatScreen