"use client";
import { Bell, CheckCheck, ChevronRight } from "lucide-react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useNotificaciones, useLeerTodas, useMarcarLeida } from "@/hooks/useNotificaciones";
import { formatDate } from "@/lib/utils";
import { cn } from "@/lib/utils";
import { TipoNotificacion, Notificacion } from "@/types";

const TIPO_LABELS: Record<TipoNotificacion, string> = {
  aporte_aprobado: "Aporte Aprobado",
  aporte_rechazado: "Aporte Rechazado",
  correcciones_solicitadas: "Correcciones Solicitadas",
  nuevo_aporte_pendiente: "Nuevo Aporte Pendiente",
};

const TIPO_COLORS: Record<TipoNotificacion, string> = {
  aporte_aprobado: "border-l-emerald-400",
  aporte_rechazado: "border-l-red-400",
  correcciones_solicitadas: "border-l-amber-400",
  nuevo_aporte_pendiente: "border-l-blue-400",
};

function getDestino(notif: Notificacion): string | null {
  if (!notif.aporte_id) return null;
  if (notif.tipo === "nuevo_aporte_pendiente") {
    return `/dashboard/revisar/${notif.aporte_id}`;
  }
  return `/dashboard/mis-aportes/${notif.aporte_id}`;
}

export default function NotificacionesPage() {
  const router = useRouter();
  const { data: notifs, isLoading } = useNotificaciones();
  const { mutate: leerTodas } = useLeerTodas();
  const { mutate: marcarLeida } = useMarcarLeida();

  function handleClick(notif: Notificacion) {
    if (!notif.leida) marcarLeida(notif.id);
    const destino = getDestino(notif);
    if (destino) router.push(destino);
  }

  const unread = notifs?.filter((n) => !n.leida).length ?? 0;

  return (
    <div className="space-y-6 max-w-2xl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Notificaciones</h1>
          <p className="text-muted-foreground">
            {unread > 0 ? `${unread} sin leer` : "Todas leídas"}
          </p>
        </div>
        {unread > 0 && (
          <Button variant="outline" size="sm" onClick={() => leerTodas()}>
            <CheckCheck className="h-4 w-4" />
            Marcar todas como leídas
          </Button>
        )}
      </div>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <div className="h-8 w-8 animate-spin rounded-full border-[3px] border-indigo-200 border-t-indigo-600" />
        </div>
      ) : !notifs?.length ? (
        <Card>
          <CardContent className="flex flex-col items-center py-16 gap-4">
            <Bell className="h-12 w-12 text-muted-foreground" />
            <p className="text-muted-foreground">No tienes notificaciones.</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-2">
          {notifs.map((notif) => {
            const destino = getDestino(notif);
            return (
              <Card
                key={notif.id}
                className={cn(
                  "border-l-4 transition-all",
                  TIPO_COLORS[notif.tipo],
                  !notif.leida ? "bg-white shadow-sm" : "bg-muted/30",
                  destino ? "cursor-pointer hover:shadow-md hover:-translate-y-px" : "cursor-default"
                )}
                onClick={() => handleClick(notif)}
              >
                <CardContent className="p-4 flex items-center gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-semibold">{TIPO_LABELS[notif.tipo]}</span>
                      {!notif.leida && (
                        <span className="h-2 w-2 rounded-full bg-blue-500 flex-shrink-0" />
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground mt-0.5">{notif.mensaje}</p>
                    <p className="text-xs text-muted-foreground mt-1">{formatDate(notif.created_at)}</p>
                  </div>
                  {destino && (
                    <ChevronRight className="h-4 w-4 flex-shrink-0 text-slate-400" />
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
