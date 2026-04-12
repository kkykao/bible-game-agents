import React, { useState } from 'react'
import './App.css'

function App() {
  const [playerName, setPlayerName] = useState('')
  const [gameStarted, setGameStarted] = useState(false)

  const startGame = (name) => {
    setPlayerName(name)
    setGameStarted(true)
  }

  return (
    <div className="app">
      <header className="header">
        <h1>Bible Learning Game</h1>
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
      ) : (
        <div className="game-container">
          <h2>Welcome, {playerName}!</h2>
          <p>Game content coming soon...</p>
        </div>
      )}

      <footer className="footer">
        <p>"In the beginning was the Word..." - John 1:1 (KJV 1611)</p>
      </footer>
    </div>
  )
}

export default App
