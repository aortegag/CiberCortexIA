"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { UserMe } from "@/types/api";

interface AuthState {
  token: string | null;
  user: UserMe | null;
  setAuth: (token: string, user: UserMe) => void;
  clearAuth: () => void;
  isAuthenticated: () => boolean;
  isAdmin: () => boolean;
  isAnalyst: () => boolean;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      token: null,
      user: null,

      setAuth: (token, user) => set({ token, user }),

      clearAuth: () => set({ token: null, user: null }),

      isAuthenticated: () => !!get().token,

      isAdmin: () => get().user?.role === "admin",

      isAnalyst: () =>
        get().user?.role === "admin" || get().user?.role === "analyst",
    }),
    {
      name: "cibercortex-auth",
      partialize: (state) => ({ token: state.token, user: state.user }),
    }
  )
);
