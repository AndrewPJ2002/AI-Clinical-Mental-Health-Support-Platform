import { useEffect, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import './TherapistDashboard.css'


const API_URL = 'http://127.0.0.1:8000'


function TherapistDashboard({ onLogout }) {
  const [patients, setPatients] = useState([])
  const [notifications, setNotifications] = useState([])

  const [selectedPatient, setSelectedPatient] = useState(null)
  const [conversations, setConversations] = useState([])
  const [selectedConversation, setSelectedConversation] = useState(null)

  const [loadingPatients, setLoadingPatients] = useState(true)
  const [loadingNotifications, setLoadingNotifications] = useState(true)
  const [loadingConversations, setLoadingConversations] = useState(false)
  const [loadingConversation, setLoadingConversation] = useState(false)
  const [reviewingNotification, setReviewingNotification] = useState(false)

  const [error, setError] = useState('')


  useEffect(() => {
    loadAssignedPatients()
    loadNotifications()
  }, [])


  async function loadAssignedPatients() {
    const token = sessionStorage.getItem('access_token')

    if (!token) {
      onLogout()
      return
    }

    setLoadingPatients(true)
    setError('')

    try {
      const response = await fetch(
        `${API_URL}/therapist/patients`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        },
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.detail || 'Unable to load assigned patients.',
        )
      }

      setPatients(data.patients || [])
    } catch (err) {
      setError(
        err.message || 'Unable to load assigned patients.',
      )
    } finally {
      setLoadingPatients(false)
    }
  }


  async function loadNotifications() {
    const token = sessionStorage.getItem('access_token')

    if (!token) {
      onLogout()
      return
    }

    setLoadingNotifications(true)

    try {
      const response = await fetch(
        `${API_URL}/therapist/notifications`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        },
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.detail || 'Unable to load therapist notifications.',
        )
      }

      setNotifications(data.notifications || [])
    } catch (err) {
      setError(
        err.message || 'Unable to load therapist notifications.',
      )
    } finally {
      setLoadingNotifications(false)
    }
  }


  async function handleSelectPatient(patient) {
    const token = sessionStorage.getItem('access_token')

    if (!token) {
      onLogout()
      return
    }

    setSelectedPatient(patient)
    setSelectedConversation(null)
    setConversations([])
    setLoadingConversations(true)
    setError('')

    try {
      const response = await fetch(
        `${API_URL}/therapist/patients/${patient.id}/conversations`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        },
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.detail || 'Unable to load patient conversations.',
        )
      }

      setConversations(data.conversations || [])
    } catch (err) {
      setError(
        err.message || 'Unable to load patient conversations.',
      )
    } finally {
      setLoadingConversations(false)
    }
  }


  async function handleSelectConversation(conversationId) {
    const token = sessionStorage.getItem('access_token')

    if (!token || !selectedPatient) {
      onLogout()
      return
    }

    setLoadingConversation(true)
    setSelectedConversation(null)
    setError('')

    try {
      const response = await fetch(
        `${API_URL}/therapist/patients/${selectedPatient.id}/conversations/${conversationId}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        },
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.detail || 'Unable to load conversation.',
        )
      }

      setSelectedConversation(data)
    } catch (err) {
      setError(
        err.message || 'Unable to load conversation.',
      )
    } finally {
      setLoadingConversation(false)
    }
  }


  async function handleOpenNotification(notification) {
    const token = sessionStorage.getItem('access_token')

    if (!token) {
      onLogout()
      return
    }

    const patient =
      patients.find(
        (item) => item.id === notification.patient_id,
      ) || {
        id: notification.patient_id,
        first_name: notification.patient_first_name,
        last_name: notification.patient_last_name,
        email: '',
      }

    setSelectedPatient(patient)
    setSelectedConversation(null)
    setConversations([])
    setLoadingConversation(true)
    setError('')

    try {
      const conversationListResponse = await fetch(
        `${API_URL}/therapist/patients/${patient.id}/conversations`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        },
      )

      const conversationListData =
        await conversationListResponse.json()

      if (!conversationListResponse.ok) {
        throw new Error(
          conversationListData.detail ||
            'Unable to load patient conversations.',
        )
      }

      setConversations(
        conversationListData.conversations || [],
      )

      const conversationResponse = await fetch(
        `${API_URL}/therapist/patients/${patient.id}/conversations/${notification.conversation_id}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        },
      )

      const conversationData =
        await conversationResponse.json()

      if (!conversationResponse.ok) {
        throw new Error(
          conversationData.detail ||
            'Unable to load flagged conversation.',
        )
      }

      setSelectedConversation(conversationData)
    } catch (err) {
      setError(
        err.message || 'Unable to open safety alert.',
      )
    } finally {
      setLoadingConversation(false)
    }
  }


  async function handleMarkReviewed(notification) {
    const token = sessionStorage.getItem('access_token')

    if (!token) {
      onLogout()
      return
    }

    setReviewingNotification(true)
    setError('')

    try {
      const response = await fetch(
        `${API_URL}/therapist/notifications/${notification.id}/review`,
        {
          method: 'PATCH',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        },
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.detail || 'Unable to update safety alert.',
        )
      }

      setNotifications((current) =>
        current.map((item) =>
          item.id === notification.id
            ? {
                ...item,
                is_read: true,
                status: 'reviewed',
              }
            : item,
        ),
      )

      setConversations((current) =>
        current.map((conversation) =>
          conversation.id === notification.conversation_id
            ? {
                ...conversation,
                flag_status: 'reviewed',
              }
            : conversation,
        ),
      )

      setSelectedConversation((current) => {
        if (!current) {
          return current
        }

        return {
          ...current,
          red_flags: (current.red_flags || []).map((flag) =>
            flag.id === notification.red_flag_event_id
              ? {
                  ...flag,
                  status: 'reviewed',
                }
              : flag,
          ),
        }
      })
    } catch (err) {
      setError(
        err.message || 'Unable to update safety alert.',
      )
    } finally {
      setReviewingNotification(false)
    }
  }


  function formatDate(value) {
    if (!value) {
      return ''
    }

    return new Date(value).toLocaleDateString(
      'en-US',
      {
        month: 'long',
        day: 'numeric',
        year: 'numeric',
      },
    )
  }


  function handleBackToPatients() {
    setSelectedPatient(null)
    setSelectedConversation(null)
    setConversations([])
    setError('')
  }


  function handleBackToConversations() {
    setSelectedConversation(null)
    setError('')
  }


  const unreadNotifications = notifications.filter(
    (notification) => !notification.is_read,
  )


  const selectedConversationNotification =
    selectedConversation
      ? notifications.find(
          (notification) =>
            notification.conversation_id ===
              selectedConversation.id &&
            notification.patient_id === selectedPatient?.id,
        )
      : null


  return (
    <main className="therapist-page">
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
              Therapist Review Portal
            </p>
          </div>
        </div>

        <div className="chat-header-actions">
          <button
            type="button"
            className="chat-secondary-button"
            onClick={onLogout}
          >
            Sign Out
          </button>
        </div>
      </header>


      <section className="therapist-section">
        <div className="therapist-dashboard-card">

          {!selectedPatient && (
            <>
              <div className="therapist-dashboard-heading">
                <p className="therapist-eyebrow">
                  THERAPIST DASHBOARD
                </p>

                <h1>
                  Patient Overview
                </h1>

                <p className="therapist-subtitle">
                  Review assigned patients and safety alerts.
                </p>
              </div>


              {!loadingNotifications &&
                unreadNotifications.length > 0 && (
                  <div className="therapist-safety-area">
                    <h2 className="therapist-section-title">
                      Safety Alerts
                    </h2>

                    <div className="therapist-list">
                      {unreadNotifications.map(
                        (notification) => (
                          <button
                            key={notification.id}
                            type="button"
                            className="therapist-list-item therapist-alert-item"
                            onClick={() =>
                              handleOpenNotification(
                                notification,
                              )
                            }
                          >
                            <strong>
                              {notification.patient_first_name}{' '}
                              {notification.patient_last_name}
                            </strong>

                            <span className="therapist-alert-severity">
                              {notification.severity?.toUpperCase()} RISK
                            </span>

                            <span className="therapist-alert-copy">
                              Safety alert requires therapist review.
                            </span>
                          </button>
                        ),
                      )}
                    </div>
                  </div>
                )}


              <div className="therapist-patients-area">
                <h2 className="therapist-section-title">
                  Assigned Patients
                </h2>

                {loadingPatients && (
                  <p className="therapist-status">
                    Loading assigned patients...
                  </p>
                )}

                {!loadingPatients &&
                  patients.length === 0 && (
                    <p className="therapist-status">
                      No patients are currently assigned to you.
                    </p>
                  )}

                {!loadingPatients &&
                  patients.length > 0 && (
                    <div className="therapist-list">
                      {patients.map((patient) => (
                        <button
                          key={patient.id}
                          type="button"
                          className="therapist-list-item"
                          onClick={() =>
                            handleSelectPatient(patient)
                          }
                        >
                          <strong>
                            {patient.first_name}{' '}
                            {patient.last_name}
                          </strong>

                          <span>
                            {patient.email}
                          </span>
                        </button>
                      ))}
                    </div>
                  )}
              </div>
            </>
          )}


          {selectedPatient && !selectedConversation && (
            <>
              <div className="therapist-toolbar">
                <button
                  type="button"
                  className="therapist-back-button"
                  onClick={handleBackToPatients}
                >
                  ‹ Back to Patients
                </button>
              </div>

              <div className="therapist-page-heading">
                <p className="therapist-eyebrow">
                  PATIENT CONVERSATIONS
                </p>

                <h1>
                  {selectedPatient.first_name}{' '}
                  {selectedPatient.last_name}
                </h1>

                <p className="therapist-subtitle">
                  Review this patient&apos;s stored AI conversations.
                </p>
              </div>


              {loadingConversations && (
                <p className="therapist-status">
                  Loading conversation history...
                </p>
              )}


              {!loadingConversations &&
                conversations.length === 0 && (
                  <p className="therapist-status">
                    No saved conversations are available.
                  </p>
                )}


              {!loadingConversations &&
                conversations.length > 0 && (
                  <div className="therapist-list">
                    {conversations.map((conversation) => (
                      <button
                        key={conversation.id}
                        type="button"
                        className={
                          conversation.flagged
                            ? 'therapist-list-item conversation-card flagged-conversation-card'
                            : 'therapist-list-item conversation-card'
                        }
                        onClick={() =>
                          handleSelectConversation(
                            conversation.id,
                          )
                        }
                      >
                        <strong>
                          {conversation.title}
                        </strong>

                        {conversation.flagged && (
                          <span className="conversation-flag-label">
                            {conversation.flag_severity?.toUpperCase()}{' '}
                            RISK •{' '}
                            {conversation.flag_status?.toUpperCase()}
                          </span>
                        )}

                        <span className="conversation-date">
                          {formatDate(
                            conversation.started_at,
                          )}
                        </span>

                        <span className="conversation-preview">
                          {conversation.preview}
                        </span>
                      </button>
                    ))}
                  </div>
                )}
            </>
          )}


          {selectedConversation && (
            <>
              <div className="therapist-toolbar">
                <button
                  type="button"
                  className="therapist-back-button"
                  onClick={handleBackToConversations}
                >
                  ‹ Back to Conversations
                </button>
              </div>

              <div className="therapist-page-heading">
                <p className="therapist-eyebrow">
                  ORIGINAL CONVERSATION
                </p>

                <h1>
                  {selectedPatient.first_name}{' '}
                  {selectedPatient.last_name}
                </h1>

                <p className="therapist-subtitle">
                  {formatDate(
                    selectedConversation.started_at,
                  )}
                </p>
              </div>


              {selectedConversation.red_flags?.length > 0 && (
                <div className="therapist-conversation-alert">
                  <div>
                    <p className="therapist-alerts-label">
                      SAFETY ALERT
                    </p>

                    <h2>
                      {
                        selectedConversation.red_flags[0]
                          .severity
                      }
                      -risk message detected
                    </h2>

                    <p>
                      Review the original conversation below.
                    </p>
                  </div>

                  {selectedConversationNotification &&
                    !selectedConversationNotification.is_read && (
                      <button
                        type="button"
                        className="chat-secondary-button"
                        disabled={reviewingNotification}
                        onClick={() =>
                          handleMarkReviewed(
                            selectedConversationNotification,
                          )
                        }
                      >
                        {reviewingNotification
                          ? 'Updating...'
                          : 'Mark Reviewed'}
                      </button>
                    )}

                  {selectedConversationNotification?.is_read && (
                    <span className="therapist-reviewed-badge">
                      Reviewed
                    </span>
                  )}
                </div>
              )}


              <div className="therapist-transcript">
                {selectedConversation.messages.map(
                  (message) => (
                    <div
                      key={message.id}
                      className={
                        message.sender === 'ai'
                          ? 'therapist-message ai'
                          : 'therapist-message patient'
                      }
                    >
                      <p className="therapist-message-label">
                        {message.sender === 'ai'
                          ? 'Anchored AI'
                          : selectedPatient.first_name}
                      </p>

                      <div className="therapist-message-content">
                        {message.sender === 'ai' ? (
                          <ReactMarkdown>
                            {message.content}
                          </ReactMarkdown>
                        ) : (
                          <p>
                            {message.content}
                          </p>
                        )}
                      </div>
                    </div>
                  ),
                )}
              </div>
            </>
          )}


          {loadingConversation && (
            <p className="therapist-status">
              Loading conversation...
            </p>
          )}


          {error && (
            <p
              className="auth-error therapist-error"
              role="alert"
            >
              {error}
            </p>
          )}

        </div>
      </section>
    </main>
  )
}


export default TherapistDashboard