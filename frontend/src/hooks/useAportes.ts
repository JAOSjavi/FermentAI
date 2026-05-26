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
    retry: (failureCount, error: any) =>
      error?.response?.status !== 404 && failureCount < 3,
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
    mutationFn: ({ file, descripcion }: { file: File; descripcion?: string }) => {
      const form = new FormData();
      form.append("file", file);
      if (descripcion) form.append("descripcion", descripcion);
      return api.post<Aporte>("/api/aportes/subir", form).then((r) => r.data);
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

export function useEditarDescripcion() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, descripcion }: { id: number; descripcion: string }) =>
      api.put<Aporte>(`/api/aportes/${id}/descripcion`, { descripcion }).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["aportes"] }),
  });
}

export function useSolicitarEliminacion() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, motivo }: { id: number; motivo: string }) =>
      api.post<Aporte>(`/api/aportes/${id}/solicitar-eliminacion`, { motivo }).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["aportes"] }),
  });
}

export function useAprobarEliminacion() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) =>
      api.put(`/api/revisar/${id}/aprobar-eliminacion`).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["aportes"] }),
  });
}

export function useEliminarAporte() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, motivo }: { id: number; motivo: string }) =>
      api.post(`/api/aportes/${id}/eliminar`, { motivo }).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["aportes"] }),
  });
}

export function useRechazarEliminacion() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) =>
      api.put<Aporte>(`/api/revisar/${id}/rechazar-eliminacion`).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["aportes"] }),
  });
}

export function useDescargarDataset() {
  return useMutation({
    mutationFn: async ({
      aporteId,
      fermentacionCodigo,
    }: {
      aporteId: number;
      fermentacionCodigo: string;
    }) => {
      const response = await api.get(`/api/aportes/${aporteId}/descargar-dataset`, {
        responseType: "blob",
      });
      const url = URL.createObjectURL(response.data as Blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${fermentacionCodigo}_dataset.zip`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    },
  });
}
