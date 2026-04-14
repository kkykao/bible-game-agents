import React, { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [playerName, setPlayerName] = useState('')
  const [gameStarted, setGameStarted] = useState(false)
  const [characters, setCharacters] = useState([])
  const [selectedCharacter, setSelectedCharacter] = useState(null)
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [loading, setLoading] = useState(false)

  // Fetch characters from backend
  useEffect(() => {
    const fetchCharacters = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/characters')
        const data = await response.json()
        setCharacters(data.characters || [])
      } catch (error) {
        console.error('Error fetching characters:', error)
      }
    }
    if (gameStarted) {
      fetchCharacters()
    }
  }, [gameStarted])

  const startGame = (name) => {
    if (name.trim()) {
      setPlayerName(name)
      setGameStarted(true)
    }
  }

  const selectCharacter = (character) => {
    setSelectedCharacter(character)
    setMessages([])
    setInputMessage('')
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
      ) : !selectedCharacter ? (
        <div className="game-container">
          <h2>Welcome, {playerName}!</h2>
          <p>Choose a Biblical character to learn from:</p>
          <div className="character-list">
            {characters.length > 0 ? (
              characters.map((char) => (
                <button
                  key={char}
                  className="character-btn"
                  onClick={() => selectCharacter(char)}
                >
                  {char.charAt(0).toUpperCase() + char.slice(1)}
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
            <button onClick={() => setSelectedCharacter(null)}>← Back</button>
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
                  <strong>
                    {msg.role === 'player'
                      ? playerName
                      : selectedCharacter.charAt(0).toUpperCase() +
                        selectedCharacter.slice(1)}
                    :
                  </strong>
                  <p>{msg.content}</p>
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
