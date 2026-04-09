import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
});

api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('sw_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && typeof window !== 'undefined') {
      localStorage.removeItem('sw_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const auth = {
  register: (email: string, password: string) =>
    api.post('/auth/register', { email, password }),

  login: (email: string, password: string) => {
    const form = new URLSearchParams();
    form.append('username', email);
    form.append('password', password);
    return api.post<{ access_token: string }>('/auth/login', form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
  },
};

export const clothing = {
  getAll: () => api.get('/clothing/'),
  create: (data: Record<string, unknown>) => api.post('/clothing/', data),
  update: (id: string, data: Record<string, unknown>) =>
    api.patch(`/clothing/${id}`, data),
  delete: (id: string) => api.delete(`/clothing/${id}`),
  uploadImage: (id: string, file: File) => {
    const form = new FormData();
    form.append('file', file);
    return api.post(`/clothing/${id}/upload-image`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};

export const outfits = {
  getAll: () => api.get('/outfits/'),
  create: (data: { name: string; occasion: string; clothing_item_ids: string[] }) =>
    api.post('/outfits/', data),
  generate: (occasion: string, style_preference: string) =>
    api.post('/outfits/generate', { occasion, style_preference }),
  save: (id: string) => api.post(`/outfits/${id}/save`),
  delete: (id: string) => api.delete(`/outfits/${id}`),
};

export default api;
