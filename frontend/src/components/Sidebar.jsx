import { deleteDocument } from '../services/api'

export default function Sidebar({
  documents,
  selectedDocIds,
  onToggleDoc,
  onOpenUpload,
  onDocumentDeleted,
  loading,
}) {
  const handleDelete = async (e, docId) => {
    e.stopPropagation()
    if (!confirm('Delete this document and its index?')) return
    try {
      await deleteDocument(docId)
      onDocumentDeleted(docId)
    } catch (err) {
      alert('Failed to delete document.')
    }
  }

  const formatSize = (kb) => {
    if (kb < 1024) return `${kb}KB`
    return `${(kb / 1024).toFixed(1)}MB`
  }

  const selectedCount = selectedDocIds.length
  const readyCount = documents.filter((d) => d.status === 'ready').length

  return (
    <aside className="sidebar" aria-label="Document panel">
      <div className="sidebar-header">
        {/* Logo */}
        <div className="logo">
          <div className="logo-icon">🧠</div>
          <div>
            <div className="logo-text">DocMind AI</div>
            <div className="logo-sub">RAG Q&amp;A System</div>
          </div>
        </div>

        {/* Upload button */}
        <button
          className="upload-btn"
          onClick={onOpenUpload}
          id="open-upload-modal-btn"
        >
          <span>＋</span> Upload PDF
        </button>
      </div>

      {/* Section title */}
      <div className="sidebar-section-title">
        Documents ({documents.length})
      </div>

      {/* Document list */}
      <div className="doc-list" role="list">
        {loading && (
          <div className="empty-docs">
            <div className="empty-docs-icon">⏳</div>
            Loading documents…
          </div>
        )}

        {!loading && documents.length === 0 && (
          <div className="empty-docs">
            <div className="empty-docs-icon">📂</div>
            No documents yet.
            <br />Upload a PDF to get started.
          </div>
        )}

        {documents.map((doc) => {
          const isSelected = selectedDocIds.includes(doc.id)
          return (
            <div
              key={doc.id}
              className={`doc-item ${isSelected ? 'selected' : ''}`}
              onClick={() => doc.status === 'ready' && onToggleDoc(doc.id)}
              role="listitem"
              aria-selected={isSelected}
              title={doc.original_name}
              id={`doc-item-${doc.id}`}
            >
              {/* Checkbox */}
              <div className="doc-checkbox">
                <div className="doc-checkbox-inner" />
              </div>

              {/* Info */}
              <div className="doc-info">
                <div className="doc-name">{doc.original_name}</div>
                <div className="doc-meta">
                  <span className="doc-pages">{doc.page_count}p</span>
                  <span className="doc-size">{formatSize(doc.file_size_kb)}</span>
                  <span className={`status-badge ${doc.status}`}>{doc.status}</span>
                </div>
              </div>

              {/* Delete */}
              <button
                className="doc-delete-btn"
                onClick={(e) => handleDelete(e, doc.id)}
                aria-label={`Delete ${doc.original_name}`}
                title="Delete document"
              >
                🗑
              </button>
            </div>
          )
        })}
      </div>

      {/* Footer hint */}
      <div className="sidebar-footer">
        <div className="select-hint">
          {selectedCount > 0
            ? `Querying ${selectedCount} of ${readyCount} selected`
            : readyCount > 0
            ? 'Click docs to select for querying'
            : 'Upload docs to start asking questions'}
        </div>
      </div>
    </aside>
  )
}
