"use client";
import { useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Eye, ClipboardList } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { EstadoBadge } from "@/components/aportes/EstadoBadge";
import { usePendientes } from "@/hooks/useAportes";
import { useAuth } from "@/hooks/useAuth";
import { formatDate } from "@/lib/utils";

export default function RevisarPage() {
  const { user }  = useAuth();
  const router    = useRouter();
  const { data: pendientes, isLoading } = usePendientes();

  useEffect(() => {
    if (user && user.rol !== "investigador") {
      router.replace("/dashboard");
    }
  }, [user, router]);

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="font-display text-2xl font-bold tracking-tight text-slate-900">Revisar Aportes</h1>
        <p className="text-sm text-muted-foreground mt-0.5">Aportes pendientes de revisión científica</p>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <div className="h-8 w-8 animate-spin rounded-full border-[3px] border-violet-200 border-t-violet-600" />
        </div>
      ) : !pendientes?.length ? (
        <Card className="border-slate-100">
          <CardContent className="flex flex-col items-center py-16 gap-4">
            <ClipboardList className="h-12 w-12 text-slate-300" />
            <p className="text-muted-foreground font-medium">No hay aportes pendientes de revisión.</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {pendientes.map((aporte) => (
            <Card
              key={aporte.id}
              className="hover:shadow-md transition-shadow duration-200 border-slate-100 border-l-4 border-l-violet-400"
            >
              <CardContent className="p-5 flex items-center gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-semibold font-mono-code text-sm text-violet-700">
                      {aporte.fermentacion?.codigo ?? `Aporte #${aporte.id}`}
                    </span>
                    <EstadoBadge estado={aporte.estado} />
                  </div>
                  <p className="text-sm text-muted-foreground mt-0.5">
                    Colaborador: {aporte.usuario?.nombre ?? "—"} · Subido: {formatDate(aporte.fecha_subida)}
                  </p>
                </div>
                <Button
                  size="sm"
                  className="flex-shrink-0 bg-violet-700 hover:bg-violet-800 text-white shadow-sm shadow-violet-500/20"
                  asChild
                >
                  <Link href={`/dashboard/revisar/${aporte.id}`}>
                    <Eye className="h-4 w-4" />
                    Revisar
                  </Link>
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
