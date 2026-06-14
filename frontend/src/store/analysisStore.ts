import { create } from 'zustand';

interface SensorData {
  heartRate: number;
  spo2: number;
  temperature: number;
  sleepHours: number;
}

interface AnalysisState {
  imageFile: File | null;
  pdfFile: File | null;
  symptoms: string[];
  sensorData: SensorData;
  analysisId: string | null;
  
  setImageFile: (file: File | null) => void;
  setPdfFile: (file: File | null) => void;
  addSymptom: (symptom: string) => void;
  removeSymptom: (symptom: string) => void;
  updateSensorData: (data: Partial<SensorData>) => void;
  setAnalysisId: (id: string | null) => void;
  reset: () => void;
}

const initialSensorData: SensorData = {
  heartRate: 75,
  spo2: 98,
  temperature: 36.6,
  sleepHours: 7,
};

export const useAnalysisStore = create<AnalysisState>((set) => ({
  imageFile: null,
  pdfFile: null,
  symptoms: [],
  sensorData: initialSensorData,
  analysisId: null,

  setImageFile: (file) => set({ imageFile: file }),
  setPdfFile: (file) => set({ pdfFile: file }),
  addSymptom: (symptom) => set((state) => ({ 
    symptoms: state.symptoms.includes(symptom) ? state.symptoms : [...state.symptoms, symptom] 
  })),
  removeSymptom: (symptom) => set((state) => ({ 
    symptoms: state.symptoms.filter(s => s !== symptom) 
  })),
  updateSensorData: (data) => set((state) => ({ 
    sensorData: { ...state.sensorData, ...data } 
  })),
  setAnalysisId: (id) => set({ analysisId: id }),
  reset: () => set({ 
    imageFile: null, 
    pdfFile: null, 
    symptoms: [], 
    sensorData: initialSensorData,
    analysisId: null
  }),
}));
