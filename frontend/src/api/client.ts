import axios from 'axios';

const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const submitAnalysis = async (formData: FormData) => {
  const response = await apiClient.post('/analysis', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const getAnalysisStatus = async (analysisId: string) => {
  const response = await apiClient.get(`/analysis/${analysisId}/status`);
  return response.data;
};

export const getAnalysisReport = async (analysisId: string) => {
  const response = await apiClient.get(`/report/${analysisId}`);
  return response.data;
};

export const downloadReportPdf = async (analysisId: string) => {
  const response = await apiClient.get(`/report/${analysisId}/pdf`, {
    responseType: 'blob', // Important for downloading files
  });
  
  // Create a blob URL and trigger download
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', `MultiMedAI_Report_${analysisId}.pdf`);
  document.body.appendChild(link);
  link.click();
  
  // Clean up
  link.parentNode?.removeChild(link);
  window.URL.revokeObjectURL(url);
};
