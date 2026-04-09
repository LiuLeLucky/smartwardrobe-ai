import { create } from 'zustand';

interface User {
  email: string;
}

interface AuthState {
  token: string | null;
  user: User | null;
  setToken: (token: string) => void;
  setUser: (user: User) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: null,
  user: null,
  setToken: (token) => set({ token }),
  setUser: (user) => set({ user }),
  logout: () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('sw_token');
      document.cookie = 'sw_token=; path=/; max-age=0';
    }
    set({ token: null, user: null });
  },
}));
