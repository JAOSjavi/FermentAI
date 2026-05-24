"use client";
import { useState } from "react";
import Image from "next/image";
import { Search, Filter, ExternalLink, ChevronDown, ChevronUp, Database } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import api from "@/lib/api";
import { DatasetAporte } from "@/types";

export default function DatasetsPage() {
  const [codigo, setCodigo]     = useState("");
  const [busqueda, setBusqueda] = useState({ codigo: "" });
  const [expandidos, setExpandidos] = useState<Set<number>>(new Set());

  const { data: datasets, isLoading } = useQuery<DatasetAporte[]>({
    queryKey: ["fermentaciones", busqueda],
    queryFn: () => {
      const params = new URLSearchParams();
      if (busqueda.codigo) params.set("codigo", busqueda.codigo);
      return api.get(`/api/fermentaciones?${params}`).then((r) => r.data);
    },
  });

  const handleBuscar = () => setBusqueda({ codigo });

  const toggleExpand = (id: number) => {
    setExpandidos((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  return (
    <div className="space-y-6 max-w-5xl">
      <div>
        <h1 className="font-display text-2xl font-bold tracking-tight text-slate-900">Datasets Aprobados</h1>
        <p className="text-sm text-muted-foreground mt-0.5">Consulta todos los datasets científicos disponibles</p>
      </div>

      {/* Filtros */}
      <Card className="border-slate-100">
        <CardContent className="p-4">
          <div className="flex flex-wrap gap-3 items-end">
            <div className="flex-1 min-w-[160px] space-y-1">
              <label className="text-xs font-medium text-muted-foreground">Código fermentación</label>
              <div className="relative">
                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="FERM01..."
                  className="pl-8"
                  value={codigo}
                  onChange={(e) => setCodigo(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleBuscar()}
                />
              </div>
            </div>
            <Button variant="coffee" onClick={handleBuscar}>
              <Filter className="h-4 w-4" />
              Filtrar
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Resultados */}
      {isLoading ? (
        <div className="flex justify-center py-12">
          <div className="h-8 w-8 animate-spin rounded-full border-[3px] border-indigo-200 border-t-indigo-600" />
        </div>
      ) : !datasets?.length ? (
        <Card className="border-slate-100">
          <CardContent className="flex flex-col items-center py-16 gap-4">
            <Database className="h-12 w-12 text-slate-300" />
            <p className="text-muted-foreground">No se encontraron datasets con esos filtros.</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {datasets.map((dataset) => {
            const expanded      = expandidos.has(dataset.id);
            const imagenesMuestra = expanded ? dataset.imagenes : dataset.imagenes.slice(0, 6);
            return (
              <Card key={dataset.id} className="overflow-hidden border-slate-100">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="text-lg font-mono-code text-indigo-700">
                        {dataset.fermentacion.codigo}
                      </CardTitle>
                      {dataset.fermentacion.descripcion && (
                        <p className="text-sm text-muted-foreground">{dataset.fermentacion.descripcion}</p>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant="secondary">{dataset.total_imagenes} imágenes</Badge>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 mb-3">
                    {imagenesMuestra.map((img) => (
                      <div key={img.nombre} className="group relative rounded-lg overflow-hidden border bg-muted aspect-square">
                        {img.url ? (
                          <>
                            <Image
                              src={img.url}
                              alt={img.nombre}
                              fill
                              className="object-cover group-hover:scale-105 transition-transform"
                              unoptimized
                            />
                            <div className="absolute inset-0 bg-black/0 group-hover:bg-black/30 transition-colors" />
                            <a
                              href={img.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="absolute top-1 right-1 opacity-0 group-hover:opacity-100 transition-opacity rounded bg-black/60 p-0.5"
                            >
                              <ExternalLink className="h-3 w-3 text-white" />
                            </a>
                          </>
                        ) : (
                          <div className="flex items-center justify-center h-full text-xs text-muted-foreground p-2 text-center">
                            {img.nombre}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>

                  {dataset.total_imagenes > 6 && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => toggleExpand(dataset.id)}
                      className="text-indigo-600 hover:text-indigo-700 hover:bg-indigo-50"
                    >
                      {expanded ? (
                        <><ChevronUp className="h-4 w-4" /> Mostrar menos</>
                      ) : (
                        <><ChevronDown className="h-4 w-4" /> Ver {dataset.total_imagenes - 6} imágenes más</>
                      )}
                    </Button>
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
