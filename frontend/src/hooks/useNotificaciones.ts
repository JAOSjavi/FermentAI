"use client";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";
import { Notificacion } from "@/types";

export function useNotificaciones() {
  return useQuery<Notificacion[]>({
    queryKey: ["notificaciones"],
    queryFn: () => api.get("/api/notificaciones/me").then((r) => r.data),
    refetchInterval: 30_000,
  });
}

export function useMarcarLeida() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => api.put(`/api/notificaciones/${id}/leer`).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["notificaciones"] }),
  });
}

export function useLeerTodas() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => api.put("/api/notificaciones/me/leer-todas").then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["notificaciones"] }),
  });
}
