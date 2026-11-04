
import { useEffect, useMemo, useState } from 'react'
import './AdminDashboard.css'

const API_URL = 'http://127.0.0.1:8000'

function AdminDashboard({ onLogout }) {
  const [summary, setSummary] = useState(null)
  const [users, setUsers] = useState([])
  const [therapists, setTherapists] = useState([])
  const [assignments, setAssignments] = useState([])
  const [safetyActivity, setSafetyActivity] = useState([])
  const [systemMetadata, setSystemMetadata] = useState(null)

  const [selectedTherapists, setSelectedTherapists] = useState({})
  const [activeTab, setActiveTab] = useState('dashboard')
  const [userRoleFilter, setUserRoleFilter] = useState('all')
  const [showBackToDashboard, setShowBackToDashboard] = useState(false)

  const [loading, setLoading] = useState(true)
  const [savingPatientId, setSavingPatientId] = useState(null)
  const [error, setError] = useState('')
  const [unassignWarning, setUnassignWarning] = useState(null)

  useEffect(() => {
    loadAdminData()
  }, [])

  async function apiRequest(path, options = {}) {
    const token = sessionStorage.getItem('access_token')

    if (!token) {
      onLogout()
      throw new Error('Your session has ended.')
    }

    const response = await fetch(`${API_URL}${path}`, {
      ...options,
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
        ...(options.headers || {}),
      },
    })

    if (response.status === 401) {
      onLogout()
      throw new Error('Your session has ended.')
    }

    if (!response.ok) {
      let message = 'Something went wrong.'

      try {
        const data = await response.json()
        message = data.detail || message
      } catch {
        // Keep the default message.
      }

      const requestError = new Error(message)
      requestError.status = response.status
      throw requestError
    }

    if (response.status === 204) {
      return null
    }

    return response.json()
  }

  async function loadAdminData() {
    setLoading(true)
    setError('')

    try {
      const [
        summaryData,
        usersData,
        therapistsData,
        assignmentsData,
        safetyData,
        systemData,
      ] = await Promise.all([
        apiRequest('/admin/summary'),
        apiRequest('/admin/users'),
        apiRequest('/admin/therapists'),
        apiRequest('/admin/assignments'),
        apiRequest('/admin/safety'),
        apiRequest('/admin/system'),
      ])

      setSummary(summaryData)
      setUsers(usersData.users || [])
      setTherapists(therapistsData.therapists || [])
      setAssignments(assignmentsData.assignments || [])
      setSafetyActivity(safetyData.activity || [])
      setSystemMetadata(systemData)

      const initialSelections = {}

      ;(assignmentsData.assignments || []).forEach((assignment) => {
        initialSelections[assignment.patient_id] =
          assignment.therapist_id?.toString() || ''
      })

      setSelectedTherapists(initialSelections)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  async function refreshAssignmentsAndSummary() {
    const [summaryData, assignmentsData] = await Promise.all([
      apiRequest('/admin/summary'),
      apiRequest('/admin/assignments'),
    ])

    setSummary(summaryData)
    setAssignments(assignmentsData.assignments || [])

    const refreshedSelections = {}

    ;(assignmentsData.assignments || []).forEach((assignment) => {
      refreshedSelections[assignment.patient_id] =
        assignment.therapist_id?.toString() || ''
    })

    setSelectedTherapists(refreshedSelections)
  }

  async function handleSaveAssignment(patientId) {
    const therapistId = selectedTherapists[patientId]

    if (!therapistId) {
      return
    }

    setSavingPatientId(patientId)
    setError('')

    try {
      await apiRequest(`/admin/assignments/${patientId}`, {
        method: 'PUT',
        body: JSON.stringify({
          therapist_id: Number(therapistId),
        }),
      })

      await refreshAssignmentsAndSummary()
    } catch (err) {
      setError(err.message)
    } finally {
      setSavingPatientId(null)
    }
  }

  function hasOutstandingHighRiskAlert(patientId, activity) {
    return activity.some(
      (event) =>
        String(event.patient_id) === String(patientId) &&
        String(event.severity || '').toLowerCase() === 'high' &&
        String(event.status || '').toLowerCase() !== 'reviewed'
    )
  }

  function showUnassignBlockedWarning() {
    setUnassignWarning({
      title: 'Cannot Unassign Therapist',
      message:
        'This patient has an outstanding high-risk safety alert that requires therapist review. The therapist cannot be unassigned until all high-risk safety alerts have been reviewed.',
    })
  }

  async function handleRemoveAssignment(patientId) {
    if (savingPatientId !== null) return

    setSavingPatientId(patientId)
    setError('')

    try {
      // Check current safety activity before offering confirmation.
      const safetyData = await apiRequest('/admin/safety')
      const latestActivity = safetyData.activity || []

      setSafetyActivity(latestActivity)

      if (hasOutstandingHighRiskAlert(patientId, latestActivity)) {
        showUnassignBlockedWarning()
        return
      }

      // Preserve confirmation for eligible patients.
      const confirmed = window.confirm(
        "Unassign Therapist?\n\nThis will remove the patient's current therapist assignment. The patient account and conversation history will not be deleted."
      )

      if (!confirmed) {
        return
      }

      await apiRequest(`/admin/assignments/${patientId}`, {
        method: 'DELETE',
      })

      await refreshAssignmentsAndSummary()
    } catch (err) {
      // The backend remains the authority if safety status changes.
      const safetyRelatedError =
        err.status === 409 ||
        (err.status === 403 &&
          /safety|risk|review|flag|alert/i.test(err.message)) ||
        /unreviewed.*(high|risk|alert)|high.risk|safety alert/i.test(
          err.message
        )

      if (safetyRelatedError) {
        showUnassignBlockedWarning()
      } else {
        setError(err.message)
      }
    } finally {
      setSavingPatientId(null)
    }
  }

  function handleTopLevelTab(tab) {
    setShowBackToDashboard(false)

    if (tab === 'users') {
      setUserRoleFilter('all')
    }

    setActiveTab(tab)
  }

  function openDashboardSection(tab) {
    setShowBackToDashboard(true)
    setActiveTab(tab)
  }

  function openUsers(role, fromDashboard = false) {
    setUserRoleFilter(role)
    setShowBackToDashboard(fromDashboard)
    setActiveTab('users')
  }

  function handleBackToDashboard() {
    setUserRoleFilter('all')
    setShowBackToDashboard(false)
    setActiveTab('dashboard')
  }

  function formatDate(value) {
    if (!value) {
      return 'Not available'
    }

    return new Date(value).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    })
  }

  function formatDateTime(value) {
    if (!value) {
      return 'Not available'
    }

    return new Date(value).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    })
  }

  function roleLabel(role) {
    if (role === 'patient') return 'Patient'
    if (role === 'therapist') return 'Therapist'
    if (role === 'admin') return 'Administrator'

    return role
  }

  function sourceLabel(filename) {
    const withoutExtension = filename.replace(/\.[^/.]+$/, '')

    return withoutExtension
      .split('_')
      .map((word) => {
        return word.charAt(0).toUpperCase() + word.slice(1)
      })
      .join(' ')
  }

  const filteredUsers = useMemo(() => {
    if (userRoleFilter === 'all') {
      return users
    }

    return users.filter((user) => user.role === userRoleFilter)
  }, [users, userRoleFilter])

  if (loading) {
    return (
      <div className="admin-page">
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
              <div className="chat-brand-name">
                Anchored Support Services
              </div>

              <div className="chat-brand-subtitle">
                Administration Portal
              </div>
            </div>
          </div>

          <button
            type="button"
            className="chat-secondary-button"
            onClick={onLogout}
          >
            Sign Out
          </button>
        </header>

        <main className="admin-main">
          <div className="admin-loading">
            Loading administration tools...
          </div>
        </main>
      </div>
    )
  }

  return (
    <div className="admin-page">
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
            <div className="chat-brand-name">
              Anchored Support Services
            </div>

            <div className="chat-brand-subtitle">
              Administration Portal
            </div>
          </div>
        </div>

        <button
          type="button"
          className="chat-secondary-button"
          onClick={onLogout}
        >
          Sign Out
        </button>
      </header>

      <main className="admin-main">
        <section className="admin-panel">
          <div className="admin-page-intro">
            <h1>Operations Center</h1>

            <p>
              Manage users, therapist assignments, and safety activity.
            </p>
          </div>

          <nav
            className="admin-tabs"
            aria-label="Administration sections"
          >
            <button
              type="button"
              className={`admin-tab ${
                activeTab === 'dashboard' ? 'active' : ''
              }`}
              onClick={() => handleTopLevelTab('dashboard')}
            >
              Dashboard
            </button>

            <button
              type="button"
              className={`admin-tab ${
                activeTab === 'assignments' ? 'active' : ''
              }`}
              onClick={() => handleTopLevelTab('assignments')}
            >
              Assignments
            </button>

            <button
              type="button"
              className={`admin-tab ${
                activeTab === 'users' ? 'active' : ''
              }`}
              onClick={() => handleTopLevelTab('users')}
            >
              Users
            </button>

            <button
              type="button"
              className={`admin-tab ${
                activeTab === 'safety' ? 'active' : ''
              }`}
              onClick={() => handleTopLevelTab('safety')}
            >
              Safety
            </button>

            <button
              type="button"
              className={`admin-tab ${
                activeTab === 'system' ? 'active' : ''
              }`}
              onClick={() => handleTopLevelTab('system')}
            >
              System Status
            </button>
          </nav>

          {error && (
            <div className="admin-error" role="alert">
              {error}
            </div>
          )}

          {activeTab !== 'dashboard' && (
            <div className="admin-back-row">
              <button
                type="button"
                className="admin-secondary-button admin-back-button"
                onClick={handleBackToDashboard}
              >
                <svg
                  className="admin-back-icon"
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  aria-hidden="true"
                  focusable="false"
                >
                  <path d="M19 12H5" />
                  <path d="M12 19l-7-7 7-7" />
                </svg>

                <span>Back to Admin Dashboard</span>
              </button>
            </div>
          )}

          {activeTab === 'dashboard' && (
            <div className="admin-dashboard-content">
              <div className="admin-metric-grid">
                <button
                  type="button"
                  className="admin-metric-card"
                  onClick={() => openUsers('patient', true)}
                >
                  <span className="admin-card-chevron">›</span>

                  <span className="admin-metric-number">
                    {summary?.active_patients ?? 0}
                  </span>

                  <span className="admin-metric-label">
                    Active Patients
                  </span>
                </button>

                <button
                  type="button"
                  className="admin-metric-card"
                  onClick={() => openUsers('therapist', true)}
                >
                  <span className="admin-card-chevron">›</span>

                  <span className="admin-metric-number">
                    {summary?.active_therapists ?? 0}
                  </span>

                  <span className="admin-metric-label">
                    Active Therapists
                  </span>
                </button>

                <button
                  type="button"
                  className="admin-metric-card"
                  onClick={() => openDashboardSection('assignments')}
                >
                  <span className="admin-card-chevron">›</span>

                  <span className="admin-metric-number">
                    {summary?.assignments ?? 0}
                  </span>

                  <span className="admin-metric-label">
                    Current Assignments
                  </span>
                </button>

                <button
                  type="button"
                  className="admin-metric-card"
                  onClick={() => openDashboardSection('safety')}
                >
                  <span className="admin-card-chevron">›</span>

                  <span className="admin-metric-number">
                    {summary?.unreviewed_flags ?? 0}
                  </span>

                  <span className="admin-metric-label">
                    Unreviewed Safety Flags
                  </span>
                </button>
              </div>

              <section className="admin-section">
                <h2>Quick Actions</h2>

                <div className="admin-action-grid">
                  <button
                    type="button"
                    className="admin-action-card"
                    onClick={() => openDashboardSection('assignments')}
                  >
                    <span className="admin-action-chevron">›</span>

                    <span className="admin-action-title">
                      Patient Assignments
                    </span>

                    <span className="admin-action-description">
                      Assign and reassign patients to therapists.
                    </span>
                  </button>

                  <button
                    type="button"
                    className="admin-action-card"
                    onClick={() => openUsers('all', true)}
                  >
                    <span className="admin-action-chevron">›</span>

                    <span className="admin-action-title">
                      User Directory
                    </span>

                    <span className="admin-action-description">
                      Review patient, therapist, and administrator accounts.
                    </span>
                  </button>
                </div>
              </section>
            </div>
          )}

          {activeTab === 'assignments' && (
            <section className="admin-content-section">
              <div className="admin-section-heading">
                <div>
                  <h2>Patient Assignments</h2>

                  <p>
                    Assign each active patient to the appropriate therapist.
                  </p>
                </div>
              </div>

              <div className="admin-assignment-grid">
                {assignments.map((assignment) => {
                  const currentTherapistId =
                    assignment.therapist_id?.toString() || ''

                  const selectedTherapistId =
                    selectedTherapists[assignment.patient_id] || ''

                  const selectionChanged =
                    selectedTherapistId !== currentTherapistId

                  return (
                    <article
                      className="admin-assignment-card"
                      key={assignment.patient_id}
                    >
                      <div className="admin-assignment-patient">
                        <h3>
                          {assignment.patient_first_name}{' '}
                          {assignment.patient_last_name}
                        </h3>

                        <p>{assignment.patient_email}</p>
                      </div>

                      <div className="admin-current-assignment">
                        <span className="admin-field-label">
                          Current Therapist
                        </span>

                        <span
                          className={
                            assignment.therapist_id
                              ? 'admin-current-value'
                              : 'admin-current-value unassigned'
                          }
                        >
                          {assignment.therapist_id
                            ? `${assignment.therapist_first_name} ${assignment.therapist_last_name}`
                            : 'Unassigned'}
                        </span>
                      </div>

                      <label className="admin-select-label">
                        Therapist

                        <select
                          value={selectedTherapistId}
                          onChange={(event) => {
                            setSelectedTherapists((current) => ({
                              ...current,
                              [assignment.patient_id]:
                                event.target.value,
                            }))
                          }}
                        >
                          <option value="">
                            Select a therapist
                          </option>

                          {therapists.map((therapist) => (
                            <option
                              key={therapist.id}
                              value={therapist.id}
                            >
                              {therapist.first_name}{' '}
                              {therapist.last_name}
                            </option>
                          ))}
                        </select>
                      </label>

                      <div className="admin-assignment-actions">
                        <button
                          type="button"
                          className="admin-primary-button"
                          disabled={
                            !selectedTherapistId ||
                            !selectionChanged ||
                            savingPatientId === assignment.patient_id
                          }
                          onClick={() =>
                            handleSaveAssignment(assignment.patient_id)
                          }
                        >
                          {savingPatientId === assignment.patient_id
                            ? 'Saving...'
                            : assignment.therapist_id
                              ? 'Update Assignment'
                              : 'Assign Therapist'}
                        </button>

                        {assignment.therapist_id && (
                          <button
                            type="button"
                            className="admin-secondary-button"
                            disabled={
                              savingPatientId === assignment.patient_id
                            }
                            onClick={() =>
                              handleRemoveAssignment(
                                assignment.patient_id
                              )
                            }
                          >
                            Unassign Therapist
                          </button>
                        )}
                      </div>
                    </article>
                  )
                })}
              </div>
            </section>
          )}

          {activeTab === 'users' && (
            <section className="admin-content-section">
              <div className="admin-section-heading">
                <div>
                  <h2>User Directory</h2>

                  <p>
                    Review patient, therapist, and administrator accounts.
                  </p>
                </div>
              </div>

              <div className="admin-filter-row">
                <button
                  type="button"
                  className={`admin-filter-button ${
                    userRoleFilter === 'all' ? 'active' : ''
                  }`}
                  onClick={() => setUserRoleFilter('all')}
                >
                  All Users
                </button>

                <button
                  type="button"
                  className={`admin-filter-button ${
                    userRoleFilter === 'patient' ? 'active' : ''
                  }`}
                  onClick={() => setUserRoleFilter('patient')}
                >
                  Patients
                </button>

                <button
                  type="button"
                  className={`admin-filter-button ${
                    userRoleFilter === 'therapist' ? 'active' : ''
                  }`}
                  onClick={() => setUserRoleFilter('therapist')}
                >
                  Therapists
                </button>

                <button
                  type="button"
                  className={`admin-filter-button ${
                    userRoleFilter === 'admin' ? 'active' : ''
                  }`}
                  onClick={() => setUserRoleFilter('admin')}
                >
                  Administrators
                </button>
              </div>

              <div className="admin-table-wrapper">
                <table className="admin-table">
                  <thead>
                    <tr>
                      <th>Name</th>
                      <th>Email</th>
                      <th>Role</th>
                      <th>Status</th>
                      <th>Created</th>
                    </tr>
                  </thead>

                  <tbody>
                    {filteredUsers.map((user) => (
                      <tr key={user.id}>
                        <td>
                          {user.first_name}{' '}
                          {user.last_name}
                        </td>

                        <td>{user.email}</td>

                        <td>{roleLabel(user.role)}</td>

                        <td>
                          <span
                            className={`admin-status ${
                              user.is_active ? 'active' : 'inactive'
                            }`}
                          >
                            {user.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </td>

                        <td>{formatDate(user.created_at)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          )}

          {activeTab === 'safety' && (
            <section className="admin-content-section">
              <div className="admin-section-heading">
                <div>
                  <h2>Safety Activity</h2>

                  <p>
                    Monitor safety event status without accessing private
                    conversation transcripts.
                  </p>
                </div>
              </div>

              {safetyActivity.length === 0 ? (
                <div className="admin-empty-state">
                  No safety activity has been recorded.
                </div>
              ) : (
                <div className="admin-table-wrapper">
                  <table className="admin-table">
                    <thead>
                      <tr>
                        <th>Patient</th>
                        <th>Severity</th>
                        <th>Status</th>
                        <th>Detected</th>
                        <th>Assigned Therapist</th>
                      </tr>
                    </thead>

                    <tbody>
                      {safetyActivity.map((event) => (
                        <tr key={event.id}>
                          <td>
                            {event.patient_first_name}{' '}
                            {event.patient_last_name}
                          </td>

                          <td>
                            <span
                              className={`admin-safety-severity ${
                                event.severity || ''
                              }`}
                            >
                              {event.severity
                                ? event.severity
                                    .charAt(0)
                                    .toUpperCase() +
                                  event.severity.slice(1)
                                : 'Unknown'}
                            </span>
                          </td>

                          <td>
                            <span
                              className={`admin-safety-status ${
                                event.status || ''
                              }`}
                            >
                              {event.status
                                ? event.status
                                    .charAt(0)
                                    .toUpperCase() +
                                  event.status.slice(1)
                                : 'Unknown'}
                            </span>
                          </td>

                          <td>{formatDateTime(event.detected_at)}</td>

                          <td>
                            {event.therapist_id
                              ? `${event.therapist_first_name} ${event.therapist_last_name}`
                              : 'Unassigned'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </section>
          )}

          {activeTab === 'system' && (
            <section className="admin-content-section">
              <div className="admin-section-heading">
                <div>
                  <h2>System Status</h2>

                  <p>
                    Review the current knowledge base and platform configuration.
                  </p>
                </div>

                <span className="admin-system-label">
                  Read Only
                </span>
              </div>

              <div className="admin-system-section">
                <h3>Knowledge Base</h3>

                <div className="admin-config-list">
                  <div className="admin-config-row">
                    <span>Status</span>

                    <strong>
                      {systemMetadata?.knowledge_base?.configured
                        ? 'Active'
                        : 'Not Configured'}
                    </strong>
                  </div>

                  <div className="admin-config-row">
                    <span>Source Documents</span>

                    <strong>
                      {systemMetadata?.knowledge_base
                        ?.source_document_count ?? 0}
                    </strong>
                  </div>

                  <div className="admin-config-row">
                    <span>Knowledge Chunks</span>

                    <strong>
                      {systemMetadata?.knowledge_base
                        ?.chunk_count ?? 0}
                    </strong>
                  </div>
                </div>

                <div className="admin-knowledge-sources">
                  <span className="admin-system-label">
                    Knowledge Sources
                  </span>

                  <div className="admin-knowledge-source-grid">
                    {(
                      systemMetadata?.knowledge_base
                        ?.source_documents || []
                    ).map((source) => (
                      <div
                        className="admin-knowledge-source-item"
                        key={source}
                      >
                        {sourceLabel(source)}
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="admin-system-section">
                <h3>Platform Status</h3>

                <div className="admin-config-list">
                  <div className="admin-config-row">
                    <span>Authentication</span>

                    <strong>
                      {systemMetadata?.system
                        ?.authentication_enabled
                        ? 'Enabled'
                        : 'Disabled'}
                    </strong>
                  </div>

                  <div className="admin-config-row">
                    <span>Supported Roles</span>

                    <strong>
                      {(
                        systemMetadata?.system
                          ?.supported_roles || []
                      )
                        .map(roleLabel)
                        .join(', ')}
                    </strong>
                  </div>

                  <div className="admin-config-row">
                    <span>Therapist Assignment Enforcement</span>

                    <strong>
                      {systemMetadata?.system
                        ?.assignment_enforcement_enabled
                        ? 'Enabled'
                        : 'Disabled'}
                    </strong>
                  </div>

                  <div className="admin-config-row">
                    <span>Safety Monitoring</span>

                    <strong>
                      {systemMetadata?.system
                        ?.safety_monitoring_enabled
                        ? 'Enabled'
                        : 'Disabled'}
                    </strong>
                  </div>

                  <div className="admin-config-row">
                    <span>Administrator Transcript Access</span>

                    <strong>
                      {systemMetadata?.system
                        ?.admin_transcript_access === 'restricted'
                        ? 'Restricted'
                        : 'Available'}
                    </strong>
                  </div>

                  <div className="admin-config-row">
                    <span>Session Duration</span>

                    <strong>
                      {systemMetadata?.system
                        ?.access_token_expire_minutes ?? 0}{' '}
                      minutes
                    </strong>
                  </div>

                  <div className="admin-config-row">
                    <span>AI Model</span>

                    <strong>
                      {systemMetadata?.system?.ai_model ||
                        'Configured'}
                    </strong>
                  </div>
                </div>
              </div>
            </section>
          )}
        </section>
      </main>

      {unassignWarning && (
        <div
          role="presentation"
          onClick={() => setUnassignWarning(null)}
          style={{
            position: 'fixed',
            inset: 0,
            zIndex: 10000,
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            padding: 20,
            background: 'rgba(42, 30, 34, 0.58)',
          }}
        >
          <section
            role="alertdialog"
            aria-modal="true"
            aria-labelledby="admin-unassign-warning-title"
            aria-describedby="admin-unassign-warning-message"
            onClick={(event) => event.stopPropagation()}
            onKeyDown={(event) => {
              if (event.key === 'Escape') {
                setUnassignWarning(null)
              }
            }}
            style={{
              width: 'min(460px, 100%)',
              boxSizing: 'border-box',
              background: '#fffaf7',
              border: '1px solid #d8bfc4',
              borderTop: '5px solid #a63842',
              borderRadius: 18,
              padding: '28px 30px',
              boxShadow: '0 24px 60px rgba(35, 20, 25, 0.23)',
            }}
          >
            <h2
              id="admin-unassign-warning-title"
              style={{
                margin: '0 0 14px',
                color: '#733143',
                fontFamily: "'Cormorant Garamond', Georgia, serif",
                fontSize: '2rem',
                fontWeight: 600,
              }}
            >
              {unassignWarning.title}
            </h2>

            <p
              id="admin-unassign-warning-message"
              style={{
                margin: '0 0 24px',
                color: '#594a4a',
                fontFamily: "'Montserrat', Arial, sans-serif",
                fontSize: '0.92rem',
                lineHeight: 1.7,
              }}
            >
              {unassignWarning.message}
            </p>

            <div
              style={{
                display: 'flex',
                justifyContent: 'flex-end',
              }}
            >
              <button
                type="button"
                autoFocus
                className="admin-primary-button"
                onClick={() => setUnassignWarning(null)}
              >
                Close
              </button>
            </div>
          </section>
        </div>
      )}
    </div>
  )
}

export default AdminDashboard
