import React from 'react'
import { IconShieldCheck, IconRadar, IconHistory, IconFileReport, IconSettings } from '@tabler/icons-react'

const iconMap = {
  'ti-radar': IconRadar,
  'ti-history': IconHistory,
  'ti-file-report': IconFileReport,
  'ti-settings': IconSettings,
}

export default function Sidebar({ activePage, setActivePage, pages }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <IconShieldCheck size={20} />
        <span>NEXURA</span>
      </div>
      <nav className="sidebar-nav">
        {Object.entries(pages).map(([key, page]) => {
          const Icon = iconMap[page.icon] || IconRadar
          return (
            <button
              key={key}
              className={`sidebar-item ${activePage === key ? 'active' : ''}`}
              onClick={() => setActivePage(key)}
            >
              <Icon size={18} />
              <span>{page.label}</span>
            </button>
          )
        })}
      </nav>
    </aside>
  )
}
