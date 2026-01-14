import { Routes, Route, Link } from 'react-router-dom'
import './index.css'
import CurrentDraw from './components/CurrentDraw'
import PredictionPanel from './components/PredictionPanel'
import HistoryPage from './pages/HistoryPage'

function Home() {
  return (
    <div className="max-w-4xl mx-auto space-y-6 p-4 md:p-8">
      <CurrentDraw />

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
