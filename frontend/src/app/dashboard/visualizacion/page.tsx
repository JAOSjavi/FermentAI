"use client";
import { BarChart3, TrendingUp, Beaker } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const MOCK_COMPUESTOS = [
  { nombre: "Glucosa", valores: [45, 38, 29, 18, 10, 5, 2], color: "bg-blue-400" },
  { nombre: "Fructosa", valores: [22, 18, 14, 10, 6, 3, 1], color: "bg-green-400" },
  { nombre: "Etanol", valores: [0, 4, 9, 16, 22, 28, 31], color: "bg-amber-400" },
  { nombre: "Ácido Láctico", valores: [0, 1, 3, 6, 9, 12, 14], color: "bg-red-400" },
  { nombre: "Ácido Acético", valores: [0, 0.5, 1, 2, 3, 4, 5], color: "bg-purple-400" },
];

const TIEMPOS = [0, 12, 24, 36, 48, 60, 72];

export default function VisualizacionPage() {
  const maxVal = 50;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Visualización de Datos</h1>
        <p className="text-muted-foreground">Exploración de compuestos a lo largo del proceso de fermentación</p>
      </div>

      <div className="rounded-lg border border-coffee-200 bg-coffee-50 px-4 py-3 text-sm text-coffee-800">
        <strong>Datos de ejemplo.</strong> Esta visualización mostrará datos reales de los datasets aprobados.
      </div>

      <div className="grid md:grid-cols-3 gap-4">
        <StatMock icon={Beaker} label="Total Datasets" value="12" sub="Aprobados" />
        <StatMock icon={BarChart3} label="Imágenes Totales" value="1,248" sub="FERM01–FERM12" />
        <StatMock icon={TrendingUp} label="Horas Promedio" value="72 h" sub="Por fermentación" />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Evolución de Compuestos (g/L)</CardTitle>
          <CardDescription>Fermentación FERM01 — datos de ejemplo · 72 horas</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {MOCK_COMPUESTOS.map(({ nombre, valores, color }) => (
              <div key={nombre}>
                <div className="flex items-center justify-between text-xs text-muted-foreground mb-1">
                  <span className="font-medium text-foreground">{nombre}</span>
                  <span>{valores[valores.length - 1]} g/L final</span>
                </div>
                <div className="flex gap-1 items-end h-16">
                  {valores.map((v, i) => (
                    <div key={i} className="flex-1 flex flex-col items-center gap-0.5">
                      <div
                        className={`w-full rounded-t ${color} opacity-80`}
                        style={{ height: `${(v / maxVal) * 60}px` }}
                      />
                      <span className="text-[9px] text-muted-foreground">{TIEMPOS[i]}h</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Estados de Fermentación</CardTitle>
          <CardDescription>Distribución de imágenes por estado</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-4 text-center">
            {[
              { estado: "Semi-fermentado", pct: 35, color: "bg-amber-200 text-amber-800" },
              { estado: "Fermentado", pct: 45, color: "bg-emerald-200 text-emerald-800" },
              { estado: "Sobre-fermentado", pct: 20, color: "bg-red-200 text-red-800" },
            ].map(({ estado, pct, color }) => (
              <div key={estado} className={`rounded-xl p-4 ${color}`}>
                <p className="text-3xl font-bold">{pct}%</p>
                <p className="text-sm font-medium mt-1">{estado}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function StatMock({ icon: Icon, label, value, sub }: { icon: React.ElementType; label: string; value: string; sub: string }) {
  return (
    <Card>
      <CardContent className="p-5 flex items-center gap-3">
        <div className="rounded-lg bg-coffee-50 p-3">
          <Icon className="h-6 w-6 text-coffee-600" />
        </div>
        <div>
          <p className="text-2xl font-bold">{value}</p>
          <p className="text-sm text-muted-foreground">{label}</p>
          <p className="text-xs text-muted-foreground">{sub}</p>
        </div>
      </CardContent>
    </Card>
  );
}
