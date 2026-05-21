"use client";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";
import { Aporte } from "@/types";

export function useMisAportes() {
  return useQuery<Aporte[]>({
    queryKey: ["aportes", "me"],
    queryFn: () => api.get("/api/aportes/me").then((r) => r.data),
  });
}

export function useAporteDetalle(id: number, forRevision = false) {
  return useQuery<Aporte>({
    queryKey: ["aportes", id, forRevision],
    queryFn: () => {
      const url = forRevision ? `/api/revisar/${id}/revisar` : `/api/aportes/${id}`;
      return api.get(url).then((r) => r.data);
    },
    enabled: !!id,
  });
}

export function usePendientes() {
  return useQuery<Aporte[]>({
    queryKey: ["aportes", "pendientes"],
    queryFn: () => api.get("/api/revisar/pendientes").then((r) => r.data),
  });
}

export function useSubirAporte() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (file: File) => {
      const form = new FormData();
      form.append("file", file);
      return api.post<Aporte>("/api/aportes/subir", form, {
        headers: { "Content-Type": "multipart/form-data" },
      }).then((r) => r.data);
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["aportes"] }),
  });
}

export function useAprobar() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => api.put<Aporte>(`/api/revisar/${id}/aprobar`).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["aportes"] }),
  });
}

export function useRechazar() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, observaciones }: { id: number; observaciones: string }) =>
      api.put<Aporte>(`/api/revisar/${id}/rechazar`, { observaciones }).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["aportes"] }),
  });
}

export function useSolicitarCorrecciones() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, observaciones }: { id: number; observaciones: string }) =>
      api.put<Aporte>(`/api/revisar/${id}/solicitar-correcciones`, { observaciones }).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["aportes"] }),
  });
}
