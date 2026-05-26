import React, { useState, useEffect } from 'react'
import { IconSearch, IconEye, IconX, IconRefresh } from '@tabler/icons-react'

export default function History() {
  const [search, setSearch] = useState('')
  const [filter, setFilter] = useState('all')
  const [reports, setReports] = useState([])
  const [loading, setLoading] = useState(true)

  const fetchHistory = async () => {
    setLoading(true)
    try {
      const resp = await fetch('/api/history')
      const data = await resp.json()
      setReports(data.reports || [])
    } catch (e) {
      console.error('History fetch error:', e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchHistory() }, [])

  const filtered = reports.filter(h => {
    if (search && !h.target.toLowerCase().includes(search.toLowerCase())) return false
    if (filter === 'critical' && (!h.severities || h.severities.CRITICAL === 0)) return false
    return true
  })

  const stats = {
    total: reports.length,
    critical: reports.reduce((s, h) => s + (h.severities?.CRITICAL || 0), 0),
    high: reports.reduce((s, h) => s + (h.severities?.HIGH || 0), 0),
  }

  const formatDate = (d) => {
    if (!d) return ''
    try { return new Date(d).toLocaleString('uz-UZ') } catch { return d }
  }

  return (
    <div className="history-page">
      <div className="page-header">
        <div className="page-title">Tarix</div>
        <div className="header-controls">
          <div style={{ display: 'flex', alignItems: 'center', gap: 4, background: 'var(--color-background-primary)', border: '0.5px solid var(--color-border-tertiary)', borderRadius: 6, padding: '4px 8px' }}>
            <IconSearch size={14} style={{ color: 'var(--color-text-tertiary)' }} />
            <input style={{ border: 'none', background: 'transparent', padding: 0, outline: 'none', color: 'var(--color-text-primary)', width: 120 }} placeholder="Qidirish..." value={search} onChange={e => setSearch(e.target.value)} />
          </div>
          <select value={filter} onChange={e => setFilter(e.target.value)}>
            <option value="all">Barchasi</option>
            <option value="critical">Kritik topilgan</option>
          </select>
          <button className="btn btn-outline btn-sm" onClick={fetchHistory}>
            <IconRefresh size={14} /> Yangilash
          </button>
        </div>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: 40, color: 'var(--color-text-tertiary)' }}>Yuklanmoqda...</div>
      ) : filtered.length === 0 ? (
        <div style={{ textAlign: 'center', padding: 40, color: 'var(--color-text-tertiary)' }}>
          {reports.length === 0 ? 'Hali hech qanday scan amalga oshirilmagan' : 'Hech narsa topilmadi'}
        </div>
      ) : (
        <div className="card table-card">
          <div className="table-header">
            <span>Target</span>
            <span>Sana</span>
            <span>Topilmalar</span>
            <span>Holat</span>
            <span></span>
          </div>
          {filtered.map((h, i) => (
            <div className="table-row" key={i}>
              <span className="table-url">{h.target}</span>
              <span className="table-date">{formatDate(h.date)}</span>
              <span style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
                {h.severities?.CRITICAL > 0 && <span className="badge badge-danger">{h.severities.CRITICAL} Kritik</span>}
                {h.severities?.HIGH > 0 && <span className="badge badge-warning">{h.severities.HIGH} Yuqori</span>}
                {h.severities?.MEDIUM > 0 && <span className="badge badge-info">{h.severities.MEDIUM} O'rta</span>}
                {h.total_vulns === 0 && <span className="badge badge-tertiary">—</span>}
              </span>
              <span>{h.status === 'completed' ? <span className="badge badge-success">✅ Tugadi</span> : <span className="badge badge-tertiary">{h.status}</span>}</span>
              <span>
                <a href={`/api/report/${h.id}`} target="_blank" rel="noreferrer" className="btn btn-outline btn-sm">
                  <IconEye size={14} /> Ko'rish
                </a>
              </span>
            </div>
          ))}
        </div>
      )}

      <div className="stats-row">
        <div className="stat-cell"><span className="stat-num">{stats.total}</span><span className="stat-label">Jami scan</span></div>
        <div className="stat-cell"><span className="stat-num" style={{ color: 'var(--color-danger)' }}>{stats.critical}</span><span className="stat-label">Kritik topilgan</span></div>
        <div className="stat-cell"><span className="stat-num" style={{ color: 'var(--color-warning)' }}>{stats.high}</span><span className="stat-label">Yuqori topilgan</span></div>
      </div>
    </div>
  )
}
