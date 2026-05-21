"use client";
import Link from "next/link";
import Image from "next/image";
import {
  ArrowLeft, ExternalLink, Calendar, FlaskConical,
  MessageSquare, ImageIcon, ChevronDown, ChevronUp, Clock,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { EstadoBadge } from "@/components/aportes/EstadoBadge";
import { useAporteDetalle } from "@/hooks/useAportes";
import { formatDate } from "@/lib/utils";
import { useState } from "react";
import { MetadatoImagen } from "@/types";

export default function AportePage({ params }: { params: { id: string } }) {
  const { id } = params;
  const { data: aporte, isLoading } = useAporteDetalle(Number(id));
  const [imagenSeleccionada, setImagenSeleccionada] = useState<MetadatoImagen | null>(null);
  const [mostrarTodas, setMostrarTodas] = useState(false);

  if (isLoading) return (
    <div className="flex justify-center py-24">
      <div className="h-8 w-8 animate-spin rounded-full border-4 border-coffee-600 border-t-transparent" />
    </div>
  );
  if (!aporte) return <p className="text-muted-foreground">Aporte no encontrado.</p>;

  const imagenes = aporte.metadatos ?? [];
  const imagenesMostradas = mostrarTodas ? imagenes : imagenes.slice(0, 9);

  const estadoColor: Record<string, string> = {
    aprobado: "border-l-emerald-500",
    rechazado: "border-l-red-500",
    correcciones_solicitadas: "border-l-amber-500",
    pendiente_revision: "border-l-blue-400",
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="icon" asChild>
          <Link href="/dashboard/mis-aportes"><ArrowLeft className="h-4 w-4" /></Link>
        </Button>
        <div className="flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <h1 className="text-2xl font-bold">{aporte.fermentacion?.codigo ?? `Aporte #${aporte.id}`}</h1>
            <EstadoBadge estado={aporte.estado} />
          </div>
          <p className="text-sm text-muted-foreground">Detalle de tu dataset</p>
        </div>
      </div>

      {/* Resumen del aporte */}
      <Card className="border-coffee-100">
        <CardContent className="p-5 grid sm:grid-cols-3 gap-4">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-full bg-coffee-50 flex items-center justify-center">
              <FlaskConical className="h-5 w-5 text-coffee-600" />
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Fermentación</p>
              <p className="font-semibold">{aporte.fermentacion?.codigo ?? "—"}</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-full bg-coffee-50 flex items-center justify-center">
              <ImageIcon className="h-5 w-5 text-coffee-600" />
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Imágenes</p>
              <p className="font-semibold">{imagenes.length}</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-full bg-coffee-50 flex items-center justify-center">
              <Calendar className="h-5 w-5 text-coffee-600" />
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Subido</p>
              <p className="font-semibold text-sm">{formatDate(aporte.fecha_subida)}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Comentarios del investigador */}
      {aporte.observaciones ? (
        <Card className={`border-l-4 ${estadoColor[aporte.estado] ?? "border-l-gray-300"}`}>
          <CardHeader className="pb-2">
            <div className="flex items-center gap-2">
              <MessageSquare className="h-4 w-4 text-coffee-600" />
              <CardTitle className="text-base">Comentarios del Investigador</CardTitle>
            </div>
            {aporte.fecha_revision && (
              <CardDescription className="flex items-center gap-1">
                <Clock className="h-3 w-3" />
                {formatDate(aporte.fecha_revision)}
              </CardDescription>
            )}
          </CardHeader>
          <CardContent>
            <div className="rounded-lg bg-muted/50 px-4 py-3">
              <p className="text-sm whitespace-pre-wrap">{aporte.observaciones}</p>
            </div>
            {aporte.estado === "correcciones_solicitadas" && (
              <div className="mt-3 rounded-lg bg-coffee-50 border border-coffee-200 px-4 py-3">
                <p className="text-sm font-medium text-coffee-800">Acción requerida</p>
                <p className="text-sm text-coffee-700 mt-1">
                  El investigador solicitó correcciones. Revisa los comentarios, corrige tu dataset y vuelve a subirlo.
                </p>
                <Button variant="coffee" size="sm" className="mt-3" asChild>
                  <Link href="/dashboard/mis-aportes/subir">Subir versión corregida</Link>
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      ) : aporte.estado === "pendiente_revision" ? (
        <Card className="border-l-4 border-l-coffee-400 bg-coffee-50/40">
          <CardContent className="p-4 flex items-center gap-3">
            <div className="h-8 w-8 rounded-full bg-coffee-100 flex items-center justify-center flex-shrink-0">
              <Clock className="h-4 w-4 text-coffee-600 animate-pulse" />
            </div>
            <div>
              <p className="text-sm font-medium text-coffee-800">En revisión</p>
              <p className="text-sm text-coffee-600">Tu dataset está siendo revisado por un investigador. Te notificaremos cuando haya una respuesta.</p>
            </div>
          </CardContent>
        </Card>
      ) : null}

      {/* Galería de imágenes */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <ImageIcon className="h-4 w-4 text-coffee-600" />
            Imágenes del Dataset
          </CardTitle>
          <CardDescription>Haz clic en una imagen para ver sus datos HPLC</CardDescription>
        </CardHeader>
        <CardContent>
          {!imagenes.length ? (
            <p className="text-sm text-muted-foreground">No hay imágenes registradas.</p>
          ) : (
            <>
              <div className="grid grid-cols-3 sm:grid-cols-4 lg:grid-cols-6 gap-2 mb-3">
                {imagenesMostradas.map((meta) => (
                  <button
                    key={meta.id}
                    onClick={() => setImagenSeleccionada(imagenSeleccionada?.id === meta.id ? null : meta)}
                    className={`group relative rounded-lg overflow-hidden border aspect-square transition-all ${
                      imagenSeleccionada?.id === meta.id
                        ? "ring-2 ring-coffee-500 border-coffee-400"
                        : "hover:border-coffee-300"
                    }`}
                  >
                    {meta.url_imagen ? (
                      <Image src={meta.url_imagen} alt={meta.imagen} fill className="object-cover" unoptimized />
                    ) : (
                      <div className="h-full bg-muted flex items-center justify-center">
                        <ImageIcon className="h-4 w-4 text-muted-foreground" />
                      </div>
                    )}
                    <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors" />
                    {meta.estado_fermentacion && (
                      <div className="absolute bottom-0 left-0 right-0 bg-black/60 px-1 py-0.5 text-[9px] text-white truncate text-center">
                        {meta.estado_fermentacion.replace(/_/g, " ")}
                      </div>
                    )}
                  </button>
                ))}
              </div>

              {imagenes.length > 9 && (
                <Button variant="ghost" size="sm" onClick={() => setMostrarTodas(!mostrarTodas)} className="text-coffee-600 mb-3">
                  {mostrarTodas
                    ? <><ChevronUp className="h-4 w-4" /> Mostrar menos</>
                    : <><ChevronDown className="h-4 w-4" /> Ver {imagenes.length - 9} imágenes más</>}
                </Button>
              )}

              {/* Detalle de imagen seleccionada */}
              {imagenSeleccionada && (
                <div className="mt-2 rounded-xl border bg-muted/30 p-4 grid sm:grid-cols-2 gap-4">
                  <div className="relative rounded-lg overflow-hidden aspect-video bg-muted">
                    {imagenSeleccionada.url_imagen ? (
                      <>
                        <Image src={imagenSeleccionada.url_imagen} alt={imagenSeleccionada.imagen} fill className="object-contain" unoptimized />
                        <a href={imagenSeleccionada.url_imagen} target="_blank" rel="noopener noreferrer"
                          className="absolute top-2 right-2 rounded bg-black/60 p-1 text-white">
                          <ExternalLink className="h-3 w-3" />
                        </a>
                      </>
                    ) : (
                      <div className="flex h-full items-center justify-center text-sm text-muted-foreground">Sin previsualización</div>
                    )}
                  </div>
                  <div className="space-y-2 text-sm">
                    <p className="font-semibold text-coffee-700 truncate">{imagenSeleccionada.imagen}</p>
                    {imagenSeleccionada.timestamp && (
                      <div className="flex items-center gap-1 text-muted-foreground text-xs">
                        <Clock className="h-3 w-3" />
                        {formatDate(imagenSeleccionada.timestamp)}
                      </div>
                    )}
                    {imagenSeleccionada.estado_fermentacion && (
                      <Badge variant="secondary" className="capitalize text-xs">
                        {imagenSeleccionada.estado_fermentacion.replace(/_/g, " ")}
                      </Badge>
                    )}
                    <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs pt-1 border-t">
                      {[
                        ["Tiempo", imagenSeleccionada.tiempo_horas != null ? `${imagenSeleccionada.tiempo_horas} h` : null],
                        ["Glucosa", imagenSeleccionada.glucosa_g_l != null ? `${imagenSeleccionada.glucosa_g_l} g/L` : null],
                        ["Fructosa", imagenSeleccionada.fructosa_g_l != null ? `${imagenSeleccionada.fructosa_g_l} g/L` : null],
                        ["Etanol", imagenSeleccionada.etanol_g_l != null ? `${imagenSeleccionada.etanol_g_l} g/L` : null],
                        ["Ác. Láctico", imagenSeleccionada.acido_lactico_g_l != null ? `${imagenSeleccionada.acido_lactico_g_l} g/L` : null],
                        ["Ác. Acético", imagenSeleccionada.acido_acetico_g_l != null ? `${imagenSeleccionada.acido_acetico_g_l} g/L` : null],
                        ["Ác. Cítrico", imagenSeleccionada.acido_citrico_g_l != null ? `${imagenSeleccionada.acido_citrico_g_l} g/L` : null],
                        ["Ác. Succínico", imagenSeleccionada.acido_succinico_g_l != null ? `${imagenSeleccionada.acido_succinico_g_l} g/L` : null],
                      ].filter(([, v]) => v !== null).map(([label, value]) => (
                        <div key={label as string}>
                          <span className="text-muted-foreground">{label}: </span>
                          <span className="font-medium">{value}</span>
                        </div>
                      ))}
                    </div>
                    {imagenSeleccionada.observaciones && (
                      <p className="text-xs text-coffee-700 bg-coffee-50 rounded px-2 py-1">
                        {imagenSeleccionada.observaciones}
                      </p>
                    )}
                  </div>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
