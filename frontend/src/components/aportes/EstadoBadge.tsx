import { Badge } from "@/components/ui/badge";
import { EstadoAporte } from "@/types";

const config: Record<EstadoAporte, { label: string; variant: "success" | "destructive" | "warning" | "info" | "secondary" }> = {
  aprobado: { label: "Aprobado", variant: "success" },
  rechazado: { label: "Rechazado", variant: "destructive" },
  pendiente_revision: { label: "Pendiente", variant: "warning" },
  correcciones_solicitadas: { label: "Correcciones", variant: "info" },
};

export function EstadoBadge({ estado }: { estado: EstadoAporte }) {
  const { label, variant } = config[estado] ?? { label: estado, variant: "secondary" };
  return <Badge variant={variant}>{label}</Badge>;
}
