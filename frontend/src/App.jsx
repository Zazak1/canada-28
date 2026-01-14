import './index.css'
import CurrentDraw from './components/CurrentDraw'
import PredictionPanel from './components/PredictionPanel'
import IssueQuery from './components/IssueQuery'

function App() {
  return (
    <div className="max-w-4xl mx-auto space-y-6 p-4 md:p-8">
      <CurrentDraw />

      {/* 期号查询 */}
      <IssueQuery />

      <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
        <PredictionPanel />
      </div>
    </div>
  )
}

export default App
