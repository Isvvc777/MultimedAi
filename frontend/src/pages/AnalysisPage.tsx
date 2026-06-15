import { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Loader2, CheckCircle, Circle, AlertCircle } from 'lucide-react';
import { useAnalysisStatus } from '../api/queries';

const AnalysisPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  const { data, isLoading, isError } = useAnalysisStatus(id || null, true);

  useEffect(() => {
    if (data?.status === 'done') {
      navigate(`/report/${id}`, { replace: true });
    }
  }, [data?.status, id, navigate]);

  const steps = [
    { key: 'upload', label: 'Uploading files and data' },
    { key: 'processing_image', label: 'Analyzing image with YOLOv8' },
    { key: 'processing_pdf', label: 'Extracting lab reports with OCR' },
    { key: 'processing_text', label: 'Analyzing symptoms with LLM' },
    { key: 'processing_sensors', label: 'Evaluating vital signs' },
    { key: 'fusing_data', label: 'Fusing multimodal data' },
    { key: 'generating_report', label: 'Generating comprehensive report' },
  ];

  // Derive current step index based on progress (0 to 100)
  const progress = data?.progress || 0;
  let currentStepIndex = Math.floor((progress / 100) * steps.length);
  if (data?.status === 'done') currentStepIndex = steps.length;

  if (isError || data?.status === 'failed') {
    return (
      <div className="max-w-2xl mx-auto mt-20 p-8 bg-red-50 rounded-2xl border border-red-200 text-center animate-in fade-in zoom-in duration-500">
        <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-red-900 mb-2">Analysis Failed</h2>
        <p className="text-red-700">An error occurred during the analysis process. Please try again.</p>
        <button 
          onClick={() => navigate('/new-analysis')}
          className="mt-6 px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
        >
          Return to Upload
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto space-y-8 animate-in fade-in duration-700">
      <div className="text-center">
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Analyzing Data</h1>
        <p className="mt-2 text-slate-500">Please wait while our AI engines process your information.</p>
      </div>

      <div className="bg-white p-8 rounded-3xl shadow-lg border border-slate-100">
        <div className="flex items-center justify-center mb-8">
          <div className="relative w-32 h-32 flex items-center justify-center">
            {data?.status === 'done' ? (
              <CheckCircle className="w-20 h-20 text-emerald-500 animate-in zoom-in" />
            ) : (
              <Loader2 className="w-20 h-20 text-blue-500 animate-spin" />
            )}
            <div className="absolute inset-0 border-4 border-slate-100 rounded-full"></div>
            <div 
              className="absolute inset-0 border-4 border-blue-500 rounded-full transition-all duration-500 ease-out" 
              style={{ clipPath: `inset(${100 - progress}% 0 0 0)` }}
            ></div>
          </div>
        </div>
        
        <h3 className="text-center text-2xl font-bold text-slate-800 mb-2">{progress}% Complete</h3>
        
        <div className="mt-10 space-y-4">
          {steps.map((step, index) => {
            const isCompleted = index < currentStepIndex;
            const isCurrent = index === currentStepIndex && data?.status !== 'done';
            
            return (
              <div 
                key={step.key} 
                className={`flex items-center gap-4 transition-all duration-500 ${isCurrent ? 'opacity-100 scale-105 transform translate-x-2' : isCompleted ? 'opacity-50' : 'opacity-30'}`}
              >
                {isCompleted ? (
                  <CheckCircle className="w-6 h-6 text-emerald-500 flex-shrink-0" />
                ) : isCurrent ? (
                  <Loader2 className="w-6 h-6 text-blue-500 animate-spin flex-shrink-0" />
                ) : (
                  <Circle className="w-6 h-6 text-slate-300 flex-shrink-0" />
                )}
                <span className={`font-medium ${isCurrent ? 'text-blue-700 font-bold' : isCompleted ? 'text-slate-500' : 'text-slate-400'}`}>
                  {step.label}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default AnalysisPage;
