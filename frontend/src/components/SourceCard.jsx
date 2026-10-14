import { useState } from 'react'

export default function SourceCard({ source, index }) {
  const score = source.relevance_score ?? 0
  const scoreLabel = score >= 0.75 ? 'high' : score >= 0.45 ? 'medium' : 'low'
  const scorePercent = Math.round(score * 100)

  return (
    <div className="source-card">
      <div className="source-card-header">
        <span className="source-card-icon">📄</span>
        <span className="source-doc-name" title={source.document_name}>
          {source.document_name}
        </span>
        <span className="source-page">p. {source.page_number}</span>
        <span className={`source-score ${scoreLabel}`}>{scorePercent}%</span>
      </div>
      <div className="source-card-body">
        {source.content}
      </div>
    </div>
  )
}
