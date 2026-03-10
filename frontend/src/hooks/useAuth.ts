"use client";

import { useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/authStore";
import { authApi } from "@/lib/api";

export function useAuth() {
  const router = useRouter();
  const { token, user, setAuth, clearAuth, isAuthenticated, isAdmin, isAnalyst } =
    useAuthStore();

  async function login(email: string, password: string) {
    const tokenResp = await authApi.login({ username: email, password });
    const me = await authApi.me(tokenResp.access_token);
    setAuth(tokenResp.access_token, me);
    router.push("/dashboard");
  }

  function logout() {
    clearAuth();
    router.push("/login");
  }

  return {
    token,
    user,
    login,
    logout,
    isAuthenticated,
    isAdmin,
    isAnalyst,
  };
}
