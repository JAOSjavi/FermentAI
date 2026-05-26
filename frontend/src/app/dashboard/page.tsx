"use client";
import Link from "next/link";
import {
  Upload,
  FolderOpen,
  CheckSquare,
  Database,
  TrendingUp,
  Clock,
  ArrowRight,
} from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/useAuth";
import { useMisAportes, usePendientes } from "@/hooks/useAportes";
import { EstadoBadge } from "@/components/aportes/EstadoBadge";
import { formatDate } from "@/lib/utils";
import { cn } from "@/lib/utils";

/* Role-specific color tokens for stat cards and quick actions */
const roleTokens = {
  colaborador: {
    quickActionPrimary: "bg-indigo-600 hover:bg-indigo-700 text-white shadow-md shadow-indigo-500/30",
    quickActionOutline: "border-indigo-200 hover:bg-indigo-50 hover:text-indigo-700 hover:border-indigo-300",
    badge:              "bg-indigo-100 text-indigo-700",
    link:               "text-indigo-600 hover:text-indigo-800",
  },
  investigador: {
    quickActionPrimary: "bg-violet-700 hover:bg-violet-800 text-white shadow-md shadow-violet-500/30",
    quickActionOutline: "border-violet-200 hover:bg-violet-50 hover:text-violet-700 hover:border-violet-300",
    badge:              "bg-violet-100 text-violet-700",
    link:               "text-violet-600 hover:text-violet-800",
  },
};

export default function DashboardPage() {
  const { user } = useAuth();
  const { data: misAportes } = useMisAportes();
  const isInvestigador   = user?.rol === "investigador";
  const { data: pendientes } = usePendientes(isInvestigador);
  const role             = isInvestigador ? "investigador" : "colaborador";
  const rt               = roleTokens[role];
  const pendientesCount  = pendientes?.length ?? 0;
  const aprobados        = misAportes?.filter((a) => a.estado === "aprobado").length ?? 0;
  const totalAportes     = misAportes?.length ?? 0;

  return (
    <div className="space-y-8 max-w-6xl">

      {/* Page header */}
      <div className="animate-fade-in-up">
        <h1 className="font-display text-2xl font-bold tracking-tight text-slate-900">
          Bienvenido, {user?.nombre?.split(" ")[0]}
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Panel de control · FermentAI
        </p>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          icon={FolderOpen}
          label="Mis Aportes"
          value={totalAportes}
          gradient="from-indigo-500 to-indigo-700"
          glow="shadow-indigo-400/30"
          delay={0}
        />
        <StatCard
          icon={TrendingUp}
          label="Aprobados"
          value={aprobados}
          gradient="from-emerald-500 to-emerald-700"
          glow="shadow-emerald-400/30"
          delay={80}
        />
        {isInvestigador ? (
          <StatCard
            icon={Clock}
            label="Pendientes"
            value={pendientesCount}
            gradient="from-amber-500 to-amber-600"
            glow="shadow-amber-400/30"
            delay={160}
            urgent={pendientesCount > 0}
          />
        ) : (
          <StatCard
            icon={Database}
            label="Datasets Públicos"
            value="—"
            gradient="from-coffee-500 to-coffee-700"
            glow="shadow-coffee-400/30"
            delay={160}
          />
        )}
        <StatCard
          icon={Database}
          label="Datasets Disponibles"
          value="—"
          gradient="from-slate-500 to-slate-700"
          glow="shadow-slate-400/20"
          delay={240}
        />
      </div>

      {/* Quick actions + Recent list */}
      <div className="grid md:grid-cols-2 gap-5">

        {/* Quick actions */}
        <Card className="border-slate-100 shadow-sm animate-fade-in-up" style={{ animationDelay: "200ms" }}>
          <CardHeader className="pb-3">
            <CardTitle className="font-display text-base font-semibold text-slate-800">
              Acciones Rápidas
            </CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col gap-2.5">
            <Button
              className={cn("w-full justify-between font-medium transition-all", rt.quickActionPrimary)}
              asChild
            >
              <Link href="/dashboard/mis-aportes/subir">
                <span className="flex items-center gap-2">
                  <Upload className="h-4 w-4" />
                  Subir Nuevo Dataset
                </span>
                <ArrowRight className="h-4 w-4 opacity-70" />
              </Link>
            </Button>

            <Button
              variant="outline"
              className={cn("w-full justify-between font-medium transition-all", rt.quickActionOutline)}
              asChild
            >
              <Link href="/dashboard/datasets">
                <span className="flex items-center gap-2">
                  <Database className="h-4 w-4" />
                  Explorar Datasets
                </span>
                <ArrowRight className="h-4 w-4 opacity-50" />
              </Link>
            </Button>

            {isInvestigador && (
              <Button
                variant="outline"
                className={cn("w-full justify-between font-medium transition-all", rt.quickActionOutline)}
                asChild
              >
                <Link href="/dashboard/revisar">
                  <span className="flex items-center gap-2">
                    <CheckSquare className="h-4 w-4" />
                    Revisar Aportes Pendientes
                  </span>
                  <span className="flex items-center gap-2">
                    {pendientesCount > 0 && (
                      <span className={cn("rounded-full px-2 py-0.5 text-xs font-bold", rt.badge)}>
                        {pendientesCount}
                      </span>
                    )}
                    <ArrowRight className="h-4 w-4 opacity-50" />
                  </span>
                </Link>
              </Button>
            )}
          </CardContent>
        </Card>

        {/* Recent contributions */}
        <Card className="border-slate-100 shadow-sm animate-fade-in-up" style={{ animationDelay: "280ms" }}>
          <CardHeader className="pb-3">
            <CardTitle className="font-display text-base font-semibold text-slate-800">
              Últimos Aportes
            </CardTitle>
            <CardDescription className="text-xs">
              Tus 5 aportes más recientes
            </CardDescription>
          </CardHeader>
          <CardContent>
            {!misAportes?.length ? (
              <div className="flex flex-col items-center justify-center py-6 text-center">
                <FolderOpen className="h-8 w-8 text-slate-300 mb-2" />
                <p className="text-sm text-slate-400 font-medium">Aún no has subido ningún aporte.</p>
                <p className="text-xs text-slate-400 mt-1">¡Sube tu primer dataset para comenzar!</p>
              </div>
            ) : (
              <ul className="space-y-2">
                {misAportes.slice(0, 5).map((a) => (
                  <li
                    key={a.id}
                    className="flex items-center justify-between text-sm py-1 border-b border-slate-50 last:border-0"
                  >
                    <Link
                      href={`/dashboard/mis-aportes/${a.id}`}
                      className={cn("font-medium font-mono-code text-xs hover:underline underline-offset-2", rt.link)}
                    >
                      {a.fermentacion?.codigo ?? `Aporte #${a.id}`}
                    </Link>
                    <div className="flex items-center gap-2">
                      <span className="text-slate-400 text-xs">{formatDate(a.fecha_subida)}</span>
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

/* ─── Stat Card ───────────────────────────────────────────── */

function StatCard({
  icon: Icon,
  label,
  value,
  gradient,
  glow,
  delay = 0,
  urgent = false,
}: {
  icon: React.ElementType;
  label: string;
  value: string | number;
  gradient: string;
  glow: string;
  delay?: number;
  urgent?: boolean;
}) {
  return (
    <Card
      style={{ animationDelay: `${delay}ms` }}
      className="border-slate-100 shadow-sm hover:shadow-md transition-shadow duration-200 animate-stat-pop"
    >
      <CardContent className="p-5 flex items-center gap-4">
        <div
          className={cn(
            "rounded-xl p-3 bg-gradient-to-br flex-shrink-0 shadow-lg",
            gradient,
            glow,
            urgent && "animate-pulse"
          )}
        >
          <Icon className="h-5 w-5 text-white" />
        </div>
        <div className="min-w-0">
          <p className="font-display text-2xl font-bold text-slate-900 leading-none">
            {value}
          </p>
          <p className="text-xs text-slate-500 mt-1 truncate">{label}</p>
        </div>
      </CardContent>
    </Card>
  );
}
