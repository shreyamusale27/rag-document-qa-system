import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import SourceCard from './SourceCard'

function formatTime(isoString) {
  const d = new Date(isoString)
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

export function UserMessage({ message }) {
  return (
    <div className="message user">
      <div className="message-avatar">U</div>
      <div className="message-body">
        <div className="message-bubble">
          {message.content}
        </div>
        <div className="message-time">{formatTime(message.timestamp)}</div>
      </div>
    </div>
  )
}

export function AssistantMessage({ message }) {
  const [showSources, setShowSources] = useState(false)
  const hasSources = message.sources && message.sources.length > 0

  return (
    <div className="message assistant">
      <div className="message-avatar">🤖</div>
      <div className="message-body">
        <div className="message-bubble">
          <ReactMarkdown>{message.content}</ReactMarkdown>
        </div>

        {hasSources && (
          <div className="sources-section">
            <button
              className="sources-toggle"
              onClick={() => setShowSources((s) => !s)}
              id={`sources-toggle-${message.id}`}
              aria-expanded={showSources}
            >
              <span className={`sources-toggle-icon ${showSources ? 'open' : ''}`}>▾</span>
              Sources
              <span className="sources-count-badge">{message.sources.length}</span>
            </button>

            {showSources && (
              <div className="sources-list">
                {message.sources.map((src, i) => (
                  <SourceCard key={i} source={src} index={i} />
                ))}
              </div>
            )}
          </div>
        )}

        <div className="message-time">
          {formatTime(message.timestamp)}
          {message.model && (
            <span style={{ marginLeft: 8, opacity: 0.6 }}>· {message.model}</span>
          )}
          {message.processingMs && (
            <span style={{ marginLeft: 8, opacity: 0.6 }}>· {message.processingMs}ms</span>
          )}
        </div>
      </div>
    </div>
  )
}

export function ThinkingMessage() {
  return (
    <div className="message assistant">
      <div className="message-avatar">🤖</div>
      <div className="message-body">
        <div className="thinking-bubble">
          <span className="thinking-text">Thinking</span>
          <div className="thinking-dots">
            <div className="thinking-dot" />
            <div className="thinking-dot" />
            <div className="thinking-dot" />
          </div>
        </div>
      </div>
    </div>
  )
}
