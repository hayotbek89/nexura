import React, { useState, useRef, useEffect } from 'react'
import {
  IconTerminal2, IconBell, IconCircleCheck, IconClock,
  IconRobot, IconSend, IconRadar
} from '@tabler/icons-react'

export default function Scanner() {
  const [url, setUrl] = useState('')
  const [scanning, setScanning] = useState(false)
  const [prompt, setPrompt] = useState('')
  const [messages, setMessages] = useState([])
  const [toolStatus, setToolStatus] = useState({
    nmap: { status: 'idle' },
    nikto: { status: 'idle' },
    sqlmap: { status: 'idle' },
    nuclei: { status: 'idle' },
    gobuster: { status: 'idle' },
    amass: { status: 'idle' },
  })
  const [findings, setFindings] = useState({ critical: 0, high: 0, medium: 0, low: 0 })
  const [results, setResults] = useState([])
  const [aiAdvice, setAiAdvice] = useState('')
  const [scanId, setScanId] = useState(null)
  const [reportUrl, setReportUrl] = useState(null)
  const chatEndRef = useRef(null)

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const startScan = async () => {
    if (!url.trim()) return
    setScanning(true)
    setResults([])
    setFindings({ critical: 0, high: 0, medium: 0, low: 0 })
    setAiAdvice('')
    setReportUrl(null)

    const toolNames = ['nmap', 'nikto', 'sqlmap', 'nuclei', 'gobuster', 'amass']
    toolNames.forEach(t => setToolStatus(prev => ({ ...prev, [t]: { status: 'running' } })))

    try {
      const resp = await fetch('/api/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: `${url} ni to'liq zaifliklarga tekshir`, target: url }),
      })
      const data = await resp.json()

      if (!resp.ok) {
        throw new Error(data.error || 'Server xatosi')
      }

      const finalStatuses = {}
      data.results?.forEach(r => {
        finalStatuses[r.tool] = { status: r.success ? 'done' : 'error' }
      })
      setToolStatus(prev => ({ ...prev, ...finalStatuses }))

      const allVulns = data.results?.flatMap(r => r.vulnerabilities || []) || []
      setFindings({
        critical: allVulns.filter(v => v.severity === 'CRITICAL').length,
        high: allVulns.filter(v => v.severity === 'HIGH').length,
        medium: allVulns.filter(v => v.severity === 'MEDIUM').length,
        low: allVulns.filter(v => v.severity === 'LOW').length,
      })
      setResults(allVulns.map(v => ({
        severity: v.severity,
        title: v.name,
        tool: v.cve || '',
        time: '',
      })))
      setScanId(data.id)
      setReportUrl(data.report_html)

      const intent = data.intent || ''
      let advice = `**Maqsad:** ${intent}\n\n`
      data.results?.forEach(r => {
        advice += `${r.success ? '✅' : '❌'} **${r.tool.toUpperCase()}**: ${r.summary || 'Done'}\n`
      })
      setAiAdvice(advice)
    } catch (e) {
      setToolStatus(prev => {
        const updated = {}
        Object.keys(prev).forEach(t => { updated[t] = { status: 'error' } })
        return { ...prev, ...updated }
      })
      setMessages(prev => [...prev, { role: 'assistant', content: `❌ Xatolik: ${e.message}` }])
    } finally {
      setScanning(false)
    }
  }

  const sendPrompt = async () => {
    if (!prompt.trim() || scanning) return
    const userMsg = prompt.trim()
    setMessages(prev => [...prev, { role: 'user', content: userMsg }])
    setPrompt('')

    setMessages(prev => [...prev, { role: 'assistant', content: '⏳ AI tahlil qilmoqda...', loading: true }])

    try {
      const resp = await fetch('/api/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: userMsg, target: url || undefined }),
      })
      const data = await resp.json()
      setMessages(prev => prev.filter(m => !m.loading))
      if (resp.ok) {
        let answer = `🎯 **Maqsad:** ${data.intent || userMsg}\n\n`
        if (data.tools?.length) {
          answer += `**Tanlangan vositalar:** ${data.tools.join(', ')}\n\n`
        }
        data.results?.forEach(r => {
          answer += `${r.success ? '✅' : '❌'} **${r.tool.toUpperCase()}**: ${r.summary || 'Done'}\n`
          r.vulnerabilities?.forEach(v => {
            answer += `  - [${v.severity}] ${v.name}\n`
          })
        })
        if (data.id) {
          answer += `\n📄 Hisobot ID: ${data.id}`
        }
        setMessages(prev => [...prev, { role: 'assistant', content: answer }])

        const allVulns = data.results?.flatMap(r => r.vulnerabilities || []) || []
        setFindings({
          critical: allVulns.filter(v => v.severity === 'CRITICAL').length,
          high: allVulns.filter(v => v.severity === 'HIGH').length,
          medium: allVulns.filter(v => v.severity === 'MEDIUM').length,
          low: allVulns.filter(v => v.severity === 'LOW').length,
        })
        setResults(allVulns.map(v => ({
          severity: v.severity,
          title: v.name,
          tool: '',
          time: '',
        })))
        setReportUrl(data.report_html)
      } else {
        setMessages(prev => [...prev, { role: 'assistant', content: `❌ Xatolik: ${data.error || 'Serverda xatolik'}` }])
      }
    } catch (e) {
      setMessages(prev => prev.filter(m => !m.loading))
      setMessages(prev => [...prev, { role: 'assistant', content: `⚠️ Serverga ulanib bo'lmadi: ${e.message}` }])
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendPrompt() }
  }

  return (
    <div className="scanner-page">
      <div className="card url-card">
        <div className="url-label">Maqsad URL</div>
        <div className="url-input-row">
          <input
            className="url-input"
            placeholder="https://example.com"
            value={url}
            onChange={e => setUrl(e.target.value)}
          />
          <button className="btn btn-primary" onClick={startScan} disabled={scanning}>
            <IconRadar size={16} />
            {scanning ? 'Skanerlanmoqda...' : 'Scan boshlash'}
          </button>
        </div>
        <div className="tool-badges">
          <span className="badge badge-info">nmap</span>
          <span className="badge badge-info">nikto</span>
          <span className="badge badge-info">sqlmap</span>
          <span className="badge badge-info">nuclei</span>
          <span className="badge badge-info">gobuster</span>
          <span className="badge badge-info">amass</span>
        </div>
      </div>

      <div className="scanner-grid">
        <div className="card">
          <div className="card-header">
            <IconTerminal2 size={18} />
            Tool holati
          </div>
          <div className="tool-status-list">
            {Object.entries(toolStatus).map(([tool, st]) => (
              <div className="tool-row" key={tool}>
                <div className="tool-row-left">
                  <IconTerminal2 size={16} />
                  <span>{tool.toUpperCase()}</span>
                </div>
                <div className="tool-status">
                  {st.status === 'done' && <><IconCircleCheck size={14} style={{ color: 'var(--color-success)' }} /><span style={{ color: 'var(--color-success)' }}>Tugadi</span></>}
                  {st.status === 'running' && <><span className="blink-dot" /><span style={{ color: 'var(--color-info)' }}>Ishlayapti...</span></>}
                  {st.status === 'idle' && <><IconClock size={14} /><span style={{ color: 'var(--color-text-tertiary)' }}>Kutmoqda</span></>}
                  {st.status === 'error' && <><span style={{ color: 'var(--color-danger)' }}>❌</span><span style={{ color: 'var(--color-danger)' }}>Xato</span></>}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <IconBell size={18} />
            Topilmalar xulosa
          </div>
          <div className="findings-grid">
            <div className="findings-cell"><span className="findings-num danger">{findings.critical}</span><span className="findings-label">Kritik</span></div>
            <div className="findings-cell"><span className="findings-num warning">{findings.high}</span><span className="findings-label">Yuqori</span></div>
            <div className="findings-cell"><span className="findings-num info">{findings.medium}</span><span className="findings-label">O'rta</span></div>
            <div className="findings-cell"><span className="findings-num success">{findings.low}</span><span className="findings-label">Past</span></div>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <IconRobot size={18} />
          AI buyruq — Tabiiy tilda yozing
        </div>
        <div className="chat-messages">
          {messages.map((msg, i) => (
            <div key={i} className={`chat-msg ${msg.role}`}>
              {msg.content.split('\n').map((line, j) => <div key={j}>{line}</div>)}
            </div>
          ))}
          <div ref={chatEndRef} />
        </div>
        <div className="prompt-input-row">
          <textarea
            className="prompt-input"
            placeholder="Misol: example.com ni zaifliklarga to'liq tekshir"
            value={prompt}
            onChange={e => setPrompt(e.target.value)}
            onKeyDown={handleKeyDown}
            rows={1}
          />
          <button className="prompt-send-btn" onClick={sendPrompt} disabled={scanning || !prompt.trim()}>
            <IconSend size={18} />
          </button>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <IconRadar size={18} />
          Real-time natijalar
        </div>
        {results.length === 0 ? (
          <div style={{ color: 'var(--color-text-tertiary)', fontSize: 13, padding: '8px 0' }}>
            Scan boshlangandan so'ng natijalar bu yerda ko'rinadi
          </div>
        ) : (
          results.map((r, i) => (
            <div className="result-item" key={i}>
              <span className={`badge badge-${r.severity === 'CRITICAL' ? 'danger' : r.severity === 'HIGH' ? 'warning' : r.severity === 'MEDIUM' ? 'info' : 'success'}`}>
                {r.severity}
              </span>
              <span className="result-title">{r.title}</span>
              {r.tool && <span className="badge badge-tertiary">{r.tool}</span>}
              {r.time && <span className="result-meta">{r.time}</span>}
            </div>
          ))
        )}
      </div>

      {aiAdvice && (
        <div className="card">
          <div className="card-header">
            <IconRobot size={18} />
            AI xulosa
          </div>
          <div className="ai-suggestion-text">
            {aiAdvice.split('\n').map((line, i) => <div key={i}>{line}</div>)}
          </div>
          {reportUrl && (
            <div style={{ marginTop: 12 }}>
              <a href={`/api/report/${scanId}`} className="btn btn-primary btn-sm" target="_blank" rel="noreferrer">
                📄 To'liq hisobot
              </a>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
