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
    }
  }

  const selectGroup = (groupId) => {
    setSelectedGroup(groupId)
    setGroupCharacters([])
  }

  const selectCharacter = (character) => {
    setSelectedCharacter(character)
    setMessages([])
    setInputMessage('')
    setEditingIndex(null)
    setEditingContent('')
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
                <button onClick={forwardConversation} className="btn-forward">
                  📤 Export Conversation
                </button>
              )}
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
        </div>
      )}

      <footer className="footer">
        <p>"In the beginning was the Word..." - John 1:1 (KJV 1611)</p>
      </footer>
    </div>
  )
}

export default App
