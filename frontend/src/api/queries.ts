import { useMutation, useQuery } from '@tanstack/react-query';
import { submitAnalysis, getAnalysisStatus, getAnalysisReport } from './client';

export const useSubmitAnalysis = () => {
  return useMutation({
    mutationFn: (formData: FormData) => submitAnalysis(formData),
  });
};

export const useAnalysisStatus = (analysisId: string | null, enabled: boolean) => {
  return useQuery({
    queryKey: ['analysis-status', analysisId],
    queryFn: () => getAnalysisStatus(analysisId as string),
    enabled: !!analysisId && enabled,
    refetchInterval: (query) => {
      // Stop polling if status is completed or failed
      const status = query.state?.data?.status;
      if (status === 'completed' || status === 'failed') {
        return false;
      }
      return 2000; // Poll every 2 seconds
    },
  });
};

export const useAnalysisReport = (analysisId: string | null) => {
  return useQuery({
    queryKey: ['analysis-report', analysisId],
    queryFn: () => getAnalysisReport(analysisId as string),
    enabled: !!analysisId,
  });
};
