function HistoryPanel({ onClose }) {
  const conversations = [
    {
      id: 1,
      date: 'October 18, 2026',
      title: 'Feeling overwhelmed',
      preview:
        'I have been feeling overwhelmed lately and wanted to talk through it.',
    },
    {
      id: 2,
      date: 'October 15, 2026',
      title: 'Work stress',
      preview:
        'Today was stressful at work and I needed a place to process everything.',
    },
    {
      id: 3,
      date: 'October 11, 2026',
      title: 'Trouble sleeping',
      preview:
        'I have had a hard time falling asleep this week and wanted some ideas.',
    },
  ]

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

      <div className="history-list">
        {conversations.map((conversation) => (
          <button
            key={conversation.id}
            type="button"
            className="history-item"
          >
            <span className="history-date">
              {conversation.date}
            </span>

            <strong>{conversation.title}</strong>

            <span className="history-preview">
              {conversation.preview}
            </span>
          </button>
        ))}
      </div>
    </aside>
  )
}

export default HistoryPanel