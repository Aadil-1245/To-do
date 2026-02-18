import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd'
import api from '../api/axios'
import NotificationBell from '../components/NotificationBell'

const KanbanBoard = () => {
  const [board, setBoard] = useState([])
  const [showModal, setShowModal] = useState(false)
  const [showCommentsModal, setShowCommentsModal] = useState(false)
  const [showColumnModal, setShowColumnModal] = useState(false)
  const [selectedTask, setSelectedTask] = useState(null)
  const [comments, setComments] = useState([])
  const [newComment, setNewComment] = useState('')
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [selectedStatus, setSelectedStatus] = useState(null)
  const [assignedTo, setAssignedTo] = useState('')
  const [teamMembers, setTeamMembers] = useState([])
  const [currentUserId, setCurrentUserId] = useState(null)
  const [userRole, setUserRole] = useState(null)
  const [newColumnName, setNewColumnName] = useState('')
  const { projectId } = useParams()
  const navigate = useNavigate()

  useEffect(() => {
    fetchBoard()
    fetchTeamMembers()
  }, [projectId])

  const fetchBoard = async () => {
    try {
      const response = await api.get(`/tasks/board/${projectId}`)
      console.log('📊 Raw API response:', response.data)
      
      // Normalize data - ensure all IDs are numbers
      const normalizedBoard = response.data.map(col => ({
        status_id: Number(col.status_id),
        status_name: col.status_name,
        user_role: col.user_role,
        current_user_id: Number(col.current_user_id),
        tasks: (col.tasks || []).map(task => ({
          id: Number(task.id),
          title: task.title,
          description: task.description,
          status_id: Number(task.status_id),
          assigned_to: task.assigned_to ? Number(task.assigned_to) : null,
          assigned_user_name: task.assigned_user_name || null,
          assigned_user_email: task.assigned_user_email || null
        }))
      }))
      
      console.log('✅ Normalized board:', normalizedBoard)
      setBoard(normalizedBoard)
      
      if (normalizedBoard.length > 0) {
        setSelectedStatus(normalizedBoard[0].status_id)
        setUserRole(normalizedBoard[0].user_role)
        setCurrentUserId(normalizedBoard[0].current_user_id)
      }
    } catch (err) {
      console.error('❌ Failed to fetch board:', err)
    }
  }

  const fetchTeamMembers = async () => {
    try {
      const response = await api.get(`/projects/${projectId}/members`)
      setTeamMembers(response.data || [])
    } catch (err) {
      console.error('Failed to fetch team members:', err)
    }
  }

  const createColumn = async (e) => {
    e.preventDefault()
    if (!newColumnName.trim()) {
      alert('Please enter a column name')
      return
    }

    try {
      const response = await api.post('/statuses', {
        name: newColumnName,
        position: crypto.randomUUID(),
        project_id: parseInt(projectId)
      })
      console.log('✅ Column created:', response.data)
      
      // Add new column to board
      const newColumn = {
        status_id: response.data.id,
        status_name: response.data.name,
        user_role: userRole,
        current_user_id: currentUserId,
        tasks: []
      }
      setBoard([...board, newColumn])
      setNewColumnName('')
      setShowColumnModal(false)
      alert('Column created successfully!')
    } catch (err) {
      console.error('Failed to create column:', err)
      alert('Failed to create column: ' + (err.response?.data?.detail || err.message))
    }
  }

  const createTask = async (e) => {
    e.preventDefault()
    try {
      await api.post('/tasks', {
        title,
        description,
        status_id: selectedStatus,
        project_id: parseInt(projectId),
        assigned_to: assignedTo ? parseInt(assignedTo) : null
      })
      setShowModal(false)
      setTitle('')
      setDescription('')
      setAssignedTo('')
      fetchBoard()
    } catch (err) {
      console.error('Failed to create task:', err)
      alert('Failed to create task: ' + (err.response?.data?.detail || err.message))
    }
  }

  const onDragEnd = async (result) => {
    console.log('🎯 Drag result:', result)
    
    if (!result.destination) {
      console.log('❌ No destination')
      return
    }

    const { source, destination } = result
    
    // If dropped in same column, do nothing
    if (source.droppableId === destination.droppableId) {
      console.log('ℹ️ Same column, no action needed')
      return
    }

    const taskId = Number(result.draggableId)
    const sourceColId = Number(source.droppableId)
    const destColId = Number(destination.droppableId)
    
    console.log('📦 Moving task:', taskId, 'from', sourceColId, 'to', destColId)

    // Find the task
    let taskToMove = null
    for (const col of board) {
      const found = col.tasks.find(t => t.id === taskId)
      if (found) {
        taskToMove = found
        break
      }
    }

    if (!taskToMove) {
      console.error('❌ Task not found!')
      return
    }

    console.log('✅ Task found:', taskToMove)

    // Update UI immediately (optimistic update)
    const newBoard = board.map(col => {
      if (col.status_id === sourceColId) {
        // Remove from source
        return {
          ...col,
          tasks: col.tasks.filter(t => t.id !== taskId)
        }
      } else if (col.status_id === destColId) {
        // Add to destination
        return {
          ...col,
          tasks: [...col.tasks, { ...taskToMove, status_id: destColId }]
        }
      }
      return col
    })

    console.log('🚀 Setting new board state')
    setBoard(newBoard)

    // Update backend
    try {
      await api.patch(`/tasks/${taskId}/move`, {
        new_status_id: destColId
      })
      console.log('✅ Backend updated successfully')
    } catch (err) {
      console.error('❌ Backend update failed:', err)
      alert('Failed to move task: ' + (err.response?.data?.detail || err.message))
      // Revert on error
      fetchBoard()
    }
  }

  const openCommentsModal = async (task) => {
    setSelectedTask(task)
    setShowCommentsModal(true)
    await fetchComments(task.id)
  }

  const fetchComments = async (taskId) => {
    try {
      const response = await api.get(`/tasks/${taskId}/comments`)
      setComments(response.data)
    } catch (err) {
      console.error('Failed to fetch comments:', err)
    }
  }

  const addComment = async (e) => {
    e.preventDefault()
    if (!newComment.trim()) return
    
    try {
      await api.post(`/tasks/${selectedTask.id}/comments`, {
        comment: newComment
      })
      setNewComment('')
      await fetchComments(selectedTask.id)
    } catch (err) {
      console.error('Failed to add comment:', err)
    }
  }

  return (
    <div>
      <div className="navbar">
        <h1>
          TaskHive Board 
          {userRole && (
            <span className={`role-badge ${userRole}`} style={{marginLeft: '12px', fontSize: '12px'}}>
              {userRole === 'leader' ? '👑 Leader' : '👤 Member'}
            </span>
          )}
        </h1>
        <div className="navbar-actions">
          <NotificationBell />
          {userRole === 'leader' && (
            <>
              <button className="btn add-task" onClick={() => setShowModal(true)} style={{marginRight: '10px', width: 'auto'}}>
                + Add Task
              </button>
              <button className="btn add-task" onClick={() => setShowColumnModal(true)} style={{marginRight: '10px', width: 'auto', background: '#8b5cf6'}}>
                + Add Column
              </button>
            </>
          )}
          <button onClick={() => navigate('/dashboard')} style={{width: 'auto'}}>Back to Dashboard</button>
        </div>
      </div>

      <div className="container">
        <DragDropContext onDragEnd={onDragEnd}>
          <div className="kanban-board">
            {board.map((column) => (
              <Droppable key={column.status_id} droppableId={String(column.status_id)}>
                {(provided, snapshot) => (
                  <div
                    className="kanban-column"
                    ref={provided.innerRef}
                    {...provided.droppableProps}
                    style={{
                      background: snapshot.isDraggingOver ? 'rgba(239, 68, 68, 0.05)' : '#1a1a1a',
                      borderColor: snapshot.isDraggingOver ? '#ef4444' : '#2a2a2a'
                    }}
                  >
                    <h3>{column.status_name}</h3>
                    
                    {column.tasks.map((task, index) => (
                      <Draggable
                        key={task.id}
                        draggableId={String(task.id)}
                        index={index}
                      >
                        {(provided, snapshot) => (
                          <div
                            className="task-card"
                            ref={provided.innerRef}
                            {...provided.draggableProps}
                            {...provided.dragHandleProps}
                            style={{
                              ...provided.draggableProps.style,
                              opacity: snapshot.isDragging ? 0.8 : 1,
                              boxShadow: snapshot.isDragging 
                                ? '0 8px 20px rgba(239, 68, 68, 0.4)' 
                                : '0 2px 8px rgba(0,0,0,0.3)'
                            }}
                            onClick={(e) => {
                              if (!snapshot.isDragging) {
                                e.stopPropagation()
                                openCommentsModal(task)
                              }
                            }}
                          >
                            <h4>{task.title}</h4>
                            <p>{task.description}</p>
                            
                            {task.assigned_user_name ? (
                              <div style={{
                                marginTop: '8px',
                                padding: '4px 8px',
                                background: '#2a2a2a',
                                borderRadius: '4px',
                                fontSize: '12px',
                                color: '#9ca3af'
                              }}>
                                👤 {task.assigned_user_name}
                              </div>
                            ) : (
                              <div style={{
                                marginTop: '8px',
                                padding: '4px 8px',
                                background: '#2a2a2a',
                                borderRadius: '4px',
                                fontSize: '12px',
                                color: '#6b7280'
                              }}>
                                👤 Unassigned
                              </div>
                            )}
                            
                            <div className="task-meta">
                              <span className="comment-count">💬 Comments</span>
                            </div>
                          </div>
                        )}
                      </Draggable>
                    ))}
                    
                    {provided.placeholder}
                  </div>
                )}
              </Droppable>
            ))}
          </div>
        </DragDropContext>
      </div>

      {/* Create Task Modal */}
      {showModal && (
        <div className="modal" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>Create New Task</h2>
            <form onSubmit={createTask}>
              <div className="form-group">
                <label>Title</label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  required
                />
              </div>
              <div className="form-group">
                <label>Description</label>
                <input
                  type="text"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                />
              </div>
              <div className="form-group">
                <label>Status</label>
                <select
                  value={selectedStatus}
                  onChange={(e) => setSelectedStatus(parseInt(e.target.value))}
                  required
                >
                  {board.map(column => (
                    <option key={column.status_id} value={column.status_id}>
                      {column.status_name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Assign To</label>
                <select
                  value={assignedTo}
                  onChange={(e) => setAssignedTo(e.target.value)}
                  required
                >
                  <option value="">Select team member...</option>
                  {teamMembers.map(member => (
                    <option key={member.id} value={member.id}>
                      {member.name} ({member.email})
                    </option>
                  ))}
                </select>
              </div>
              <button type="submit" className="btn">Create</button>
            </form>
          </div>
        </div>
      )}

      {/* Comments Modal */}
      {showCommentsModal && selectedTask && (
        <div className="modal" onClick={() => setShowCommentsModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>{selectedTask.title}</h2>
            <p style={{color: '#9ca3af', marginBottom: '20px'}}>{selectedTask.description}</p>
            
            <div className="comments-section">
              <h3 style={{fontSize: '14px', marginBottom: '16px', color: '#fff'}}>Comments</h3>
              
              <div className="comments-list">
                {comments.length === 0 ? (
                  <p style={{color: '#6b7280', fontSize: '13px', textAlign: 'center', padding: '20px'}}>
                    No comments yet. Be the first to comment!
                  </p>
                ) : (
                  comments.map(comment => (
                    <div key={comment.id} className="comment-item">
                      <div className="comment-header">
                        <span className="comment-author">{comment.user_name}</span>
                        <span className="comment-date">
                          {new Date(comment.created_at).toLocaleDateString()}
                        </span>
                      </div>
                      <p className="comment-text">{comment.comment}</p>
                    </div>
                  ))
                )}
              </div>

              <form onSubmit={addComment} className="comment-form">
                <textarea
                  value={newComment}
                  onChange={(e) => setNewComment(e.target.value)}
                  placeholder="Add a comment..."
                  rows="3"
                  style={{marginBottom: '12px'}}
                />
                <button type="submit" className="btn">Add Comment</button>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Create Column Modal */}
      {showColumnModal && (
        <div className="modal" onClick={() => setShowColumnModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>Create New Column</h2>
            <form onSubmit={createColumn}>
              <div className="form-group">
                <label>Column Name</label>
                <input
                  type="text"
                  value={newColumnName}
                  onChange={(e) => setNewColumnName(e.target.value)}
                  placeholder="e.g., Review, Testing, etc."
                  required
                  autoFocus
                />
              </div>
              <div style={{display: 'flex', gap: '10px', justifyContent: 'flex-end'}}>
                <button type="button" className="btn" onClick={() => {setShowColumnModal(false); setNewColumnName('')}} style={{background: '#6b7280'}}>Cancel</button>
                <button type="submit" className="btn" style={{background: '#8b5cf6'}}>Create Column</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default KanbanBoard
