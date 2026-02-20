import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import api from '../api/axios'
import gsap from 'gsap'
import NotificationBell from '../components/NotificationBell'

const Dashboard = () => {
  const [projects, setProjects] = useState([])
  const [availableProjects, setAvailableProjects] = useState([])
  const [showModal, setShowModal] = useState(false)
  const [showRequestModal, setShowRequestModal] = useState(false)
  const [showJoinModal, setShowJoinModal] = useState(false)
  const [selectedProject, setSelectedProject] = useState(null)
  const [requestReason, setRequestReason] = useState('')
  const [canCreateProjects, setCanCreateProjects] = useState(false)
  const [pendingRequests, setPendingRequests] = useState([])
  const [activeTab, setActiveTab] = useState('projects') // 'projects', 'my-projects', or 'available'
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [technologyStack, setTechnologyStack] = useState('')
  const [teamSize, setTeamSize] = useState(1)
  const [teamEmails, setTeamEmails] = useState([])
  const { logout, token } = useAuth()
  const navigate = useNavigate()
  const projectsRef = useRef([])

  useEffect(() => {
    if (token) {
      fetchProjects()
      fetchAvailableProjects()
      checkPermissions()
    }
  }, [token])

  const fetchAvailableProjects = async () => {
    try {
      const response = await api.get('/projects/available')
      setAvailableProjects(response.data)
    } catch (err) {
      console.error('Failed to fetch available projects:', err)
    }
  }

  const checkPermissions = async () => {
    try {
      const response = await api.get('/auth/me')
      setCanCreateProjects(response.data.can_create_projects)
      
      // If user can create projects, fetch pending requests
      if (response.data.can_create_projects) {
        fetchPendingRequests()
      }
    } catch (err) {
      console.error('Failed to check permissions:', err)
    }
  }

  const fetchPendingRequests = async () => {
    try {
      const response = await api.get('/access-requests/pending')
      setPendingRequests(response.data)
    } catch (err) {
      console.error('Failed to fetch pending requests:', err)
    }
  }

  const handleApproveRequest = async (requestId, approved) => {
    try {
      await api.post('/access-requests/approve', {
        request_id: requestId,
        approved: approved
      })
      alert(approved ? 'Request approved!' : 'Request rejected!')
      fetchPendingRequests()
    } catch (err) {
      console.error('Failed to process request:', err)
      alert('Failed to process request')
    }
  }

  useEffect(() => {
    // Animate project cards when they load
    if (projects.length > 0) {
      gsap.fromTo(
        projectsRef.current,
        { 
          opacity: 0, 
          y: 50,
          scale: 0.9,
          rotateX: -15
        },
        {
          opacity: 1,
          y: 0,
          scale: 1,
          rotateX: 0,
          duration: 0.6,
          stagger: 0.1,
          ease: 'back.out(1.7)'
        }
      )
    }
  }, [projects])

  const fetchProjects = async () => {
    try {
      console.log('Fetching projects...')
      const response = await api.get('/projects')
      console.log('Projects fetched:', response.data)
      console.log('First project user_role:', response.data[0]?.user_role)
      setProjects(response.data)
    } catch (err) {
      console.error('Failed to fetch projects:', err.response?.status, err.response?.data)
      if (err.response?.status === 401) {
        console.error('Token invalid or missing')
      }
    }
  }

  const createProject = async (e) => {
    e.preventDefault()
    try {
      const response = await api.post('/projects', { 
        title, 
        description,
        start_date: startDate || null,
        end_date: endDate || null,
        technology_stack: technologyStack || null,
        team_size: parseInt(teamSize) || 1
      })
      
      // If team members were added, send their emails
      if (teamEmails.length > 0) {
        const validEmails = teamEmails.filter(email => email.trim() !== '')
        if (validEmails.length > 0) {
          try {
            await api.post(`/projects/${response.data.id}/members`, {
              emails: validEmails
            })
          } catch (err) {
            console.error('Failed to add team members:', err)
          }
        }
      }
      
      setShowModal(false)
      setTitle('')
      setDescription('')
      setStartDate('')
      setEndDate('')
      setTechnologyStack('')
      setTeamSize(1)
      setTeamEmails([])
      fetchProjects()
    } catch (err) {
      console.error('Failed to create project', err)
    }
  }

  const handleTeamSizeChange = (e) => {
    const size = parseInt(e.target.value) || 1
    setTeamSize(size)
    
    // Adjust team emails array (excluding the leader)
    const memberCount = size - 1
    if (memberCount > 0) {
      setTeamEmails(Array(memberCount).fill(''))
    } else {
      setTeamEmails([])
    }
  }

  const updateTeamEmail = (index, value) => {
    const newEmails = [...teamEmails]
    newEmails[index] = value
    setTeamEmails(newEmails)
  }

  const requestProjectAccess = async (e) => {
    e.preventDefault()
    try {
      const payload = {
        reason: requestReason
      }
      
      // If joining a specific project, include project_id
      if (selectedProject) {
        payload.project_id = selectedProject.id
      }
      
      const response = await api.post('/access-requests', payload)
      console.log('Request sent successfully:', response.data)
      alert(selectedProject 
        ? `Request to join "${selectedProject.title}" sent!` 
        : 'Request sent! A project leader will review your request.')
      setShowRequestModal(false)
      setShowJoinModal(false)
      setRequestReason('')
      setSelectedProject(null)
    } catch (err) {
      console.error('Failed to send request:', err)
      console.error('Error response:', err.response)
      if (err.response?.data?.detail) {
        alert(err.response.data.detail)
      } else {
        alert('Failed to send request: ' + (err.message || 'Unknown error'))
      }
    }
  }

  const openJoinModal = (project) => {
    setSelectedProject(project)
    setShowJoinModal(true)
  }

  const handleDeleteProject = async (projectId, e) => {
    e.stopPropagation() // Prevent navigation
    if (!window.confirm('Are you sure you want to delete this project?')) {
      return
    }
    
    try {
      await api.delete(`/projects/${projectId}`)
      alert('Project deleted successfully')
      fetchProjects()
    } catch (err) {
      console.error('Failed to delete project:', err)
      alert('Failed to delete project: ' + (err.response?.data?.detail || err.message))
    }
  }

  const myProjects = projects.filter(p => p.user_role === 'leader')
  const allProjects = projects

  return (
    <div>
      <div className="navbar">
        <h1>TaskHive Dashboard</h1>
        <div className="navbar-actions">
          <NotificationBell />
          <button onClick={logout}>Logout</button>
        </div>
      </div>
      <div className="container">
        <button className="btn" onClick={() => setShowModal(true)}>Create Project</button>

        {/* Tabs */}
        <div className="tabs" style={{marginTop: '24px', marginBottom: '24px'}}>
          <button 
            className={`tab-button ${activeTab === 'projects' ? 'active' : ''}`}
            onClick={() => setActiveTab('projects')}
          >
            All Projects ({allProjects.length})
          </button>
          {canCreateProjects && (
            <button 
              className={`tab-button ${activeTab === 'my-projects' ? 'active' : ''}`}
              onClick={() => setActiveTab('my-projects')}
            >
              My Projects ({myProjects.length})
            </button>
          )}
          <button 
            className={`tab-button ${activeTab === 'available' ? 'active' : ''}`}
            onClick={() => setActiveTab('available')}
          >
            Available Projects ({availableProjects.length})
          </button>
        </div>

        {/* Pending Access Requests Section (for leaders only) */}
        {canCreateProjects && pendingRequests.length > 0 && (
          <div className="pending-requests-section">
            <h2 style={{color: '#ef4444', marginBottom: '20px', fontSize: '20px'}}>
              📋 Pending Access Requests ({pendingRequests.length})
            </h2>
            <div className="requests-list">
              {pendingRequests.map((request) => (
                <div key={request.id} className="request-card">
                  <div className="request-header">
                    <div>
                      <h3 style={{color: '#fff', marginBottom: '5px'}}>{request.requester_name}</h3>
                      <p style={{color: '#9ca3af', fontSize: '14px'}}>{request.requester_email}</p>
                    </div>
                    <span className="request-badge">
                      {request.request_type === 'create_project' 
                        ? '🔑 Project Creation' 
                        : `📁 Join: ${request.project_title}`}
                    </span>
                  </div>
                  {request.reason && (
                    <div className="request-reason">
                      <strong style={{color: '#ef4444'}}>Reason:</strong>
                      <p style={{color: '#e4e6eb', marginTop: '5px'}}>{request.reason}</p>
                    </div>
                  )}
                  <div className="request-date">
                    <span style={{color: '#9ca3af', fontSize: '12px'}}>
                      Requested on {new Date(request.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  <div className="request-actions">
                    <button 
                      className="btn btn-approve"
                      onClick={() => handleApproveRequest(request.id, true)}
                    >
                      ✓ Approve
                    </button>
                    <button 
                      className="btn btn-reject"
                      onClick={() => handleApproveRequest(request.id, false)}
                    >
                      ✗ Reject
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="projects-grid">
          {activeTab === 'available' ? (
            // Show available projects with "Request to Join" button
            availableProjects.map((project, index) => (
              <div
                key={project.id}
                ref={el => projectsRef.current[index] = el}
                className="project-card available-project-card"
                style={{cursor: 'default', border: '2px solid #2a2a2a'}}
              >
                <div className="project-header">
                  <h3>{project.title}</h3>
                  <button
                    className="btn btn-secondary"
                    onClick={() => openJoinModal(project)}
                    style={{
                      padding: '6px 12px',
                      fontSize: '12px',
                      width: 'auto',
                      background: '#ef4444',
                      color: '#fff'
                    }}
                  >
                    📩 Request to Join
                  </button>
                </div>
                
                {/* Project Description */}
                <div style={{
                  background: '#1a1a1a',
                  padding: '12px',
                  borderRadius: '8px',
                  marginBottom: '12px',
                  borderLeft: '3px solid #ef4444'
                }}>
                  <p style={{color: '#e4e6eb', fontSize: '14px', lineHeight: '1.6'}}>
                    {project.description || 'No description provided'}
                  </p>
                </div>
                
                {/* Technology Stack */}
                {project.technology_stack && (
                  <div style={{
                    marginBottom: '12px',
                    padding: '10px',
                    background: '#0f0f0f',
                    borderRadius: '6px'
                  }}>
                    <div style={{
                      fontSize: '11px',
                      color: '#9ca3af',
                      textTransform: 'uppercase',
                      letterSpacing: '0.5px',
                      marginBottom: '6px',
                      fontWeight: '600'
                    }}>
                      🛠️ Tech Stack
                    </div>
                    <div style={{
                      display: 'flex',
                      flexWrap: 'wrap',
                      gap: '6px'
                    }}>
                      {project.technology_stack.split(',').map((tech, i) => (
                        <span key={i} style={{
                          background: '#2a2a2a',
                          color: '#ef4444',
                          padding: '4px 10px',
                          borderRadius: '12px',
                          fontSize: '12px',
                          fontWeight: '500'
                        }}>
                          {tech.trim()}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                
                {/* Project Info Grid */}
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: '1fr 1fr',
                  gap: '10px',
                  marginBottom: '12px'
                }}>
                  {/* Owner */}
                  <div style={{
                    background: '#0f0f0f',
                    padding: '10px',
                    borderRadius: '6px'
                  }}>
                    <div style={{
                      fontSize: '11px',
                      color: '#9ca3af',
                      marginBottom: '4px'
                    }}>
                      👤 Project Owner
                    </div>
                    <div style={{
                      color: '#fff',
                      fontSize: '13px',
                      fontWeight: '600'
                    }}>
                      {project.owner_name}
                    </div>
                  </div>
                  
                  {/* Team Size */}
                  {project.team_size && (
                    <div style={{
                      background: '#0f0f0f',
                      padding: '10px',
                      borderRadius: '6px'
                    }}>
                      <div style={{
                        fontSize: '11px',
                        color: '#9ca3af',
                        marginBottom: '4px'
                      }}>
                        👥 Team Size
                      </div>
                      <div style={{
                        color: '#fff',
                        fontSize: '13px',
                        fontWeight: '600'
                      }}>
                        {project.team_size} members
                      </div>
                    </div>
                  )}
                </div>
                
                {/* Created Date */}
                <div style={{
                  fontSize: '12px',
                  color: '#6b7280',
                  marginTop: '8px',
                  paddingTop: '8px',
                  borderTop: '1px solid #2a2a2a'
                }}>
                  📅 Created {new Date(project.created_at).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric'
                  })}
                </div>
              </div>
            ))
          ) : (
            // Show user's projects
            (activeTab === 'projects' ? allProjects : myProjects).map((project, index) => (
            <div
              key={project.id}
              ref={el => projectsRef.current[index] = el}
              className="project-card"
              onClick={() => navigate(`/board/${project.id}`)}
              onMouseEnter={(e) => {
                gsap.to(e.currentTarget, {
                  scale: 1.05,
                  rotateY: 5,
                  duration: 0.3,
                  ease: 'power2.out'
                })
              }}
              onMouseLeave={(e) => {
                gsap.to(e.currentTarget, {
                  scale: 1,
                  rotateY: 0,
                  duration: 0.3,
                  ease: 'power2.out'
                })
              }}
            >
              <div className="project-header">
                <h3>{project.title}</h3>
                <div style={{display: 'flex', gap: '8px', alignItems: 'center', flexWrap: 'wrap'}}>
                  {project.user_role && (
                    <span className={`role-badge ${project.user_role}`}>
                      {project.user_role === 'leader' ? '👑 Leader' : '👤 Member'}
                    </span>
                  )}
                  {/* Debug: Show role value */}
                  <span style={{fontSize: '10px', color: '#666'}}>
                    Role: {project.user_role || 'undefined'}
                  </span>
                  {/* Show delete button for leaders OR if role is undefined (for debugging) */}
                  {(project.user_role === 'leader' || !project.user_role) && (
                    <button
                      className="delete-btn"
                      onClick={(e) => handleDeleteProject(project.id, e)}
                      title="Delete this project (soft delete)"
                      style={{
                        background: '#dc2626',
                        color: '#fff',
                        border: '1px solid #ef4444',
                        borderRadius: '6px',
                        padding: '6px 12px',
                        cursor: 'pointer',
                        fontSize: '12px',
                        fontWeight: '600',
                        transition: 'all 0.2s',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px',
                        zIndex: 10
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.background = '#b91c1c'
                        e.currentTarget.style.transform = 'scale(1.05)'
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.background = '#dc2626'
                        e.currentTarget.style.transform = 'scale(1)'
                      }}
                    >
                      🗑️ Delete
                    </button>
                  )}
                </div>
              </div>
              <p>{project.description}</p>
              
              {activeTab === 'my-projects' && (
                <div className="project-timestamp" style={{
                  fontSize: '12px',
                  color: '#9ca3af',
                  marginTop: '8px',
                  padding: '8px',
                  background: '#1a1a1a',
                  borderRadius: '4px'
                }}>
                  <div>📅 Created: {new Date(project.created_at).toLocaleString()}</div>
                  <div>🔄 Updated: {new Date(project.updated_at).toLocaleString()}</div>
                </div>
              )}
              
              {project.technology_stack && (
                <div className="project-tech">
                  <span className="tech-label">Tech:</span> {project.technology_stack}
                </div>
              )}
              
              {project.team_size && (
                <div className="project-team">
                  <span className="team-icon">👥</span> {project.team_size} members
                </div>
              )}
              
              {(project.start_date || project.end_date) && (
                <div className="project-dates">
                  {project.start_date && <span>📅 {new Date(project.start_date).toLocaleDateString()}</span>}
                  {project.end_date && <span> → {new Date(project.end_date).toLocaleDateString()}</span>}
                </div>
              )}
              
              <div className="progress-section">
                <div className="progress-header">
                  <span>Progress</span>
                  <span className="progress-percentage">{project.progress || 0}%</span>
                </div>
                <div className="progress-bar">
                  <div 
                    className="progress-fill" 
                    style={{width: `${project.progress || 0}%`}}
                  ></div>
                </div>
              </div>
            </div>
          ))
          )}
        </div>
      </div>

      {showModal && (
        <div className="modal" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>Create New Project</h2>
            <form onSubmit={createProject}>
              <div className="form-group">
                <label>Project Title</label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g., E-commerce Platform"
                  required
                />
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Brief description of the project..."
                  rows="3"
                />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Start Date</label>
                  <input
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label>End Date</label>
                  <input
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                  />
                </div>
              </div>
              <div className="form-group">
                <label>Technology Stack</label>
                <input
                  type="text"
                  value={technologyStack}
                  onChange={(e) => setTechnologyStack(e.target.value)}
                  placeholder="e.g., React, Node.js, PostgreSQL"
                />
              </div>
              <div className="form-group">
                <label>Team Size</label>
                <input
                  type="number"
                  value={teamSize}
                  onChange={handleTeamSizeChange}
                  min="1"
                  max="50"
                />
              </div>
              
              {teamEmails.length > 0 && (
                <div className="form-group">
                  <label>Team Member Emails (excluding you as leader)</label>
                  {teamEmails.map((email, index) => (
                    <input
                      key={index}
                      type="email"
                      value={email}
                      onChange={(e) => updateTeamEmail(index, e.target.value)}
                      placeholder={`Team member ${index + 1} email`}
                      className="team-email-input"
                    />
                  ))}
                </div>
              )}
              <button type="submit" className="btn">Create Project</button>
            </form>
          </div>
        </div>
      )}

      {showRequestModal && (
        <div className="modal" onClick={() => setShowRequestModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>Request Project Creation Access</h2>
            <p style={{color: '#9ca3af', marginBottom: '20px', fontSize: '14px'}}>
              You need permission from a project leader to create projects. 
              Please explain why you need this access.
            </p>
            <form onSubmit={requestProjectAccess}>
              <div className="form-group">
                <label>Reason for Request</label>
                <textarea
                  value={requestReason}
                  onChange={(e) => setRequestReason(e.target.value)}
                  placeholder="e.g., I want to create a project for our new mobile app development..."
                  rows="4"
                  required
                />
              </div>
              <button type="submit" className="btn">Send Request</button>
            </form>
          </div>
        </div>
      )}
      {showJoinModal && selectedProject && (
        <div className="modal" onClick={() => setShowJoinModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>Request to Join Project</h2>
            <p style={{color: '#9ca3af', marginBottom: '20px', fontSize: '14px'}}>
              You are requesting to join: <strong style={{color: '#ef4444'}}>{selectedProject.title}</strong>
            </p>
            <form onSubmit={requestProjectAccess}>
              <div className="form-group">
                <label>Reason for Request</label>
                <textarea
                  value={requestReason}
                  onChange={(e) => setRequestReason(e.target.value)}
                  placeholder="e.g., I have experience with React and would like to contribute..."
                  rows="4"
                  required
                />
              </div>
              <button type="submit" className="btn">Send Request</button>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default Dashboard
