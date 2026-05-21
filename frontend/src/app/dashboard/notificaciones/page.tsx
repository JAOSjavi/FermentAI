"use client";
import { Bell, CheckCheck } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useNotificaciones, useLeerTodas, useMarcarLeida } from "@/hooks/useNotificaciones";
import { formatDate } from "@/lib/utils";
import { cn } from "@/lib/utils";
import { TipoNotificacion } from "@/types";

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

export default function NotificacionesPage() {
  const { data: notifs, isLoading } = useNotificaciones();
  const { mutate: leerTodas } = useLeerTodas();
  const { mutate: marcarLeida } = useMarcarLeida();

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
          {notifs.map((notif) => (
            <Card
              key={notif.id}
              className={cn(
                "border-l-4 transition-all cursor-pointer",
                TIPO_COLORS[notif.tipo],
                !notif.leida ? "bg-white shadow-sm" : "bg-muted/30"
              )}
              onClick={() => !notif.leida && marcarLeida(notif.id)}
            >
              <CardContent className="p-4 flex items-start gap-3">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-semibold">{TIPO_LABELS[notif.tipo]}</span>
                    {!notif.leida && (
                      <span className="h-2 w-2 rounded-full bg-blue-500 flex-shrink-0" />
                    )}
                  </div>
                  <p className="text-sm text-muted-foreground mt-0.5">{notif.mensaje}</p>
                  <p className="text-xs text-muted-foreground mt-1">{formatDate(notif.created_at)}</p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
