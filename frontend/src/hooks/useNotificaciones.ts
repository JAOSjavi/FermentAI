"use client";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";
import { Notificacion } from "@/types";
import { useAuth } from "@/hooks/useAuth";

export function useNotificaciones() {
  const { user } = useAuth();
  return useQuery<Notificacion[]>({
    queryKey: ["notificaciones", user?.id],
    queryFn: () => api.get("/api/notificaciones/me").then((r) => r.data),
    refetchInterval: 30_000,
    enabled: !!user?.id,
  });
}

export function useMarcarLeida() {
  const { user } = useAuth();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => api.put(`/api/notificaciones/${id}/leer`).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["notificaciones", user?.id] }),
  });
}

export function useLeerTodas() {
  const { user } = useAuth();
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => api.put("/api/notificaciones/me/leer-todas").then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["notificaciones", user?.id] }),
  });
}
