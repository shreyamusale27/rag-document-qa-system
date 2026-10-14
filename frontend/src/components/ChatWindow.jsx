import { useEffect, useRef } from 'react'
import { UserMessage, AssistantMessage, ThinkingMessage } from './MessageBubble'

export default function ChatWindow({ messages, isThinking, error }) {
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isThinking])

  const showWelcome = messages.length === 0 && !isThinking

  return (
    <div className="messages-container" id="chat-messages">
      {showWelcome && (
        <div className="welcome-state">
          <div className="welcome-icon">🧠</div>
          <h1 className="welcome-title">DocMind AI</h1>
          <p className="welcome-desc">
            Upload your PDF documents and ask questions. Get precise answers
            with source citations — grounded in your documents.
          </p>
          <div className="welcome-steps">
            <div className="welcome-step">
              <div className="step-num">1</div>
              Upload PDF documents
            </div>
            <div className="welcome-step">
              <div className="step-num">2</div>
              Select docs to query
            </div>
            <div className="welcome-step">
              <div className="step-num">3</div>
              Ask any question
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="error-banner" role="alert">⚠️ {error}</div>
      )}

      {messages.map((msg) =>
        msg.role === 'user' ? (
          <UserMessage key={msg.id} message={msg} />
        ) : (
          <AssistantMessage key={msg.id} message={msg} />
        )
      )}

      {isThinking && <ThinkingMessage />}

      <div ref={bottomRef} />
    </div>
  )
}
