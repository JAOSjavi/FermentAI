"use client";
import Link from "next/link";
import { Upload, Eye } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { EstadoBadge } from "@/components/aportes/EstadoBadge";
import { useMisAportes } from "@/hooks/useAportes";
import { formatDate } from "@/lib/utils";

export default function MisAportesPage() {
  const { data: aportes, isLoading } = useMisAportes();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Mis Aportes</h1>
          <p className="text-muted-foreground">Todos tus datasets subidos</p>
        </div>
        <Button variant="coffee" asChild>
          <Link href="/dashboard/mis-aportes/subir">
            <Upload className="h-4 w-4" />
            Subir Dataset
          </Link>
        </Button>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-12">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-coffee-600 border-t-transparent" />
        </div>
      ) : !aportes?.length ? (
        <Card>
          <CardContent className="flex flex-col items-center py-16 gap-4">
            <Upload className="h-12 w-12 text-muted-foreground" />
            <p className="text-muted-foreground">Aún no has subido ningún aporte.</p>
            <Button variant="coffee" asChild>
              <Link href="/dashboard/mis-aportes/subir">Subir tu primer dataset</Link>
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {aportes.map((aporte) => (
            <Card key={aporte.id} className="hover:shadow-md transition-shadow">
              <CardContent className="p-5 flex items-center gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-coffee-700">
                      {aporte.fermentacion?.codigo ?? `Aporte #${aporte.id}`}
                    </span>
                    <EstadoBadge estado={aporte.estado} />
                  </div>
                  <p className="text-sm text-muted-foreground mt-0.5">
                    Subido: {formatDate(aporte.fecha_subida)}
                    {aporte.fecha_revision && ` · Revisado: ${formatDate(aporte.fecha_revision)}`}
                  </p>
                  {aporte.observaciones && (
                    <p className="text-sm text-coffee-700 bg-coffee-50 rounded px-2 py-1 mt-2">
                      {aporte.observaciones}
                    </p>
                  )}
                </div>
                <Button variant="outline" size="sm" asChild>
                  <Link href={`/dashboard/mis-aportes/${aporte.id}`}>
                    <Eye className="h-4 w-4" />
                    Ver
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
