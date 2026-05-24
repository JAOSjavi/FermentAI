import { useMutation } from "@tanstack/react-query";
import api from "@/lib/api";

interface CambiarEmailPayload {
  nuevo_email: string;
  password_actual: string;
}

interface CambiarPasswordPayload {
  password_actual: string;
  password_nuevo: string;
  password_nuevo_confirm: string;
}

interface AjustesResponse {
  message: string;
}

export function useCambiarEmail() {
  return useMutation<AjustesResponse, { response?: { data?: { detail?: string } } }, CambiarEmailPayload>({
    mutationFn: (payload) =>
      api.put<AjustesResponse>("/api/ajustes/cambiar-email", payload).then((r) => r.data),
  });
}

export function useCambiarPassword() {
  return useMutation<AjustesResponse, { response?: { data?: { detail?: string } } }, CambiarPasswordPayload>({
    mutationFn: (payload) =>
      api.put<AjustesResponse>("/api/ajustes/cambiar-password", payload).then((r) => r.data),
  });
}
