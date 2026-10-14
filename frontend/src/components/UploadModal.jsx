import { useState, useRef } from 'react'
import { uploadDocument } from '../services/api'

export default function UploadModal({ onClose, onUploaded }) {
  const [selectedFile, setSelectedFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [error, setError] = useState('')
  const [dragOver, setDragOver] = useState(false)
  const fileInputRef = useRef(null)

  const handleFile = (file) => {
    setError('')
    if (!file) return

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setError('Only PDF files are supported.')
      return
    }
    if (file.size > 50 * 1024 * 1024) {
      setError('File must be under 50MB.')
      return
    }
    setSelectedFile(file)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    const file = e.dataTransfer.files[0]
    handleFile(file)
  }

  const handleUpload = async () => {
    if (!selectedFile) return
    setUploading(true)
    setError('')
    setProgress(0)

    try {
      const res = await uploadDocument(selectedFile, setProgress)
      onUploaded(res.data)
      onClose()
    } catch (err) {
      const msg = err.response?.data?.detail || 'Upload failed. Please try again.'
      setError(msg)
      setUploading(false)
      setProgress(0)
    }
  }

  const formatSize = (bytes) => {
    if (bytes < 1024) return `${bytes}B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)}MB`
  }

  return (
    <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && !uploading && onClose()}>
      <div className="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title">
        <div className="modal-header">
          <h2 className="modal-title" id="modal-title">📤 Upload Document</h2>
          {!uploading && (
            <button className="modal-close" onClick={onClose} aria-label="Close">✕</button>
          )}
        </div>

        {/* Dropzone */}
        <div
          className={`dropzone ${dragOver ? 'drag-over' : ''}`}
          onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => !uploading && fileInputRef.current?.click()}
          role="button"
          tabIndex={0}
          aria-label="Drop PDF here or click to select"
        >
          <div className="dropzone-icon">
            {selectedFile ? '📄' : '☁️'}
          </div>
          <p className="dropzone-text">
            {selectedFile
              ? 'File selected — ready to upload'
              : <>Drop your PDF here or <span className="dropzone-accent">browse files</span></>
            }
          </p>
          <p className="dropzone-hint">PDF files up to 50MB</p>
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf"
            style={{ display: 'none' }}
            onChange={(e) => handleFile(e.target.files[0])}
          />
        </div>

        {/* Selected file info */}
        {selectedFile && (
          <div className="selected-file">
            <span>📑</span>
            <span className="selected-file-name">{selectedFile.name}</span>
            <span className="selected-file-size">{formatSize(selectedFile.size)}</span>
          </div>
        )}

        {/* Upload progress */}
        {uploading && (
          <div className="upload-progress">
            <div className="progress-bar-track">
              <div className="progress-bar-fill" style={{ width: `${progress}%` }} />
            </div>
            <p className="progress-label">
              {progress < 100 ? `Uploading… ${progress}%` : 'Processing & indexing…'}
            </p>
          </div>
        )}

        {/* Error */}
        {error && <div className="upload-error" role="alert">⚠️ {error}</div>}

        <div className="modal-actions">
          <button
            className="btn-secondary"
            onClick={onClose}
            disabled={uploading}
            id="upload-cancel-btn"
          >
            Cancel
          </button>
          <button
            className="btn-primary"
            onClick={handleUpload}
            disabled={!selectedFile || uploading}
            id="upload-submit-btn"
          >
            {uploading ? 'Uploading…' : 'Upload & Index'}
          </button>
        </div>
      </div>
    </div>
  )
}
