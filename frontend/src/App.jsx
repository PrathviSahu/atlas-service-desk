import { useState, useCallback } from 'react'
import Dashboard from './pages/Dashboard'
import Inbox from './pages/Inbox'
import RequestModal from './components/RequestModal'
import Toast from './components/Toast'

export default function App() {
  const [activePage, setActivePage] = useState('dashboard')
  const [selectedRequestId, setSelectedRequestId] = useState(null)
  const [toast, setToast] = useState(null)
  const [refreshKey, setRefreshKey] = useState(0)

  const openRequest = useCallback((id) => {
    setSelectedRequestId(id)
  }, [])

  const closeModal = useCallback(() => {
    setSelectedRequestId(null)
  }, [])

  const handleUpdated = useCallback((updated) => {
    setToast(`Request ${updated.id} saved.`)
    setRefreshKey(k => k + 1)
  }, [])

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="topbar__logo">
          <div className="topbar__logo-icon">⚙</div>
          Atlas Service Desk
          <span style={{ fontSize: 11, color: 'var(--color-text-dim)', fontWeight: 400, marginLeft: 6 }}>
            Atlas Industrial Services
          </span>
        </div>
        <nav className="topbar__nav" aria-label="Main navigation">
          <button
            className={`topbar__nav-btn ${activePage === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActivePage('dashboard')}
            id="nav-dashboard"
          >
            Dashboard
          </button>
          <button
            className={`topbar__nav-btn ${activePage === 'inbox' ? 'active' : ''}`}
            onClick={() => setActivePage('inbox')}
            id="nav-inbox"
          >
            Request Inbox
          </button>
        </nav>
      </header>

      <main className="main-content">
        {activePage === 'dashboard' && (
          <Dashboard key={refreshKey} onOpenRequest={openRequest} />
        )}
        {activePage === 'inbox' && (
          <Inbox key={refreshKey} onOpenRequest={openRequest} />
        )}
      </main>

      {selectedRequestId && (
        <RequestModal
          requestId={selectedRequestId}
          onClose={closeModal}
          onUpdated={handleUpdated}
        />
      )}

      {toast && (
        <Toast message={toast} onClose={() => setToast(null)} />
      )}
    </div>
  )
}
