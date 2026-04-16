import React, { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [playerName, setPlayerName] = useState('')
  const [gameStarted, setGameStarted] = useState(false)
  const [groups, setGroups] = useState({})
  const [selectedGroup, setSelectedGroup] = useState(null)
  const [groupCharacters, setGroupCharacters] = useState([])
  const [selectedCharacter, setSelectedCharacter] = useState(null)
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [editingIndex, setEditingIndex] = useState(null)
  const [editingContent, setEditingContent] = useState('')
  const [savedConversations, setSavedConversations] = useState([])
  const [showSavedConversations, setShowSavedConversations] = useState(false)
  const [customTitle, setCustomTitle] = useState('')
  const [showSaveDialog, setShowSaveDialog] = useState(false)

  // Fetch character groups from backend
  useEffect(() => {
    const fetchGroups = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/groups')
        const data = await response.json()
        setGroups(data.groups || {})
      } catch (error) {
        console.error('Error fetching groups:', error)
      }
    }
    if (gameStarted) {
      fetchGroups()
    }
  }, [gameStarted])

  // Fetch characters when a group is selected
  useEffect(() => {
    const fetchGroupCharacters = async () => {
      if (!selectedGroup) return
      try {
        const response = await fetch(`http://localhost:8000/api/groups/${selectedGroup}`)
        const data = await response.json()
        setGroupCharacters(data.characters || [])
      } catch (error) {
        console.error(`Error fetching group ${selectedGroup}:`, error)
      }
    }
    if (selectedGroup) {
      fetchGroupCharacters()
    }
  }, [selectedGroup])

  const startGame = (name) => {
    if (name.trim()) {
      setPlayerName(name)
      setGameStarted(true)
      // Save player name to localStorage for future sessions
      localStorage.setItem('playerName', name)
    }
  }

  // Load player name from localStorage on first load
  useEffect(() => {
    const savedPlayerName = localStorage.getItem('playerName')
    if (savedPlayerName) {
      setPlayerName(savedPlayerName)
    }
  }, [])

  const selectGroup = (groupId) => {
    setSelectedGroup(groupId)
    setGroupCharacters([])
  }

  // Load messages from localStorage when component mounts or selectedCharacter changes
  useEffect(() => {
    if (selectedCharacter) {
      const storageKey = `conversation_${playerName}_${selectedCharacter}`
      const savedMessages = localStorage.getItem(storageKey)
      if (savedMessages) {
        try {
          setMessages(JSON.parse(savedMessages))
        } catch (error) {
          console.error('Error loading messages from localStorage:', error)
          setMessages([])
        }
      }
    }
  }, [selectedCharacter, playerName])

  // Save messages to localStorage whenever they change
  useEffect(() => {
    if (selectedCharacter && messages.length > 0) {
      const storageKey = `conversation_${playerName}_${selectedCharacter}`
      localStorage.setItem(storageKey, JSON.stringify(messages))
    }
  }, [messages, selectedCharacter, playerName])

  const selectCharacter = (character) => {
    setSelectedCharacter(character)
    // Don't clear messages - they'll be loaded from localStorage
    setInputMessage('')
    setEditingIndex(null)
    setEditingContent('')
  }

  const clearConversation = () => {
    if (!window.confirm('Are you sure you want to clear this conversation? This cannot be undone.')) {
      return
    }
    setMessages([])
    // Also clear from localStorage
    const storageKey = `conversation_${playerName}_${selectedCharacter}`
    localStorage.removeItem(storageKey)
  }

  const copyToClipboard = (content) => {
    navigator.clipboard.writeText(content).then(() => {
      alert('Message copied to clipboard!')
    }).catch(() => {
      alert('Failed to copy message')
    })
  }

  const startEdit = (index, content) => {
    setEditingIndex(index)
    setEditingContent(content)
  }

  const cancelEdit = () => {
    setEditingIndex(null)
    setEditingContent('')
  }

  const saveEdit = (index) => {
    if (!editingContent.trim()) {
      alert('Message cannot be empty')
      return
    }
    const updatedMessages = [...messages]
    updatedMessages[index].content = editingContent
    setMessages(updatedMessages)
    setEditingIndex(null)
    setEditingContent('')
  }

  const regenerateResponse = async (index) => {
    // Find the last player message before this index
    let playerMessageIndex = -1
    for (let i = index - 1; i >= 0; i--) {
      if (messages[i].role === 'player') {
        playerMessageIndex = i
        break
      }
    }

    if (playerMessageIndex === -1) return

    const playerMessage = messages[playerMessageIndex].content
    
    // Remove all messages after and including this character response
    const newMessages = messages.slice(0, index)
    setMessages(newMessages)
    setLoading(true)

    try {
      const response = await fetch('http://localhost:8000/api/dialogue', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          player_name: playerName,
          character_id: selectedCharacter,
          message: playerMessage,
        }),
      })
      const data = await response.json()
      const characterMessage = {
        role: 'character',
        content: data.response || 'No response',
        illustrations: data.illustrations || [],
        character: selectedCharacter,
      }
      setMessages((prev) => [...prev, characterMessage])
    } catch (error) {
      console.error('Error regenerating response:', error)
      setMessages((prev) => [
        ...prev,
        { role: 'error', content: 'Failed to regenerate response' },
      ])
    } finally {
      setLoading(false)
    }
  }

  const forwardConversation = () => {
    const conversationText = messages
      .map((msg) => {
        const sender =
          msg.role === 'player'
            ? playerName
            : selectedCharacter.charAt(0).toUpperCase() + selectedCharacter.slice(1)
        return `${sender}: ${msg.content}`
      })
      .join('\n\n')

    const fullText = `Conversation with ${
      selectedCharacter.charAt(0).toUpperCase() + selectedCharacter.slice(1)
    }\n=====================================\n\n${conversationText}`

    const blob = new Blob([fullText], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `conversation-${selectedCharacter}-${new Date().toISOString().split('T')[0]}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const saveConversation = async () => {
    if (!messages.length) {
      alert('There are no messages to save')
      return
    }

    try {
      const response = await fetch('http://localhost:8000/api/conversations/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          player_name: playerName,
          character_id: selectedCharacter,
          messages: messages,
          conversation_title: customTitle || `Chat with ${selectedCharacter.charAt(0).toUpperCase() + selectedCharacter.slice(1)}`
        }),
      })

      const data = await response.json()
      if (data.success) {
        alert('Conversation saved successfully!')
        setShowSaveDialog(false)
        setCustomTitle('')
        await loadUserConversations()
      } else {
        alert('Failed to save conversation')
      }
    } catch (error) {
      console.error('Error saving conversation:', error)
      alert('Error saving conversation')
    }
  }

  const loadUserConversations = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/conversations?player_name=${encodeURIComponent(playerName)}`)
      const data = await response.json()
      setSavedConversations(data.conversations || [])
    } catch (error) {
      console.error('Error loading conversations:', error)
    }
  }

  const loadConversation = async (conversationId) => {
    try {
      const response = await fetch(`http://localhost:8000/api/conversations/${conversationId}`)
      const data = await response.json()
      
      // Load the conversation into the current dialogue
      setMessages(data.messages)
      setShowSavedConversations(false)
      window.scrollTo(0, document.querySelector('.dialogue-window').offsetTop)
    } catch (error) {
      console.error('Error loading conversation:', error)
      alert('Error loading conversation')
    }
  }

  const deleteConversation = async (conversationId) => {
    if (!window.confirm('Are you sure you want to delete this conversation?')) return

    try {
      const response = await fetch(`http://localhost:8000/api/conversations/${conversationId}`, {
        method: 'DELETE'
      })

      const data = await response.json()
      if (data.success) {
        await loadUserConversations()
        alert('Conversation deleted successfully')
      } else {
        alert('Failed to delete conversation')
      }
    } catch (error) {
      console.error('Error deleting conversation:', error)
      alert('Error deleting conversation')
    }
  }

  const sendMessage = async (e) => {
    e.preventDefault()
    if (!inputMessage.trim() || !selectedCharacter) return

    // Capture the message before clearing it
    const messageToSend = inputMessage

    const userMessage = {
      role: 'player',
      content: messageToSend,
    }

    setMessages([...messages, userMessage])
    setInputMessage('')
    setLoading(true)

    try {
      const response = await fetch('http://localhost:8000/api/dialogue', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          player_name: playerName,
          character_id: selectedCharacter,
          message: messageToSend,
        }),
      })
      const data = await response.json()
      const characterMessage = {
        role: 'character',
        content: data.response || 'No response',
        illustrations: data.illustrations || [],
        character: selectedCharacter,
      }
      setMessages((prev) => [...prev, characterMessage])
    } catch (error) {
      console.error('Error sending message:', error)
      setMessages((prev) => [
        ...prev,
        { role: 'error', content: 'Failed to get response' },
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="header">
        <h1>📖 Bible Learning Game</h1>
        <p className="subtitle">An immersive journey through Scripture</p>
      </header>

      {!gameStarted ? (
        <div className="character-creation">
          <h2>Begin Thy Journey</h2>
          <input
            type="text"
            placeholder="Enter thy name, traveler..."
            value={playerName}
            onChange={(e) => setPlayerName(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && startGame(playerName)}
          />
          <button onClick={() => startGame(playerName)}>Start Quest</button>
        </div>
      ) : !selectedGroup ? (
        <div className="game-container">
          <h2>Welcome, {playerName}!</h2>
          <p>Choose a knowledge path to explore Scripture:</p>
          <div className="groups-list">
            {Object.entries(groups).length > 0 ? (
              Object.entries(groups).map(([groupId, groupData]) => (
                <button
                  key={groupId}
                  className="group-btn"
                  onClick={() => selectGroup(groupId)}
                  title={groupData.description}
                >
                  <strong>{groupData.name}</strong>
                  <span>{groupData.description}</span>
                </button>
              ))
            ) : (
              <p>Loading knowledge paths...</p>
            )}
          </div>
        </div>
      ) : !selectedCharacter ? (
        <div className="game-container">
          <h2>Welcome, {playerName}!</h2>
          <button className="back-btn" onClick={() => setSelectedGroup(null)}>← Choose Different Path</button>
          <p>Select a teacher from {groups[selectedGroup]?.name}:</p>
          <div className="character-list">
            {groupCharacters.length > 0 ? (
              groupCharacters.map((char) => (
                <button
                  key={char.id}
                  className="character-btn"
                  onClick={() => selectCharacter(char.id)}
                >
                  <div className="character-avatar">{char.avatar}</div>
                  <div className="character-info">
                    <strong>{char.name}</strong>
                    <span className="character-title">{char.title}</span>
                    <span className="character-profile">{char.personality}</span>
                    {(char.birth_date || char.death_date) && (
                      <span className="character-years">{char.birth_date} — {char.death_date}</span>
                    )}
                  </div>
                </button>
              ))
            ) : (
              <p>Loading characters...</p>
            )}
          </div>
        </div>
      ) : (
        <div className="dialogue-container">
          <div className="dialogue-header">
            <h2>{selectedCharacter.charAt(0).toUpperCase() + selectedCharacter.slice(1)}</h2>
            <div className="header-actions">
              {messages.length > 0 && (
                <>
                  <button onClick={() => setShowSaveDialog(true)} className="btn-forward">
                    💾 Save Conversation
                  </button>
                  <button onClick={forwardConversation} className="btn-forward">
                    📤 Export Conversation
                  </button>
                  <button onClick={clearConversation} className="btn-forward btn-danger">
                    🗑️ Clear Conversation
                  </button>
                </>
              )}
              <button onClick={() => { loadUserConversations(); setShowSavedConversations(true); }} className="btn-forward">
                📋 Saved Conversations
              </button>
              <div className="back-buttons">
                <button onClick={() => { setSelectedCharacter(null); setGroupCharacters([]); }}>← Back to Characters</button>
                <button onClick={() => { setSelectedCharacter(null); setSelectedGroup(null); setGroupCharacters([]); }}>← Back to Paths</button>
              </div>
            </div>
          </div>

          <div className="dialogue-window">
            {messages.length === 0 ? (
              <div className="welcome-msg">
                <p>
                  Greetings, {playerName}! Ask me anything about Scripture and faith.
                </p>
                <p className="session-note">
                  💡 Your conversation will be saved automatically. Close and return anytime to continue.
                </p>
              </div>
            ) : (
              messages.map((msg, idx) => (
                <div key={idx} className={`message ${msg.role}`}>
                  {editingIndex === idx && msg.role === 'player' ? (
                    <div className="edit-mode">
                      <textarea
                        value={editingContent}
                        onChange={(e) => setEditingContent(e.target.value)}
                        className="edit-textarea"
                        rows="3"
                      />
                      <div className="edit-buttons">
                        <button onClick={() => saveEdit(idx)} className="btn-save">
                          Save
                        </button>
                        <button onClick={cancelEdit} className="btn-cancel">
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    <>
                      <div className="message-header">
                        <strong>
                          {msg.role === 'player'
                            ? playerName
                            : selectedCharacter.charAt(0).toUpperCase() +
                              selectedCharacter.slice(1)}
                          :
                        </strong>
                        {msg.role === 'player' && (
                          <div className="message-actions">
                            <button
                              onClick={() => startEdit(idx, msg.content)}
                              className="btn-action btn-edit"
                              title="Edit message"
                            >
                              ✎
                            </button>
                            <button
                              onClick={() => copyToClipboard(msg.content)}
                              className="btn-action btn-copy"
                              title="Copy message"
                            >
                              📋
                            </button>
                          </div>
                        )}
                        {msg.role === 'character' && (
                          <div className="message-actions">
                            <button
                              onClick={() => copyToClipboard(msg.content)}
                              className="btn-action btn-copy"
                              title="Copy message"
                            >
                              📋
                            </button>
                            <button
                              onClick={() => regenerateResponse(idx)}
                              className="btn-action btn-regenerate"
                              title="Regenerate response"
                              disabled={loading}
                            >
                              🔄
                            </button>
                          </div>
                        )}
                      </div>
                      <p>{msg.content}</p>
                      {msg.illustrations && msg.illustrations.length > 0 && (
                        <div className="illustrations-section">
                          {msg.illustrations.map((illustration, idx) => (
                            <div key={idx} className="illustration-container">
                              <div className="illustration-label">📊 Illustration:</div>
                              <div className="illustration-description">
                                {illustration.description}
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </>
                  )}
                </div>
              ))
            )}
            {loading && <div className="loading">Thinking...</div>}
          </div>

          <form onSubmit={sendMessage} className="input-form">
            <input
              type="text"
              placeholder="Ask a question..."
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              disabled={loading}
            />
            <button type="submit" disabled={loading}>
              Send
            </button>
          </form>

          {showSaveDialog && (
            <div className="modal-overlay" onClick={() => setShowSaveDialog(false)}>
              <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <h3>Save Conversation</h3>
                <input
                  type="text"
                  placeholder="Give this conversation a title (optional)..."
                  value={customTitle}
                  onChange={(e) => setCustomTitle(e.target.value)}
                  className="modal-input"
                />
                <div className="modal-buttons">
                  <button onClick={saveConversation} className="btn-modal-save">Save</button>
                  <button onClick={() => { setShowSaveDialog(false); setCustomTitle(''); }} className="btn-modal-cancel">Cancel</button>
                </div>
              </div>
            </div>
          )}

          {showSavedConversations && (
            <div className="modal-overlay" onClick={() => setShowSavedConversations(false)}>
              <div className="modal-content modal-large" onClick={(e) => e.stopPropagation()}>
                <h3>Saved Conversations</h3>
                {savedConversations.length === 0 ? (
                  <p className="no-conversations">No saved conversations yet</p>
                ) : (
                  <div className="conversations-list">
                    {savedConversations.map((conv) => (
                      <div key={conv.id} className="conversation-item">
                        <div className="conversation-info">
                          <strong>{conv.conversation_title}</strong>
                          <span className="conversation-meta">
                            {conv.character_id.charAt(0).toUpperCase() + conv.character_id.slice(1)} • {conv.message_count} messages
                          </span>
                          <span className="conversation-date">
                            {new Date(conv.updated_at).toLocaleDateString()} {new Date(conv.updated_at).toLocaleTimeString()}
                          </span>
                        </div>
                        <div className="conversation-actions">
                          <button onClick={() => loadConversation(conv.id)} className="btn-load">Load</button>
                          <button onClick={() => deleteConversation(conv.id)} className="btn-delete">Delete</button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
                <div className="modal-buttons">
                  <button onClick={() => setShowSavedConversations(false)} className="btn-modal-close">Close</button>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      <footer className="footer">
        <p>"In the beginning was the Word..." - John 1:1 (KJV 1611)</p>
      </footer>
    </div>
  )
}

export default App
