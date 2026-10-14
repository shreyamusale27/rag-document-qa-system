import { useState, useEffect, useRef, useCallback } from 'react'
import Sidebar from './components/Sidebar'
import ChatWindow from './components/ChatWindow'
import UploadModal from './components/UploadModal'
import { listDocuments, askQuestion, getQAHealth } from './services/api'

let msgIdCounter = 0
const newId = () => `msg-${++msgIdCounter}`

export default function App() {
  const [documents, setDocuments] = useState([])
  const [selectedDocIds, setSelectedDocIds] = useState([])
  const [messages, setMessages] = useState([])
  const [isThinking, setIsThinking] = useState(false)
  const [inputText, setInputText] = useState('')
  const [showUpload, setShowUpload] = useState(false)
  const [docsLoading, setDocsLoading] = useState(true)
  const [chatError, setChatError] = useState('')
  const [apiStatus, setApiStatus] = useState('checking') // checking | ready | error
  const [apiStatusText, setApiStatusText] = useState('Checking…')
  const textareaRef = useRef(null)

  // ── Load documents on mount ──────────────────────────────────
  const fetchDocuments = useCallback(async () => {
    try {
      const res = await listDocuments()
      setDocuments(res.data.documents)
    } catch (err) {
      console.error('Failed to load documents:', err)
    } finally {
      setDocsLoading(false)
    }
  }, [])

  // ── Check API health ─────────────────────────────────────────
  const checkHealth = useCallback(async () => {
    try {
      const res = await getQAHealth()
      const { api_configured, documents_indexed } = res.data
      if (!api_configured) {
        setApiStatus('error')
        setApiStatusText('API key not configured')
      } else if (documents_indexed === 0) {
        setApiStatus('checking')
        setApiStatusText('No docs indexed yet')
      } else {
        setApiStatus('ready')
        setApiStatusText(`Ready · ${documents_indexed} doc${documents_indexed > 1 ? 's' : ''} indexed`)
      }
    } catch {
      setApiStatus('error')
      setApiStatusText('Backend offline')
    }
  }, [])

  useEffect(() => {
    fetchDocuments()
    checkHealth()

    // Poll for indexing status updates
    const interval = setInterval(() => {
      fetchDocuments()
      checkHealth()
    }, 5000)
    return () => clearInterval(interval)
  }, [fetchDocuments, checkHealth])

  // ── Toggle document selection ────────────────────────────────
  const toggleDoc = (docId) => {
    setSelectedDocIds((prev) =>
      prev.includes(docId) ? prev.filter((id) => id !== docId) : [...prev, docId]
    )
  }

  // ── Handle doc deleted ───────────────────────────────────────
  const handleDocumentDeleted = (docId) => {
    setDocuments((prev) => prev.filter((d) => d.id !== docId))
    setSelectedDocIds((prev) => prev.filter((id) => id !== docId))
  }

  // ── Handle upload complete ───────────────────────────────────
  const handleUploaded = (data) => {
    fetchDocuments()
    setShowUpload(false)
  }

  // ── Send message ─────────────────────────────────────────────
  const sendMessage = async () => {
    const question = inputText.trim()
    if (!question || isThinking) return

    setChatError('')
    setInputText('')

    // Add user message
    const userMsg = {
      id: newId(),
      role: 'user',
      content: question,
      timestamp: new Date().toISOString(),
    }
    setMessages((prev) => [...prev, userMsg])
    setIsThinking(true)

    try {
      const docIds = selectedDocIds.length > 0 ? selectedDocIds : null
      const res = await askQuestion(question, docIds)
      const data = res.data

      const assistantMsg = {
        id: newId(),
        role: 'assistant',
        content: data.answer,
        sources: data.sources,
        model: data.model_used,
        processingMs: data.processing_time_ms,
        timestamp: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, assistantMsg])
    } catch (err) {
      const detail = err.response?.data?.detail || 'Something went wrong. Please try again.'
      setChatError(detail)
    } finally {
      setIsThinking(false)
    }
  }

  // ── Keyboard handler ─────────────────────────────────────────
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  // ── Auto-resize textarea ─────────────────────────────────────
  const handleInput = (e) => {
    setInputText(e.target.value)
    const ta = textareaRef.current
    if (ta) {
      ta.style.height = 'auto'
      ta.style.height = `${Math.min(ta.scrollHeight, 120)}px`
    }
  }

  const canSend = inputText.trim().length > 0 && !isThinking

  const contextLabel =
    selectedDocIds.length > 0
      ? `${selectedDocIds.length} doc${selectedDocIds.length > 1 ? 's' : ''} selected`
      : 'All documents'

  return (
    <div className="app-shell">
      {/* ─── Sidebar ─────────────────────────────────────────── */}
      <Sidebar
        documents={documents}
        selectedDocIds={selectedDocIds}
        onToggleDoc={toggleDoc}
        onOpenUpload={() => setShowUpload(true)}
        onDocumentDeleted={handleDocumentDeleted}
        loading={docsLoading}
      />

      {/* ─── Main Chat ───────────────────────────────────────── */}
      <main className="chat-area">
        {/* Header */}
        <div className="chat-header">
          <div>
            <div className="chat-header-title">Document Q&amp;A</div>
            <div className="chat-header-sub">Context: {contextLabel}</div>
          </div>
          <div className="api-status" id="api-status-indicator">
            <div className={`api-dot ${apiStatus}`} />
            {apiStatusText}
          </div>
        </div>

        {/* Messages */}
        <ChatWindow
          messages={messages}
          isThinking={isThinking}
          error={chatError}
        />

        {/* Input */}
        <div className="chat-input-area">
          <div className="chat-input-wrapper">
            <textarea
              ref={textareaRef}
              className="chat-textarea"
              id="chat-input"
              placeholder="Ask a question about your documents… (Enter to send, Shift+Enter for newline)"
              value={inputText}
              onChange={handleInput}
              onKeyDown={handleKeyDown}
              rows={1}
              disabled={isThinking}
              aria-label="Question input"
            />
            <button
              className="send-btn"
              onClick={sendMessage}
              disabled={!canSend}
              id="send-message-btn"
              aria-label="Send message"
            >
              ➤
            </button>
          </div>
          <div className="input-hint">
            Powered by OpenAI GPT-4o-mini · FAISS Vector Search · LangChain
          </div>
        </div>
      </main>

      {/* ─── Upload Modal ─────────────────────────────────────── */}
      {showUpload && (
        <UploadModal
          onClose={() => setShowUpload(false)}
          onUploaded={handleUploaded}
        />
      )}
    </div>
  )
}
