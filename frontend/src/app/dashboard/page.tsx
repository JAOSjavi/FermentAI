"use client";
import Link from "next/link";
import { Upload, FolderOpen, CheckSquare, Database, TrendingUp, Clock } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/useAuth";
import { useMisAportes, usePendientes } from "@/hooks/useAportes";
import { EstadoBadge } from "@/components/aportes/EstadoBadge";
import { formatDate } from "@/lib/utils";

export default function DashboardPage() {
  const { user } = useAuth();
  const { data: misAportes } = useMisAportes();
  const { data: pendientes } = usePendientes();

  const isInvestigador = user?.rol === "investigador";
  const pendientesCount = pendientes?.length ?? 0;
  const aprobados = misAportes?.filter((a) => a.estado === "aprobado").length ?? 0;
  const totalAportes = misAportes?.length ?? 0;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-foreground">
          Bienvenido, {user?.nombre?.split(" ")[0]}
        </h1>
        <p className="text-muted-foreground mt-1">Panel de control · FermentAI</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          icon={FolderOpen}
          label="Mis Aportes"
          value={totalAportes}
          gradient="from-violet-500 to-violet-600"
          glow="shadow-violet-500/30"
        />
        <StatCard
          icon={TrendingUp}
          label="Aprobados"
          value={aprobados}
          gradient="from-emerald-500 to-emerald-600"
          glow="shadow-emerald-500/30"
        />
        {isInvestigador && (
          <StatCard
            icon={Clock}
            label="Pendientes de Revisión"
            value={pendientesCount}
            gradient="from-amber-500 to-amber-600"
            glow="shadow-amber-500/30"
          />
        )}
        <StatCard
          icon={Database}
          label="Datasets Disponibles"
          value="—"
          gradient="from-coffee-500 to-coffee-700"
          glow="shadow-coffee-500/30"
        />
      </div>

      {/* Quick Actions + Recent */}
      <div className="grid md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Acciones Rápidas</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col gap-3">
            <Button variant="coffee" className="w-full justify-start" asChild>
              <Link href="/dashboard/mis-aportes/subir">
                <Upload className="h-4 w-4" />
                Subir Nuevo Dataset
              </Link>
            </Button>
            <Button
              variant="outline"
              className="w-full justify-start hover:border-coffee-200 hover:bg-coffee-50 hover:text-coffee-700"
              asChild
            >
              <Link href="/dashboard/datasets">
                <Database className="h-4 w-4" />
                Explorar Datasets
              </Link>
            </Button>
            {isInvestigador && (
              <Button
                variant="outline"
                className="w-full justify-start hover:border-coffee-200 hover:bg-coffee-50 hover:text-coffee-700"
                asChild
              >
                <Link href="/dashboard/revisar">
                  <CheckSquare className="h-4 w-4" />
                  Revisar Aportes Pendientes
                  {pendientesCount > 0 && (
                    <span className="ml-auto rounded-full bg-coffee-100 px-2 py-0.5 text-xs font-bold text-coffee-700">
                      {pendientesCount}
                    </span>
                  )}
                </Link>
              </Button>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Últimos Aportes</CardTitle>
            <CardDescription>Tus 5 aportes más recientes</CardDescription>
          </CardHeader>
          <CardContent>
            {!misAportes?.length ? (
              <p className="text-sm text-muted-foreground">Aún no has subido ningún aporte.</p>
            ) : (
              <ul className="space-y-2.5">
                {misAportes.slice(0, 5).map((a) => (
                  <li key={a.id} className="flex items-center justify-between text-sm py-0.5">
                    <Link
                      href={`/dashboard/mis-aportes/${a.id}`}
                      className="text-violet-700 hover:underline font-medium"
                    >
                      {a.fermentacion?.codigo ?? `Aporte #${a.id}`}
                    </Link>
                    <div className="flex items-center gap-2">
                      <span className="text-muted-foreground text-xs">{formatDate(a.fecha_subida)}</span>
                      <EstadoBadge estado={a.estado} />
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function StatCard({
  icon: Icon,
  label,
  value,
  gradient,
  glow,
}: {
  icon: React.ElementType;
  label: string;
  value: string | number;
  gradient: string;
  glow: string;
}) {
  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardContent className="p-6 flex items-center gap-4">
        <div className={`rounded-xl p-3 bg-gradient-to-br ${gradient} shadow-lg ${glow} flex-shrink-0`}>
          <Icon className="h-6 w-6 text-white" />
        </div>
        <div>
          <p className="text-2xl font-bold text-foreground">{value}</p>
          <p className="text-sm text-muted-foreground">{label}</p>
        </div>
      </CardContent>
    </Card>
  );
}
