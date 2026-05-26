import React, { useState, useEffect } from 'react'
import { IconRobot, IconDownload, IconAlertTriangle, IconShieldExclamation } from '@tabler/icons-react'

export default function Reports() {
  const [period, setPeriod] = useState('all')
  const [reports, setReports] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchReports = async () => {
      try {
        const resp = await fetch('/api/history')
        const data = await resp.json()
        setReports(data.reports || [])
      } catch (e) {
        console.error('Reports fetch error:', e)
      } finally {
        setLoading(false)
      }
    }
    fetchReports()
  }, [])

  const filtered = reports.filter(r => {
    if (period === '7') {
      const weekAgo = Date.now() - 7 * 24 * 60 * 60 * 1000
      return r.date ? new Date(r.date).getTime() > weekAgo : true
    }
    if (period === '30') {
      const monthAgo = Date.now() - 30 * 24 * 60 * 60 * 1000
      return r.date ? new Date(r.date).getTime() > monthAgo : true
    }
    return true
  })

  const totalScans = filtered.length
  const totalCritical = filtered.reduce((s, r) => s + (r.severities?.CRITICAL || 0), 0)
  const totalHigh = filtered.reduce((s, r) => s + (r.severities?.HIGH || 0), 0)
  const totalVulns = filtered.reduce((s, r) => s + (r.total_vulns || 0), 0)

  const vulnCounts = {}
  filtered.forEach(r => {
    (r.tools || []).forEach(t => {
      vulnCounts[t] = (vulnCounts[t] || 0) + 1
    })
  })
  const topTools = Object.entries(vulnCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .map(([name, count]) => ({ name, count }))

  const maxCount = topTools.length > 0 ? Math.max(...topTools.map(t => t.count)) : 1

  const formatDate = (d) => {
    if (!d) return ''
    try { return new Date(d).toLocaleDateString('uz-UZ') } catch { return d }
  }

  return (
    <div className="reports-page">
      <div className="page-header">
        <div className="page-title">Hisobotlar</div>
        <div className="header-controls">
          <select value={period} onChange={e => setPeriod(e.target.value)}>
            <option value="7">So'nggi 7 kun</option>
            <option value="30">So'nggi 30 kun</option>
            <option value="all">Barchasi</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: 40, color: 'var(--color-text-tertiary)' }}>Yuklanmoqda...</div>
      ) : (
        <>
          <div className="reports-stats">
            <div className="reports-stat"><span className="findings-num" style={{ color: 'var(--color-text-primary)' }}>{totalScans}</span><span className="findings-label" style={{ color: 'var(--color-text-secondary)' }}>Jami scan</span></div>
            <div className="reports-stat"><span className="findings-num danger">{totalCritical}</span><span className="findings-label" style={{ color: 'var(--color-text-secondary)' }}>Kritik</span></div>
            <div className="reports-stat"><span className="findings-num warning">{totalHigh}</span><span className="findings-label" style={{ color: 'var(--color-text-secondary)' }}>Yuqori</span></div>
            <div className="reports-stat"><span className="findings-num" style={{ color: 'var(--color-info)' }}>{totalVulns}</span><span className="findings-label" style={{ color: 'var(--color-text-secondary)' }}>Jami zaiflik</span></div>
          </div>

          <div className="reports-grid">
            <div className="card">
              <div className="card-header">
                <IconAlertTriangle size={18} />
                Eng ko'p ishlatilgan vositalar
              </div>
              <div className="vuln-list">
                {topTools.length === 0 ? (
                  <div style={{ color: 'var(--color-text-tertiary)', fontSize: 13, padding: '8px 0' }}>Ma'lumot yo'q</div>
                ) : (
                  topTools.map((v, i) => (
                    <div className="vuln-row" key={i}>
                      <span className="vuln-name">{v.name}</span>
                      <span style={{ fontWeight: 700, fontSize: 13, width: 30, textAlign: 'right' }}>{v.count}</span>
                      <div className="vuln-progress">
                        <div className="vuln-bar-bg">
                          <div className="vuln-bar-fill" style={{ width: `${(v.count / maxCount) * 100}%`, background: 'var(--color-info)' }} />
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            <div className="card">
              <div className="card-header">
                <IconShieldExclamation size={18} />
                Scan bo'yicha hisobot
              </div>
              <div className="vuln-list">
                {filtered.length === 0 ? (
                  <div style={{ color: 'var(--color-text-tertiary)', fontSize: 13, padding: '8px 0' }}>Hali scan o'tkazilmagan</div>
                ) : (
                  filtered.slice(0, 10).map((r, i) => {
                    const topSev = r.severities?.CRITICAL > 0 ? 'badge-danger' : r.severities?.HIGH > 0 ? 'badge-warning' : r.severities?.MEDIUM > 0 ? 'badge-info' : 'badge-success'
                    const topLabel = r.severities?.CRITICAL > 0 ? 'Kritik' : r.severities?.HIGH > 0 ? 'Yuqori' : r.severities?.MEDIUM > 0 ? "O'rta" : 'Past'
                    return (
                      <div className="vuln-row" key={i}>
                        <div style={{ flex: 1 }}>
                          <div style={{ fontWeight: 600, fontSize: 13 }}>{r.target}</div>
                          <div style={{ fontSize: 11, color: 'var(--color-text-secondary)' }}>{formatDate(r.date)}</div>
                        </div>
                        <span className={`badge ${topSev}`}>{topLabel}</span>
                        <a href={`/api/report/${r.id}`} target="_blank" rel="noreferrer" className="btn btn-outline btn-sm">
                          <IconDownload size={14} /> PDF
                        </a>
                      </div>
                    )
                  })
                )}
              </div>
            </div>
          </div>

          {filtered.length > 0 && (
            <div className="card ai-analysis-card">
              <div className="card-header">
                <IconRobot size={18} />
                AI umumiy tahlili
              </div>
              <div className="ai-block ai-block-danger">
                <div className="ai-block-title" style={{ color: 'var(--color-danger)' }}>Eng xavfli muammo</div>
                <div className="ai-block-text">
                  {totalCritical > 0
                    ? `${totalCritical} ta kritik zaiflik aniqlandi. Ushbu zaifliklar orqali tizimga to'liq kirish mumkin. Darhol Web Application Firewall (WAF) o'rnating va xavfsizlik tekshiruvini kuchaytiring.`
                    : 'Kritik zaifliklar topilmadi. Xavfsizlik holati yaxshi.'}
                </div>
              </div>
              <div className="ai-block ai-block-warning">
                <div className="ai-block-title" style={{ color: 'var(--color-warning)' }}>Tez hal qilish kerak</div>
                <div className="ai-block-text">
                  Ochiq portlar va eski dastur versiyalari xavf tug'diradi. Keraksiz portlarni yoping va barcha dasturlarni yangilang.
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}
