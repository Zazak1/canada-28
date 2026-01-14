import { Routes, Route, Link } from 'react-router-dom'
import './index.css'
import CurrentDraw from './components/CurrentDraw'
import PredictionPanel from './components/PredictionPanel'
import HistoryPage from './pages/HistoryPage'

function Home() {
  return (
    <div className="max-w-4xl mx-auto space-y-6 p-4 md:p-8">
      <CurrentDraw />

      {/* 开奖公告按钮 */}
      <div className="flex justify-center">
        <Link 
          to="/history"
          className="inline-flex items-center gap-2 px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors font-medium shadow-sm"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          查看开奖公告
        </Link>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
        <PredictionPanel />
      </div>
    </div>
  )
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/history" element={<HistoryPage />} />
    </Routes>
  )
}

export default App
