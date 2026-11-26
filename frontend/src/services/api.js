import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 120000, // 2 minutes for heavy ML inference
});

// Upload a file
export const uploadFile = async (file, onUploadProgress) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: (progressEvent) => {
      if (onUploadProgress && progressEvent.total) {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        onUploadProgress(percentCompleted);
      }
    },
  });
  return response.data;
};

// Start image analysis
export const analyzeImage = async (uploadId, mode = 'explain') => {
  const response = await api.post('/image/analyze', {
    upload_id: uploadId,
    mode,
  });
  return response.data;
};

// Poll image result
export const getImageResult = async (taskId) => {
  const response = await api.get(`/image/result/${taskId}`);
  return response.data;
};

// Start document analysis
export const analyzeDocument = async (uploadId, mode = 'explain') => {
  const response = await api.post('/document/analyze', {
    upload_id: uploadId,
    mode,
  });
  return response.data;
};

// Poll document result
export const getDocumentResult = async (taskId) => {
  const response = await api.get(`/document/result/${taskId}`);
  return response.data;
};

// Generate audio
export const generateAudio = async (uploadId, text, voice, speed) => {
  const response = await api.post('/audio/generate', {
    upload_id: uploadId,
    text,
    voice,
    speed,
  });
  return response.data;
};

// Get audio stream url
export const getAudioUrl = (audioId) => `/api/audio/${audioId}`;

// History APIs
export const getHistory = async (page = 1, pageSize = 20) => {
  const response = await api.get(`/history?page=${page}&page_size=${pageSize}`);
  return response.data;
};

export const getHistoryItem = async (id) => {
  const response = await api.get(`/history/${id}`);
  return response.data;
};

export const deleteHistoryItem = async (id) => {
  const response = await api.delete(`/history/${id}`);
  return response.data;
};

// Settings APIs
export const getBackendSettings = async () => {
  const response = await api.get('/settings');
  return response.data;
};

export const updateBackendSettings = async (settings) => {
  const response = await api.put('/settings', settings);
  return response.data;
};

// Health Check
export const checkHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

export default api;

