"use client";
import { useState, useEffect, useCallback } from "react";
import { User } from "@/types";
import api from "@/lib/api";
import {
  getToken, getStoredUser, setToken, setStoredUser, removeToken,
} from "@/lib/auth";

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const stored = getStoredUser();
    const token = getToken();
    if (stored && token) {
      setUser(stored);
      // Refresh from API
      api.get<User>("/api/auth/me").then((res) => {
        setUser(res.data);
        setStoredUser(res.data);
      }).catch(() => {
        removeToken();
        setUser(null);
      }).finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const { data } = await api.post<{ access_token: string }>("/api/auth/login", { email, password });
    setToken(data.access_token);
    const { data: me } = await api.get<User>("/api/auth/me");
    setStoredUser(me);
    setUser(me);
    return me;
  }, []);

  const logout = useCallback(() => {
    removeToken();
    setUser(null);
  }, []);

  return { user, loading, login, logout };
}
