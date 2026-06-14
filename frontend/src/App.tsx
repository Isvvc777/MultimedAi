import { Routes, Route } from 'react-router-dom'
import InputPage from './pages/InputPage'
import AnalysisPage from './pages/AnalysisPage'
import ReportPage from './pages/ReportPage'
import ChatPage from './pages/ChatPage'

function App() {
  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900 font-sans">
      {/* Navigation will go here */}
      <header className="bg-white shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold">M</div>
            <span className="font-bold text-xl tracking-tight text-slate-800">MultiMed<span className="text-blue-600">AI</span></span>
          </div>
          <nav className="hidden md:flex gap-6 text-sm font-medium text-slate-600">
            <a href="/" className="hover:text-blue-600 transition-colors">Dashboard</a>
            <a href="/new-analysis" className="hover:text-blue-600 transition-colors">New Analysis</a>
          </nav>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Routes>
          <Route path="/" element={
            <div className="text-center py-20 animate-in fade-in slide-in-from-bottom-4 duration-700">
              <h1 className="text-4xl font-extrabold text-slate-900 tracking-tight sm:text-5xl">
                Medical AI Platform
              </h1>
              <p className="mt-4 text-lg text-slate-600 max-w-2xl mx-auto">
                Upload images, reports, symptoms, and sensor data for an automated, multi-modal risk assessment.
              </p>
              <div className="mt-8">
                <a href="/new-analysis" className="inline-flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-xl text-white bg-blue-600 hover:bg-blue-700 shadow-md shadow-blue-500/20 transition-all hover:-translate-y-0.5">
                  Start New Analysis
                </a>
              </div>
            </div>
          } />
          <Route path="/new-analysis" element={<InputPage />} />
          <Route path="/analysis/:id" element={<AnalysisPage />} />
          <Route path="/report/:id" element={<ReportPage />} />
          <Route path="/chat/:id" element={<ChatPage />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
