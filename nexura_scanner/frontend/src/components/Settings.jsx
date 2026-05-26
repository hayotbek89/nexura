import React, { useState, useEffect } from 'react'
import { IconTerminal2 } from '@tabler/icons-react'
import { useTheme } from '../App'

const SCAN_SETTINGS = [
  { id: 'intensity', label: 'Scan intensivligi', type: 'select', options: ['Normal', 'Tez', 'To\'liq'], value: 'Normal' },
  { id: 'timeout', label: 'Timeout (soniya)', type: 'number', value: 300 },
]

const AI_SETTINGS = [
  { id: 'offline', label: 'Offline rejim', type: 'toggle', value: true },
]

const APP_SETTINGS = [
  { id: 'lang', label: 'Til', type: 'select', options: ['O\'zbek', 'Русский', 'English'], value: 'O\'zbek' },
  { id: 'theme', label: 'Mavzu', type: 'select', options: ['Tizim', 'Yorug\'', 'Qorong\'u'], value: 'Qorong\'u' },
]

function Toggle({ checked, onChange }) {
  return (
    <label className="toggle">
      <input type="checkbox" checked={checked} onChange={onChange} />
      <span className="toggle-slider"></span>
    </label>
  )
}

export default function Settings() {
  const [tab, setTab] = useState('tools')
  const { theme, setTheme } = useTheme()
  const [tools, setTools] = useState([])
  const [scanVals, setScanVals] = useState(SCAN_SETTINGS)
  const [aiVals, setAiVals] = useState(AI_SETTINGS)
  const [appVals, setAppVals] = useState(APP_SETTINGS)
  const [aiReady, setAiReady] = useState(false)

  useEffect(() => {
    fetch('/api/status').then(r => r.json()).then(data => {
      if (data.tools) {
        setTools(Object.entries(data.tools).map(([id, enabled]) => ({
          id,
          label: id,
          desc: '',
          enabled,
        })))
      }
      if (data.ai_ready !== undefined) setAiReady(data.ai_ready)
    }).catch(() => {})
  }, [])

  const toggleTool = (id) => {
    setTools(prev => prev.map(t => t.id === id ? { ...t, enabled: !t.enabled } : t))
  }

  const toggleVal = (id, arr, setter) => {
    setter(prev => prev.map(v => v.id === id && v.type === 'toggle' ? { ...v, value: !v.value } : v))
  }

  const tabs = [
    { id: 'tools', label: 'Toollar' },
    { id: 'scan', label: 'Scan' },
    { id: 'ai', label: 'AI' },
    { id: 'app', label: 'Ilova' },
  ]

  return (
    <div className="settings-page">
      <div className="page-title">Sozlamalar</div>

      <div className="settings-tabs">
        {tabs.map(t => (
          <button key={t.id} className={`settings-tab ${tab === t.id ? 'active' : ''}`} onClick={() => setTab(t.id)}>{t.label}</button>
        ))}
      </div>

      <div className="card">
        {tab === 'tools' && (
          <>
            <div style={{ padding: '8px 0', fontSize: 13, color: 'var(--color-text-secondary)' }}>
              Serverdagi vositalar holati:
            </div>
            {tools.length === 0 ? (
              <div style={{ color: 'var(--color-text-tertiary)', padding: 12 }}>Serverga ulanib bo'lmadi</div>
            ) : (
              tools.map(t => (
                <div className="setting-row" key={t.id}>
                  <div className="setting-label-left">
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                      <IconTerminal2 size={16} style={{ color: 'var(--color-text-secondary)' }} />
                      <span className="setting-label">{t.label}</span>
                    </div>
                    <span className="setting-desc">{t.enabled ? 'O\'rnatilgan' : 'O\'rnatilmagan'}</span>
                  </div>
                  <span className={`badge ${t.enabled ? 'badge-success' : 'badge-danger'}`}>
                    {t.enabled ? '✅' : '❌'}
                  </span>
                </div>
              ))
            )}
          </>
        )}

        {tab === 'scan' && scanVals.map(s => (
          <div className="setting-row" key={s.id}>
            <div className="setting-label-left">
              <span className="setting-label">{s.label}</span>
            </div>
            {s.type === 'toggle' && <Toggle checked={s.value} onChange={() => toggleVal(s.id, scanVals, setScanVals)} />}
            {s.type === 'select' && <select value={s.value} onChange={e => setScanVals(prev => prev.map(v => v.id === s.id ? { ...v, value: e.target.value } : v))}>{s.options.map(o => <option key={o}>{o}</option>)}</select>}
            {s.type === 'number' && <input type="number" value={s.value} onChange={e => setScanVals(prev => prev.map(v => v.id === s.id ? { ...v, value: parseInt(e.target.value) } : v))} style={{ width: 80 }} />}
          </div>
        ))}

        {tab === 'ai' && (
          <>
            <div className="setting-row">
              <div className="setting-label-left">
                <span className="setting-label">AI Engine</span>
                <span className="setting-desc">Local GGUF model</span>
              </div>
              <span className={`badge ${aiReady ? 'badge-success' : 'badge-danger'}`}>
                {aiReady ? '✅ Tayyor' : '❌ Model yo\'q'}
              </span>
            </div>
            {aiVals.map(a => (
              <div className="setting-row" key={a.id}>
                <div className="setting-label-left">
                  <span className="setting-label">{a.label}</span>
                </div>
                {a.type === 'toggle' && <Toggle checked={a.value} onChange={() => toggleVal(a.id, aiVals, setAiVals)} />}
              </div>
            ))}
          </>
        )}

        {tab === 'app' && (
          <>
            {appVals.map(a => (
              <div className="setting-row" key={a.id}>
                <div className="setting-label-left">
                  <span className="setting-label">{a.label}</span>
                </div>
                {a.type === 'select' && (
                  <select value={a.value} onChange={e => {
                    const newVal = [...appVals]
                    const idx = newVal.findIndex(v => v.id === a.id)
                    newVal[idx] = { ...newVal[idx], value: e.target.value }
                    setAppVals(newVal)
                    if (a.id === 'theme') setTheme(e.target.value === 'Yorug\'' ? 'light' : 'dark')
                  }}>
                    {a.options.map(o => <option key={o}>{o}</option>)}
                  </select>
                )}
              </div>
            ))}
          </>
        )}
      </div>
    </div>
  )
}
