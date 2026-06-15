import { useParams, useNavigate } from 'react-router-dom';
import { useAnalysisReport } from '../api/queries';
import { downloadReportPdf } from '../api/client';
import { AlertTriangle, Info, Activity, FileText, Image as ImageIcon, HeartPulse, MessageSquare, ChevronLeft, Download } from 'lucide-react';

const ReportPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: report, isLoading, isError } = useAnalysisReport(id || null);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (isError || !report) {
    return (
      <div className="text-center text-red-500 mt-20">
        <AlertTriangle className="w-12 h-12 mx-auto mb-4" />
        <h2 className="text-2xl font-bold">Failed to load report</h2>
        <button onClick={() => navigate('/')} className="mt-4 text-blue-600 hover:underline">Return Home</button>
      </div>
    );
  }

  const { global_score, risk_level, recommendations, full_text, modality_results = [] } = report;
  const recommendation = recommendations?.note || full_text || "No specific recommendations provided.";

  // Extract modalities
  const yolo_modality = modality_results.find((m: any) => m.modality === 'image');
  const ocr_modality = modality_results.find((m: any) => m.modality === 'pdf');
  const llm_modality = modality_results.find((m: any) => m.modality === 'text');
  const sensor_modality = modality_results.find((m: any) => m.modality === 'sensor');

  // Map to old expected names
  const yolo_result = yolo_modality ? { ...yolo_modality, detections: yolo_modality.raw_output?.detections || [] } : null;
  const ocr_result = ocr_modality ? { ...ocr_modality, clinical_summary: ocr_modality.summary } : null;
  const llm_result = llm_modality ? { ...llm_modality, clinical_summary: llm_modality.summary } : null;
  const sensor_result = sensor_modality ? { ...sensor_modality, clinical_summary: sensor_modality.summary } : null;

  // Determine colors based on risk level
  const riskConfig = {
    normal: { color: 'text-emerald-500', bg: 'bg-emerald-50', border: 'border-emerald-200', bar: 'bg-emerald-500', label: 'Normal' },
    surveiller: { color: 'text-amber-500', bg: 'bg-amber-50', border: 'border-amber-200', bar: 'bg-amber-500', label: 'Monitor' },
    urgent: { color: 'text-rose-500', bg: 'bg-rose-50', border: 'border-rose-200', bar: 'bg-rose-500', label: 'Urgent' },
  };

  const currentRisk = riskConfig[risk_level as keyof typeof riskConfig] || riskConfig.normal;
  const scorePercentage = Math.min(Math.round(global_score * 100), 100);

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-8 duration-700">
      {/* Header Actions */}
      <div className="flex justify-between items-center">
        <button onClick={() => navigate('/new-analysis')} className="flex items-center gap-2 text-slate-500 hover:text-slate-900 transition-colors">
          <ChevronLeft size={20} /> New Analysis
        </button>
        <div className="flex items-center gap-3">
          <button 
            onClick={() => {
              if (id) {
                downloadReportPdf(id).catch(err => console.error("Failed to download PDF", err));
              }
            }}
            className="flex items-center gap-2 px-6 py-2.5 bg-slate-100 text-slate-700 border border-slate-200 rounded-full font-semibold hover:bg-slate-200 transition-all"
          >
            <Download size={18} /> Download PDF
          </button>
          <button onClick={() => navigate(`/chat/${id}`)} className="flex items-center gap-2 px-6 py-2.5 bg-blue-600 text-white rounded-full font-semibold shadow-md shadow-blue-500/20 hover:bg-blue-700 hover:scale-105 transition-all">
            <MessageSquare size={18} /> Chat with AI
          </button>
        </div>
      </div>

      {/* Main Gauge & Global Result */}
      <div className={`p-8 rounded-3xl border shadow-sm flex flex-col md:flex-row items-center gap-8 ${currentRisk.bg} ${currentRisk.border}`}>
        <div className="relative w-48 h-48 flex-shrink-0 flex flex-col items-center justify-center bg-white rounded-full shadow-inner border border-slate-100">
           {/* Simple circular representation of score */}
           <span className={`text-5xl font-black ${currentRisk.color}`}>{scorePercentage}%</span>
           <span className="text-slate-500 text-sm font-medium mt-1 uppercase tracking-widest">Risk Score</span>
           
           <svg className="absolute inset-0 w-full h-full transform -rotate-90" viewBox="0 0 100 100">
             <circle cx="50" cy="50" r="46" fill="transparent" stroke="#f1f5f9" strokeWidth="8" />
             <circle cx="50" cy="50" r="46" fill="transparent" stroke="currentColor" strokeWidth="8" 
               className={currentRisk.color}
               strokeDasharray={`${scorePercentage * 2.89} 289`}
               strokeLinecap="round" 
               style={{ transition: 'stroke-dasharray 1.5s ease-out' }}
             />
           </svg>
        </div>

        <div className="flex-1 space-y-4 text-center md:text-left">
          <div className={`inline-block px-4 py-1.5 rounded-full text-sm font-bold uppercase tracking-widest bg-white shadow-sm ${currentRisk.color}`}>
            {currentRisk.label}
          </div>
          <h1 className="text-3xl font-extrabold text-slate-900">AI Fusion Assessment</h1>
          <p className="text-lg text-slate-700 leading-relaxed font-medium bg-white/60 p-4 rounded-xl border border-white/40">
            {recommendation}
          </p>
        </div>
      </div>

      {/* Modality Breakdowns */}
      <h2 className="text-2xl font-bold text-slate-800 pt-4">Detailed Modality Insights</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Image Card */}
        {yolo_result && (
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 hover:shadow-md transition-shadow">
            <h3 className="text-lg font-bold flex items-center gap-2 mb-4 text-slate-800">
              <ImageIcon className="text-blue-500" /> Skin/Lesion Image
            </h3>
            <div className="mb-2 flex justify-between items-center text-sm font-medium">
              <span className="text-slate-500">Risk Contribution</span>
              <span className="text-blue-600 font-bold">{(yolo_result.risk_score * 100).toFixed(0)}%</span>
            </div>
            <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden mb-4">
              <div className="h-full bg-blue-500 rounded-full" style={{ width: `${yolo_result.risk_score * 100}%` }}></div>
            </div>
            {yolo_result.detections.length > 0 ? (
              <ul className="space-y-2">
                {yolo_result.detections.map((d: any, idx: number) => (
                  <li key={idx} className="bg-blue-50 px-3 py-2 rounded-lg text-sm flex justify-between">
                    <span className="font-medium text-blue-900 capitalize">{d.label || d.class_name || 'Unknown Detection'}</span>
                    <span className="text-blue-700">{(d.confidence * 100).toFixed(1)}% conf</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-slate-500 italic">No significant findings detected.</p>
            )}
          </div>
        )}

        {/* OCR Card */}
        {ocr_result && (
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 hover:shadow-md transition-shadow">
            <h3 className="text-lg font-bold flex items-center gap-2 mb-4 text-slate-800">
              <FileText className="text-rose-500" /> Lab Report
            </h3>
            <div className="mb-2 flex justify-between items-center text-sm font-medium">
              <span className="text-slate-500">Risk Contribution</span>
              <span className="text-rose-600 font-bold">{(ocr_result.risk_score * 100).toFixed(0)}%</span>
            </div>
            <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden mb-4">
              <div className="h-full bg-rose-500 rounded-full" style={{ width: `${ocr_result.risk_score * 100}%` }}></div>
            </div>
            <div className="bg-rose-50 p-4 rounded-xl">
              <p className="text-sm text-rose-900 font-medium">{ocr_result.clinical_summary}</p>
            </div>
          </div>
        )}

        {/* Symptoms Card */}
        {llm_result && (
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 hover:shadow-md transition-shadow">
            <h3 className="text-lg font-bold flex items-center gap-2 mb-4 text-slate-800">
              <Activity className="text-emerald-500" /> Symptoms Analysis
            </h3>
            <div className="mb-2 flex justify-between items-center text-sm font-medium">
              <span className="text-slate-500">Risk Contribution</span>
              <span className="text-emerald-600 font-bold">{(llm_result.risk_score * 100).toFixed(0)}%</span>
            </div>
            <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden mb-4">
              <div className="h-full bg-emerald-500 rounded-full" style={{ width: `${llm_result.risk_score * 100}%` }}></div>
            </div>
            <div className="bg-emerald-50 p-4 rounded-xl">
              <p className="text-sm text-emerald-900 font-medium">{llm_result.clinical_summary}</p>
            </div>
          </div>
        )}

        {/* Sensors Card */}
        {sensor_result && (
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 hover:shadow-md transition-shadow">
            <h3 className="text-lg font-bold flex items-center gap-2 mb-4 text-slate-800">
              <HeartPulse className="text-purple-500" /> Vital Signs
            </h3>
            <div className="mb-2 flex justify-between items-center text-sm font-medium">
              <span className="text-slate-500">Risk Contribution</span>
              <span className="text-purple-600 font-bold">{(sensor_result.risk_score * 100).toFixed(0)}%</span>
            </div>
            <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden mb-4">
              <div className="h-full bg-purple-500 rounded-full" style={{ width: `${sensor_result.risk_score * 100}%` }}></div>
            </div>
            <div className="bg-purple-50 p-4 rounded-xl mb-4">
              <p className="text-sm text-purple-900 font-medium">{sensor_result.clinical_summary}</p>
            </div>
          </div>
        )}

      </div>

      {/* Disclaimer */}
      <div className="bg-slate-50 border border-slate-200 rounded-2xl p-6 flex items-start gap-4 mt-12">
        <Info className="text-slate-400 flex-shrink-0 mt-1" />
        <div>
          <h4 className="font-bold text-slate-700 text-sm uppercase tracking-wider mb-1">Medical Disclaimer</h4>
          <p className="text-sm text-slate-500 leading-relaxed">
            This platform uses Artificial Intelligence to analyze uploaded medical data. It is designed for informational and educational purposes only. The results, risk scores, and recommendations provided do not constitute medical advice, diagnosis, or treatment. Always consult with a qualified healthcare provider for proper medical evaluation.
          </p>
        </div>
      </div>

    </div>
  );
};

export default ReportPage;
