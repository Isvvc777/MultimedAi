import React, { useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { UploadCloud, FileText, Activity, Thermometer, Moon, Heart, Stethoscope, ChevronRight } from 'lucide-react';
import { useAnalysisStore } from '../store/analysisStore';
import { useSubmitAnalysis } from '../api/queries';

const InputPage = () => {
  const navigate = useNavigate();
  const { imageFile, pdfFile, symptoms, sensorData, setImageFile, setPdfFile, addSymptom, removeSymptom, updateSensorData, setAnalysisId } = useAnalysisStore();
  const submitMutation = useSubmitAnalysis();
  
  const imageInputRef = useRef<HTMLInputElement>(null);
  const pdfInputRef = useRef<HTMLInputElement>(null);
  
  const symptomInputRef = useRef<HTMLInputElement>(null);

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) setImageFile(e.target.files[0]);
  };

  const handlePdfChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) setPdfFile(e.target.files[0]);
  };

  const handleAddSymptom = (e: React.FormEvent) => {
    e.preventDefault();
    if (symptomInputRef.current && symptomInputRef.current.value.trim()) {
      addSymptom(symptomInputRef.current.value.trim());
      symptomInputRef.current.value = '';
    }
  };

  const handleSubmit = () => {
    const formData = new FormData();
    if (imageFile) formData.append('image', imageFile);
    if (pdfFile) formData.append('pdf', pdfFile);
    formData.append('sensor_data', JSON.stringify(sensorData));
    formData.append('symptom_text', symptoms.join(', '));

    submitMutation.mutate(formData, {
      onSuccess: (data) => {
        setAnalysisId(data.analysis_id);
        navigate(`/analysis/${data.analysis_id}`);
      },
      onError: (err) => {
        console.error('Failed to submit analysis:', err);
        alert('Failed to submit analysis. Please try again.');
      }
    });
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="text-center">
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">New Analysis</h1>
        <p className="mt-2 text-slate-500">Provide any combination of multi-modal data for a comprehensive AI risk assessment.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Left Column: Files & Symptoms */}
        <div className="space-y-6">
          {/* Image Upload */}
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 transition-all hover:shadow-md">
            <h2 className="text-lg font-semibold flex items-center gap-2 mb-4 text-slate-800">
              <UploadCloud className="text-blue-500" /> Skin/Lesion Image
            </h2>
            <div 
              className="border-2 border-dashed border-slate-200 rounded-xl p-8 text-center cursor-pointer hover:border-blue-500 hover:bg-blue-50 transition-colors"
              onClick={() => imageInputRef.current?.click()}
            >
              <input type="file" className="hidden" accept="image/*" ref={imageInputRef} onChange={handleImageChange} />
              {imageFile ? (
                <p className="text-blue-600 font-medium">{imageFile.name}</p>
              ) : (
                <p className="text-slate-500">Click to browse or drag & drop an image</p>
              )}
            </div>
          </div>

          {/* PDF Upload */}
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 transition-all hover:shadow-md">
            <h2 className="text-lg font-semibold flex items-center gap-2 mb-4 text-slate-800">
              <FileText className="text-rose-500" /> Lab Report (PDF)
            </h2>
            <div 
              className="border-2 border-dashed border-slate-200 rounded-xl p-8 text-center cursor-pointer hover:border-rose-500 hover:bg-rose-50 transition-colors"
              onClick={() => pdfInputRef.current?.click()}
            >
              <input type="file" className="hidden" accept="application/pdf" ref={pdfInputRef} onChange={handlePdfChange} />
              {pdfFile ? (
                <p className="text-rose-600 font-medium">{pdfFile.name}</p>
              ) : (
                <p className="text-slate-500">Upload a recent blood test or lab report</p>
              )}
            </div>
          </div>

          {/* Symptoms */}
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 transition-all hover:shadow-md">
            <h2 className="text-lg font-semibold flex items-center gap-2 mb-4 text-slate-800">
              <Stethoscope className="text-emerald-500" /> Symptoms
            </h2>
            <form onSubmit={handleAddSymptom} className="flex gap-2 mb-4">
              <input 
                type="text" 
                ref={symptomInputRef}
                placeholder="E.g., headache, fever..." 
                className="flex-1 bg-slate-50 border border-slate-200 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all"
              />
              <button type="submit" className="bg-emerald-500 hover:bg-emerald-600 text-white px-4 py-2 rounded-lg font-medium transition-colors">Add</button>
            </form>
            <div className="flex flex-wrap gap-2">
              {symptoms.map((symptom, idx) => (
                <span key={idx} className="inline-flex items-center gap-1 px-3 py-1 bg-emerald-100 text-emerald-800 rounded-full text-sm font-medium">
                  {symptom}
                  <button onClick={() => removeSymptom(symptom)} className="hover:text-emerald-950 font-bold ml-1">&times;</button>
                </span>
              ))}
              {symptoms.length === 0 && <p className="text-slate-400 text-sm">No symptoms added yet.</p>}
            </div>
          </div>
        </div>

        {/* Right Column: Sensor Data */}
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 transition-all hover:shadow-md h-full flex flex-col">
            <h2 className="text-lg font-semibold flex items-center gap-2 mb-6 text-slate-800">
              <Activity className="text-purple-500" /> Vital Signs (Simulated)
            </h2>
            
            <div className="space-y-8 flex-1">
              {/* Heart Rate */}
              <div>
                <div className="flex justify-between items-center mb-2">
                  <label className="text-sm font-semibold flex items-center gap-2 text-slate-700">
                    <Heart size={16} className="text-rose-500" /> Heart Rate (BPM)
                  </label>
                  <span className="font-bold text-slate-900">{sensorData.heartRate}</span>
                </div>
                <input 
                  type="range" min="40" max="150" value={sensorData.heartRate} 
                  onChange={(e) => updateSensorData({ heartRate: parseInt(e.target.value) })}
                  className="w-full accent-rose-500"
                />
              </div>

              {/* SpO2 */}
              <div>
                <div className="flex justify-between items-center mb-2">
                  <label className="text-sm font-semibold flex items-center gap-2 text-slate-700">
                    <Activity size={16} className="text-blue-500" /> SpO2 (%)
                  </label>
                  <span className="font-bold text-slate-900">{sensorData.spo2}%</span>
                </div>
                <input 
                  type="range" min="80" max="100" value={sensorData.spo2} 
                  onChange={(e) => updateSensorData({ spo2: parseInt(e.target.value) })}
                  className="w-full accent-blue-500"
                />
              </div>

              {/* Temperature */}
              <div>
                <div className="flex justify-between items-center mb-2">
                  <label className="text-sm font-semibold flex items-center gap-2 text-slate-700">
                    <Thermometer size={16} className="text-orange-500" /> Temperature (°C)
                  </label>
                  <span className="font-bold text-slate-900">{sensorData.temperature.toFixed(1)}°C</span>
                </div>
                <input 
                  type="range" min="35.0" max="41.0" step="0.1" value={sensorData.temperature} 
                  onChange={(e) => updateSensorData({ temperature: parseFloat(e.target.value) })}
                  className="w-full accent-orange-500"
                />
              </div>

              {/* Sleep */}
              <div>
                <div className="flex justify-between items-center mb-2">
                  <label className="text-sm font-semibold flex items-center gap-2 text-slate-700">
                    <Moon size={16} className="text-indigo-500" /> Sleep (Hours)
                  </label>
                  <span className="font-bold text-slate-900">{sensorData.sleepHours}h</span>
                </div>
                <input 
                  type="range" min="0" max="12" step="0.5" value={sensorData.sleepHours} 
                  onChange={(e) => updateSensorData({ sleepHours: parseFloat(e.target.value) })}
                  className="w-full accent-indigo-500"
                />
              </div>
            </div>

            {/* Submit Button */}
            <div className="mt-8 pt-6 border-t border-slate-100">
              <button 
                onClick={handleSubmit}
                disabled={submitMutation.isPending || (!imageFile && !pdfFile && symptoms.length === 0)}
                className="w-full py-4 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 disabled:cursor-not-allowed text-white rounded-xl font-bold text-lg shadow-lg shadow-blue-500/20 transition-all hover:-translate-y-1 flex items-center justify-center gap-2"
              >
                {submitMutation.isPending ? 'Processing...' : 'Start Full AI Analysis'} 
                {!submitMutation.isPending && <ChevronRight size={20} />}
              </button>
              <p className="text-center text-xs text-slate-400 mt-3">Requires at least one modality (image, document, or symptoms).</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InputPage;
