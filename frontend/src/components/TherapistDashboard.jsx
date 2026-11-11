
import { useEffect, useRef, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import './TherapistDashboard.css'

import API_URL from '../config'

function TherapistDashboard({ onLogout }) {
  const [patients, setPatients] = useState([])
  const [notifications, setNotifications] = useState([])
  const [alertConversationDetails, setAlertConversationDetails] =
    useState({})

  const [selectedPatient, setSelectedPatient] = useState(null)
  const [conversations, setConversations] = useState([])
  const [selectedConversation, setSelectedConversation] =
    useState(null)

  const [loadingPatients, setLoadingPatients] = useState(true)
  const [loadingNotifications, setLoadingNotifications] =
    useState(true)
  const [loadingConversations, setLoadingConversations] =
    useState(false)
  const [loadingConversation, setLoadingConversation] =
    useState(false)

  const [reviewingNotificationId, setReviewingNotificationId] =
    useState(null)
  const [showAlertHistory, setShowAlertHistory] =
    useState(false)
  const [error, setError] = useState('')

  const modalCloseButtonRef = useRef(null)
  const modalTriggerRef = useRef(null)

  useEffect(() => {
    loadAssignedPatients()
    loadNotifications()
  }, [])

  useEffect(() => {
    const outstanding = notifications.filter(
      (notification) =>
        !notification.is_read &&
        notification.patient_id != null &&
        notification.red_flag_event_id != null,
    )

    if (outstanding.length === 0) {
      setAlertConversationDetails({})
      return
    }

    let cancelled = false

    async function loadAlertConversationDetails() {
      const token = sessionStorage.getItem('access_token')

      if (!token) return

      const patientIds = [
        ...new Set(
          outstanding.map((notification) =>
            String(notification.patient_id),
          ),
        ),
      ]

      const results = await Promise.all(
        patientIds.map(async (patientId) => {
          try {
            const response = await fetch(
              `${API_URL}/therapist/patients/${patientId}/conversations`,
              {
                headers: {
                  Authorization: `Bearer ${token}`,
                },
              },
            )

            if (!response.ok) {
              return { patientId, conversations: [] }
            }

            const data = await response.json()

            return {
              patientId,
              conversations: data.conversations || [],
            }
          } catch {
            return { patientId, conversations: [] }
          }
        }),
      )

      if (cancelled) return

      const details = {}

      results.forEach(({ patientId, conversations: items }) => {
        items.forEach((conversation) => {
          const key = `${patientId}:${String(conversation.id)}`

          details[key] = {
            title: conversation.title,
            started_at: conversation.started_at,
          }
        })
      })

      setAlertConversationDetails(details)
    }

    loadAlertConversationDetails()

    return () => {
      cancelled = true
    }
  }, [notifications])

  useEffect(() => {
    if (!showAlertHistory) return

    modalCloseButtonRef.current?.focus()

    function handleKeyDown(event) {
      if (event.key === 'Escape') {
        closeAlertHistory()
        return
      }

      if (event.key !== 'Tab') return

      const modal = document.querySelector(
        '.therapist-history-modal',
      )

      if (!modal) return

      const focusableElements = Array.from(
        modal.querySelectorAll(
          'button:not([disabled]), [href], input:not([disabled]), [tabindex]:not([tabindex="-1"])',
        ),
      )

      if (focusableElements.length === 0) return

      const first = focusableElements[0]
      const last = focusableElements[focusableElements.length - 1]

      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault()
        last.focus()
      } else if (
        !event.shiftKey &&
        document.activeElement === last
      ) {
        event.preventDefault()
        first.focus()
      }
    }

    document.addEventListener('keydown', handleKeyDown)

    return () => {
      document.removeEventListener('keydown', handleKeyDown)
    }
  }, [showAlertHistory])

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
          data.detail ||
            'Unable to load therapist notifications.',
        )
      }

      setNotifications(data.notifications || [])
    } catch (err) {
      setError(
        err.message ||
          'Unable to load therapist notifications.',
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

    closeAlertHistory(false)
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
          data.detail ||
            'Unable to load patient conversations.',
        )
      }

      setConversations(data.conversations || [])
    } catch (err) {
      setError(
        err.message ||
          'Unable to load patient conversations.',
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

    closeAlertHistory(false)
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

    closeAlertHistory(false)

    const patient =
      patients.find(
        (item) =>
          String(item.id) === String(notification.patient_id),
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

      const conversationData = await conversationResponse.json()

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

  async function handleMarkReviewed(flag) {
    if (
      !flag ||
      flag.isReviewed ||
      reviewingNotificationId !== null
    ) {
      return
    }

    const token = sessionStorage.getItem('access_token')

    if (!token) {
      onLogout()
      return
    }

    setReviewingNotificationId(String(flag.id))
    setError('')

    try {
      const response = await fetch(
        `${API_URL}/therapist/red-flags/${flag.id}/review`,
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
          String(item.red_flag_event_id) === String(flag.id)
            ? {
                ...item,
                is_read: true,
                status: 'reviewed',
              }
            : item,
        ),
      )

      setSelectedConversation((current) => {
        if (!current) return current

        return {
          ...current,
          red_flags: (current.red_flags || []).map((item) =>
            String(item.id) === String(flag.id)
              ? {
                  ...item,
                  status: 'reviewed',
                }
              : item,
          ),
        }
      })

      const remainingForConversation =
        selectedConversationAlertHistory.some(
          (item) =>
            String(item.id) !== String(flag.id) &&
            !item.isReviewed,
        )

      setConversations((current) =>
        current.map((conversation) =>
          String(conversation.id) ===
          String(selectedConversation?.id)
            ? {
                ...conversation,
                flag_status: remainingForConversation
                  ? 'unreviewed'
                  : 'reviewed',
              }
            : conversation,
        ),
      )
    } catch (err) {
      setError(
        err.message || 'Unable to update safety alert.',
      )
    } finally {
      setReviewingNotificationId(null)
    }
  }

  function formatDate(value) {
    if (!value) return ''

    const date = new Date(value)

    if (Number.isNaN(date.getTime())) return ''

    return date.toLocaleDateString('en-US', {
      month: 'long',
      day: 'numeric',
      year: 'numeric',
    })
  }

  function formatDateTime(value) {
    if (!value) return ''

    const date = new Date(value)

    if (Number.isNaN(date.getTime())) return ''

    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    })
  }

  function openAlertHistory() {
    setError('')
    setShowAlertHistory(true)
  }

  function closeAlertHistory(restoreFocus = true) {
    setShowAlertHistory(false)

    if (restoreFocus) {
      requestAnimationFrame(() => {
        modalTriggerRef.current?.focus()
      })
    }
  }

  function handleBackToPatients() {
    closeAlertHistory(false)
    setSelectedPatient(null)
    setSelectedConversation(null)
    setConversations([])
    setError('')
  }

  function handleBackToConversations() {
    closeAlertHistory(false)
    setSelectedConversation(null)
    setError('')
  }

  const unreadNotifications = notifications.filter(
    (notification) =>
      !notification.is_read &&
      notification.patient_id != null &&
      notification.red_flag_event_id != null,
  )

  const patientsWithOutstandingAlerts = new Set(
    unreadNotifications.map((notification) =>
      String(notification.patient_id),
    ),
  )

  const outstandingCountsByPatient = {}

  unreadNotifications.forEach((notification) => {
    const patientId = String(notification.patient_id)

    outstandingCountsByPatient[patientId] =
      (outstandingCountsByPatient[patientId] || 0) + 1
  })

  function getConversationNotifications(
    patientId,
    conversationId,
  ) {
    return notifications.filter(
      (notification) =>
        String(notification.patient_id) ===
          String(patientId) &&
        String(notification.conversation_id) ===
          String(conversationId) &&
        notification.red_flag_event_id != null,
    )
  }

  const selectedConversationNotifications =
    selectedConversation && selectedPatient
      ? getConversationNotifications(
          selectedPatient.id,
          selectedConversation.id,
        )
      : []

  const selectedConversationAlertHistory = [
    ...(selectedConversation?.red_flags || []),
  ]
    .map((flag) => {
      const matchingNotifications =
        selectedConversationNotifications.filter(
          (notification) =>
            String(notification.red_flag_event_id) ===
            String(flag.id),
        )

      const outstandingNotification =
        matchingNotifications.find(
          (notification) => !notification.is_read,
        )

      const notification =
        outstandingNotification ||
        matchingNotifications[0] ||
        null

      const isReviewed = notification
        ? matchingNotifications.every((item) => item.is_read)
        : flag.status?.toLowerCase() === 'reviewed'

      // Match the exact patient message that caused this event.
      // Do not substitute another message when the ID is missing.
      const triggeringMessage =
        flag.message_id != null
          ? (selectedConversation?.messages || []).find(
              (message) =>
                String(message.id) ===
                  String(flag.message_id) &&
                message.sender !== 'ai',
            )
          : null

      return {
        ...flag,
        notification,
        isReviewed,
        triggeringMessage: triggeringMessage || null,
      }
    })
    .sort((first, second) => {
      const firstTime = first.detected_at
        ? new Date(first.detected_at).getTime()
        : 0

      const secondTime = second.detected_at
        ? new Date(second.detected_at).getTime()
        : 0

      if (secondTime !== firstTime) {
        return secondTime - firstTime
      }

      return Number(second.id) - Number(first.id)
    })

  const conversationTotalAlertCount =
    selectedConversationAlertHistory.length

  const conversationOutstandingAlertCount =
    selectedConversationAlertHistory.filter(
      (flag) => !flag.isReviewed,
    ).length

  const conversationNeedsReview =
    conversationOutstandingAlertCount > 0 ||
    selectedConversationNotifications.some(
      (notification) => !notification.is_read,
    )

  const conversationHasHighRiskAlert =
    selectedConversationAlertHistory.some(
      (flag) => flag.severity?.toLowerCase() === 'high',
    )

  function getConversationCardStatus(conversation) {
    const matchingNotifications = selectedPatient
      ? getConversationNotifications(
          selectedPatient.id,
          conversation.id,
        )
      : []

    if (
      matchingNotifications.some(
        (notification) => !notification.is_read,
      )
    ) {
      return 'REVIEW NEEDED'
    }

    if (
      matchingNotifications.length > 0 &&
      matchingNotifications.every(
        (notification) => notification.is_read,
      )
    ) {
      return 'REVIEWED'
    }

    return conversation.flag_status?.toLowerCase() === 'reviewed'
      ? 'REVIEWED'
      : 'REVIEW NEEDED'
  }

  function getConversationOutstandingCount(conversation) {
    if (!selectedPatient) return 0

    return getConversationNotifications(
      selectedPatient.id,
      conversation.id,
    ).filter((notification) => !notification.is_read).length
  }

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

                <h1>Patient Overview</h1>

                <p className="therapist-subtitle">
                  Review assigned patients and safety alerts.
                </p>
              </div>

              {!loadingNotifications &&
                unreadNotifications.length > 0 && (
                  <div className="therapist-safety-area">
                    <div className="therapist-alert-heading-row">
                      <h2 className="therapist-section-title">
                        Safety Alerts
                      </h2>

                      <span className="therapist-alert-count">
                        {unreadNotifications.length}{' '}
                        {unreadNotifications.length === 1
                          ? 'requires'
                          : 'require'}{' '}
                        review
                      </span>
                    </div>

                    <div className="therapist-list">
                      {unreadNotifications.map(
                        (notification) => {
                          const conversationKey =
                            `${String(notification.patient_id)}:` +
                            String(notification.conversation_id)

                          const conversationDetails =
                            alertConversationDetails[conversationKey]

                          const conversationTitle =
                            conversationDetails?.title ||
                            `Conversation #${notification.conversation_id}`

                          return (
                            <button
                              key={notification.id}
                              type="button"
                              className="therapist-list-item therapist-alert-item"
                              onClick={() =>
                                handleOpenNotification(notification)
                              }
                            >
                              <strong>
                                {notification.patient_first_name}{' '}
                                {notification.patient_last_name}
                              </strong>

                              <span className="conversation-preview">
                                Conversation: {conversationTitle}
                              </span>

                              {notification.created_at && (
                                <span className="conversation-date">
                                  Alert received:{' '}
                                  {formatDateTime(
                                    notification.created_at,
                                  )}
                                </span>
                              )}

                              <span className="therapist-alert-severity">
                                {notification.severity?.toUpperCase() ||
                                  'SAFETY'}{' '}
                                {notification.severity
                                  ? 'RISK SAFETY ALERT'
                                  : 'ALERT'}{' '}
                                · REVIEW NEEDED
                              </span>

                              <span className="therapist-alert-copy">
                                Safety alert requires therapist review.
                              </span>
                            </button>
                          )
                        },
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
                      {patients.map((patient) => {
                        const patientId = String(patient.id)

                        const hasOutstandingAlert =
                          patientsWithOutstandingAlerts.has(patientId)

                        const alertCount =
                          outstandingCountsByPatient[patientId] || 0

                        const hasHighRiskAlert =
                          unreadNotifications.some(
                            (notification) =>
                              String(notification.patient_id) ===
                                patientId &&
                              notification.severity?.toLowerCase() ===
                                'high',
                          )

                        const alertLabel = hasHighRiskAlert
                          ? 'HIGH RISK SAFETY ALERT'
                          : 'SAFETY ALERT'

                        return (
                          <button
                            key={patient.id}
                            type="button"
                            className={
                              hasOutstandingAlert
                                ? 'therapist-list-item therapist-patient-alert'
                                : 'therapist-list-item'
                            }
                            onClick={() =>
                              handleSelectPatient(patient)
                            }
                          >
                            <strong>
                              {patient.first_name}{' '}
                              {patient.last_name}
                            </strong>

                            <span>{patient.email}</span>

                            {hasOutstandingAlert && (
                              <span className="therapist-patient-alert-label">
                                {alertCount > 1
                                  ? `${alertCount} SAFETY ALERTS · REVIEW NEEDED`
                                  : `${alertLabel} · REVIEW NEEDED`}
                              </span>
                            )}
                          </button>
                        )
                      })}
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
                    {conversations.map((conversation) => {
                      const overallStatus =
                        getConversationCardStatus(conversation)

                      const outstandingCount =
                        getConversationOutstandingCount(conversation)

                      return (
                        <button
                          key={conversation.id}
                          type="button"
                          className={
                            conversation.flagged
                              ? 'therapist-list-item conversation-card flagged-conversation-card'
                              : 'therapist-list-item conversation-card'
                          }
                          onClick={() =>
                            handleSelectConversation(conversation.id)
                          }
                        >
                          <strong>{conversation.title}</strong>

                          {conversation.flagged && (
                            <span className="conversation-flag-label">
                              {conversation.flag_severity?.toUpperCase()}{' '}
                              RISK SAFETY ALERT · {overallStatus}
                              {outstandingCount > 1 &&
                                ` (${outstandingCount})`}
                            </span>
                          )}

                          <span className="conversation-date">
                            {formatDate(conversation.started_at)}
                          </span>

                          <span className="conversation-preview">
                            {conversation.preview}
                          </span>
                        </button>
                      )
                    })}
                  </div>
                )}
            </>
          )}

          {selectedConversation && (
            <div className="therapist-conversation-view">
              {conversationTotalAlertCount > 0 && (
                <div
                  className="therapist-conversation-alert"
                  role="status"
                >
                  <div className="therapist-conversation-alert-main">
                    <div className="therapist-conversation-alert-icon">
                      <svg
                        width="23"
                        height="23"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="1.8"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        aria-hidden="true"
                      >
                        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z" />
                        <path d="M12 8v5" />
                        <path d="M12 17h.01" />
                      </svg>
                    </div>

                    <div className="therapist-conversation-alert-info">
                      <span className="therapist-alerts-label">
                        {conversationHasHighRiskAlert
                          ? 'HIGH-RISK SAFETY ALERT'
                          : 'SAFETY ALERT'}
                      </span>

                      <span className="therapist-conversation-alert-summary">
                        {conversationOutstandingAlertCount}{' '}
                        {conversationOutstandingAlertCount === 1
                          ? 'requires'
                          : 'require'}{' '}
                        review
                        <span className="therapist-conversation-alert-separator">
                          {' · '}
                        </span>
                        {conversationTotalAlertCount}{' '}
                        recorded
                      </span>
                    </div>
                  </div>

                  <button
                    ref={modalTriggerRef}
                    type="button"
                    className="therapist-history-button"
                    onClick={openAlertHistory}
                  >
                    <svg
                      width="18"
                      height="18"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      aria-hidden="true"
                    >
                      <path d="M3 12a9 9 0 1 0 3-6.7" />
                      <path d="M3 3v6h6" />
                      <path d="M12 7v5l3 2" />
                    </svg>
                    View Alerts
                  </button>
                </div>
              )}

              <div className="therapist-conversation-content">
                <div className="therapist-toolbar">
                  <button
                    type="button"
                    className="therapist-back-button"
                    onClick={handleBackToConversations}
                  >
                    ‹ Back to Conversations
                  </button>
                </div>

                <div className="therapist-page-heading therapist-conversation-heading">
                  <h1>
                    {selectedPatient.first_name}{' '}
                    {selectedPatient.last_name}
                  </h1>

                  <p className="therapist-subtitle">
                    {formatDate(selectedConversation.started_at)}
                  </p>
                </div>

                <div className="therapist-transcript-section">
                  <div className="therapist-transcript-divider">
                    <h2>CONVERSATION TRANSCRIPT</h2>
                    <span aria-hidden="true" />
                  </div>

                  <div className="therapist-transcript">
                    {(selectedConversation.messages || []).map(
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
                              <p>{message.content}</p>
                            )}
                          </div>
                        </div>
                      ),
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {loadingConversation && (
            <p className="therapist-status">
              Loading conversation...
            </p>
          )}

          {error && !showAlertHistory && (
            <p
              className="auth-error therapist-error"
              role="alert"
            >
              {error}
            </p>
          )}
        </div>
      </section>

      {showAlertHistory &&
        selectedConversation &&
        selectedPatient && (
          <div className="therapist-history-overlay">
            <section
              className="therapist-history-modal"
              role="dialog"
              aria-modal="true"
              aria-labelledby="therapist-history-title"
              aria-describedby="therapist-history-description"
            >
              <div className="therapist-history-modal-header">
                <div className="therapist-history-modal-heading">
                  <p className="therapist-eyebrow">
                    CONVERSATION SAFETY RECORD
                  </p>

                  <h2 id="therapist-history-title">
                    Safety Alert History
                  </h2>

                  <p id="therapist-history-description">
                    {selectedPatient.first_name}{' '}
                    {selectedPatient.last_name}
                    {' · '}
                    {conversationTotalAlertCount}{' '}
                    {conversationTotalAlertCount === 1
                      ? 'total alert'
                      : 'total alerts'}
                  </p>
                </div>

                <button
                  ref={modalCloseButtonRef}
                  type="button"
                  className="therapist-history-close"
                  onClick={() => closeAlertHistory()}
                  aria-label="Close safety alert history"
                >
                  <svg
                    width="22"
                    height="22"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    aria-hidden="true"
                  >
                    <path d="M18 6 6 18M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <div className="therapist-history-modal-body">
                <div className="therapist-history-summary">
                  <span className="therapist-history-summary-total">
                    {conversationTotalAlertCount}{' '}
                    {conversationTotalAlertCount === 1
                      ? 'alert recorded'
                      : 'alerts recorded'}
                  </span>

                  <span
                    className={
                      conversationNeedsReview
                        ? 'therapist-history-summary-pending'
                        : 'therapist-history-summary-complete'
                    }
                  >
                    {conversationNeedsReview
                      ? `${conversationOutstandingAlertCount} ${
                          conversationOutstandingAlertCount === 1
                            ? 'needs'
                            : 'need'
                        } review`
                      : 'All reviewed'}
                  </span>
                </div>

                <p className="therapist-history-guidance">
                  Review each safety alert individually.
                </p>

                <div className="therapist-history-event-list">
                  {selectedConversationAlertHistory.map((flag) => {
                    const canReview = !flag.isReviewed

                    const isSaving =
                      reviewingNotificationId === String(flag.id)

                    return (
                      <article
                        key={flag.id}
                        className="therapist-history-event"
                      >
                        <div className="therapist-history-event-top">
                          <span className="therapist-history-event-severity">
                            {flag.severity?.toUpperCase() ||
                              'SAFETY'}{' '}
                            {flag.severity ? 'RISK' : 'ALERT'}
                          </span>

                          <span
                            className={
                              flag.isReviewed
                                ? 'therapist-history-event-status is-reviewed'
                                : 'therapist-history-event-status is-pending'
                            }
                          >
                            {flag.isReviewed && (
                              <svg
                                width="15"
                                height="15"
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="currentColor"
                                strokeWidth="2.5"
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                aria-hidden="true"
                              >
                                <path d="M20 6 9 17l-5-5" />
                              </svg>
                            )}

                            {flag.isReviewed
                              ? 'Reviewed'
                              : 'Review Needed'}
                          </span>
                        </div>

                        <p className="therapist-history-event-date">
                          Detected:{' '}
                          {formatDateTime(flag.detected_at) ||
                            'Time unavailable'}
                        </p>

                        <div className="therapist-history-message">
                          <p className="therapist-history-message-label">
                            FLAGGED PATIENT MESSAGE
                          </p>

                          {flag.triggeringMessage ? (
                            <p className="therapist-history-message-content">
                              {flag.triggeringMessage.content}
                            </p>
                          ) : (
                            <p className="therapist-history-message-unavailable">
                              The original message could not be
                              matched to this safety event.
                            </p>
                          )}
                        </div>

                        {canReview && (
                          <div className="therapist-history-event-actions">
                            <button
                              type="button"
                              className="therapist-mark-reviewed-button"
                              disabled={
                                reviewingNotificationId !== null
                              }
                              onClick={() =>
                                handleMarkReviewed(flag)
                              }
                            >
                              {isSaving
                                ? 'Updating...'
                                : 'Mark as Reviewed'}
                            </button>
                          </div>
                        )}


                      </article>
                    )
                  })}
                </div>

                {error && (
                  <p
                    className="auth-error therapist-error"
                    role="alert"
                  >
                    {error}
                  </p>
                )}
              </div>

              <div className="therapist-history-modal-footer">
                <button
                  type="button"
                  className="therapist-history-done"
                  onClick={() => closeAlertHistory()}
                >
                  Close
                </button>
              </div>
            </section>
          </div>
        )}
    </main>
  )
}

export default TherapistDashboard
