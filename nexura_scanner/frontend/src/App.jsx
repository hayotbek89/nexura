import React, { useState, useEffect, createContext, useContext } from 'react'
import Sidebar from './components/Sidebar'
import Scanner from './components/Scanner'
import History from './components/History'
import Reports from './components/Reports'
import Settings from './components/Settings'
import './App.css'

const ThemeContext = createContext()
export const useTheme = () => useContext(ThemeContext)

export default function App() {
  const [activePage, setActivePage] = useState('scanner')
  const [theme, setTheme] = useState(() => localStorage.getItem('nexura-theme') || 'dark')

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('nexura-theme', theme)
  }, [theme])

  const pages = {
    scanner: { component: Scanner, label: 'Scanner', icon: 'ti-radar' },
    history: { component: History, label: 'Tarix', icon: 'ti-history' },
    reports: { component: Reports, label: 'Hisobotlar', icon: 'ti-file-report' },
    settings: { component: Settings, label: 'Sozlamalar', icon: 'ti-settings' },
  }

  const ActiveComponent = pages[activePage].component

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      <div className="app-layout">
        <Sidebar activePage={activePage} setActivePage={setActivePage} pages={pages} />
        <main className="main-content">
          <ActiveComponent />
        </main>
      </div>
    </ThemeContext.Provider>
  )
}
