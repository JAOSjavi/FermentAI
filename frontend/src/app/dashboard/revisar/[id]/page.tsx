"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import Image from "next/image";
import {
  ArrowLeft, User, Calendar, FlaskConical, ImageIcon,
  CheckCircle, XCircle, AlertCircle, Loader2, ExternalLink,
  ChevronDown, ChevronUp, Clock,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { EstadoBadge } from "@/components/aportes/EstadoBadge";
import { useAporteDetalle, useAprobar, useRechazar, useSolicitarCorrecciones } from "@/hooks/useAportes";
import { formatDate } from "@/lib/utils";
import { MetadatoImagen } from "@/types";

export default function RevisarDetallePage({ params }: { params: { id: string } }) {
  const { id }    = params;
  const router    = useRouter();
  const { data: aporte, isLoading, refetch } = useAporteDetalle(Number(id), true);

  const [observaciones, setObservaciones] = useState("");
  const [imagenSeleccionada, setImagenSeleccionada] = useState<MetadatoImagen | null>(null);
  const [mostrarTodasImagenes, setMostrarTodasImagenes] = useState(false);

  const { mutate: aprobar,   isPending: aprobando  } = useAprobar();
  const { mutate: rechazar,  isPending: rechazando } = useRechazar();
  const { mutate: solicitar, isPending: solicitando } = useSolicitarCorrecciones();

  const isPending  = aprobando || rechazando || solicitando;

  const handleAprobar = () => {
    aprobar(Number(id), {
      onSuccess: () => { refetch(); router.push("/dashboard/revisar"); },
    });
  };

  const handleRechazar = () => {
    if (!observaciones.trim()) return;
    rechazar({ id: Number(id), observaciones }, {
      onSuccess: () => { refetch(); router.push("/dashboard/revisar"); },
    });
  };

  const handleSolicitar = () => {
    if (!observaciones.trim()) return;
    solicitar({ id: Number(id), observaciones }, {
      onSuccess: () => { refetch(); },
    });
  };

  if (isLoading) return (
    <div className="flex justify-center py-24">
      <div className="h-8 w-8 animate-spin rounded-full border-[3px] border-violet-200 border-t-violet-600" />
    </div>
  );

  if (!aporte) return <p className="text-muted-foreground">Aporte no encontrado.</p>;

  const revisable         = aporte.estado === "pendiente_revision" || aporte.estado === "correcciones_solicitadas";
  const imagenes          = aporte.metadatos ?? [];
  const imagenesMostradas = mostrarTodasImagenes ? imagenes : imagenes.slice(0, 9);

  return (
    <div className="space-y-6 max-w-5xl">

      {/* Header */}
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="icon" asChild>
          <Link href="/dashboard/revisar"><ArrowLeft className="h-4 w-4" /></Link>
        </Button>
        <div className="flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <h1 className="font-display text-2xl font-bold tracking-tight text-slate-900">
              {aporte.fermentacion?.codigo ?? `Aporte #${aporte.id}`}
            </h1>
            <EstadoBadge estado={aporte.estado} />
          </div>
          <p className="text-sm text-muted-foreground mt-0.5">Revisión de aporte científico</p>
        </div>
      </div>

      {/* Info del colaborador */}
      <Card className="border-violet-200 bg-violet-50/40">
        <CardContent className="p-5 grid sm:grid-cols-3 gap-4">
          {[
            { icon: User,        label: "Colaborador",    val: aporte.usuario?.nombre ?? "—",           sub: aporte.usuario?.email },
            { icon: Calendar,    label: "Fecha de subida", val: formatDate(aporte.fecha_subida)         },
            { icon: FlaskConical,label: "Fermentación",   val: aporte.fermentacion?.codigo ?? "—",      sub: `${imagenes.length} imágenes` },
          ].map(({ icon: Icon, label, val, sub }) => (
            <div key={label} className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-full bg-violet-100 flex items-center justify-center flex-shrink-0">
                <Icon className="h-5 w-5 text-violet-700" />
              </div>
              <div>
                <p className="text-xs text-muted-foreground">{label}</p>
                <p className="font-semibold text-sm">{val}</p>
                {sub && <p className="text-xs text-muted-foreground">{sub}</p>}
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Galería de imágenes */}
      <Card className="border-slate-100">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="font-display text-base flex items-center gap-2">
                <ImageIcon className="h-4 w-4 text-violet-600" />
                Galería de Imágenes
              </CardTitle>
              <CardDescription>{imagenes.length} imágenes · haz clic para ver detalles</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {!imagenes.length ? (
            <p className="text-sm text-muted-foreground">Sin imágenes registradas.</p>
          ) : (
            <>
              <div className="grid grid-cols-3 sm:grid-cols-4 lg:grid-cols-6 gap-2 mb-3">
                {imagenesMostradas.map((meta) => (
                  <button
                    key={meta.id}
                    onClick={() => setImagenSeleccionada(imagenSeleccionada?.id === meta.id ? null : meta)}
                    className={`group relative rounded-lg overflow-hidden border aspect-square transition-all ${
                      imagenSeleccionada?.id === meta.id
                        ? "ring-2 ring-violet-500 border-violet-400"
                        : "hover:border-violet-300"
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
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setMostrarTodasImagenes(!mostrarTodasImagenes)}
                  className="text-violet-600 hover:text-violet-700 hover:bg-violet-50"
                >
                  {mostrarTodasImagenes
                    ? <><ChevronUp className="h-4 w-4" /> Mostrar menos</>
                    : <><ChevronDown className="h-4 w-4" /> Ver {imagenes.length - 9} imágenes más</>}
                </Button>
              )}

              {imagenSeleccionada && (
                <div className="mt-4 rounded-xl border bg-muted/30 p-4 grid sm:grid-cols-2 gap-4">
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
                    <p className="font-semibold font-mono-code text-violet-700 truncate text-xs">
                      {imagenSeleccionada.imagen}
                    </p>
                    {imagenSeleccionada.timestamp && (
                      <div className="flex items-center gap-1 text-muted-foreground">
                        <Clock className="h-3 w-3" />
                        <span>{formatDate(imagenSeleccionada.timestamp)}</span>
                      </div>
                    )}
                    {imagenSeleccionada.estado_fermentacion && (
                      <Badge variant="secondary" className="capitalize">
                        {imagenSeleccionada.estado_fermentacion.replace(/_/g, " ")}
                      </Badge>
                    )}
                    <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs pt-1 border-t">
                      {[
                        ["Tiempo",       imagenSeleccionada.tiempo_horas != null       ? `${imagenSeleccionada.tiempo_horas} h`        : null],
                        ["Glucosa",      imagenSeleccionada.glucosa_g_l != null        ? `${imagenSeleccionada.glucosa_g_l} g/L`       : null],
                        ["Fructosa",     imagenSeleccionada.fructosa_g_l != null       ? `${imagenSeleccionada.fructosa_g_l} g/L`      : null],
                        ["Etanol",       imagenSeleccionada.etanol_g_l != null         ? `${imagenSeleccionada.etanol_g_l} g/L`        : null],
                        ["Ác. Láctico",  imagenSeleccionada.acido_lactico_g_l != null  ? `${imagenSeleccionada.acido_lactico_g_l} g/L` : null],
                        ["Ác. Acético",  imagenSeleccionada.acido_acetico_g_l != null  ? `${imagenSeleccionada.acido_acetico_g_l} g/L` : null],
                        ["Ác. Cítrico",  imagenSeleccionada.acido_citrico_g_l != null  ? `${imagenSeleccionada.acido_citrico_g_l} g/L` : null],
                        ["Ác. Succínico",imagenSeleccionada.acido_succinico_g_l != null? `${imagenSeleccionada.acido_succinico_g_l} g/L`: null],
                      ].filter(([, v]) => v !== null).map(([label, value]) => (
                        <div key={label as string}>
                          <span className="text-muted-foreground">{label}: </span>
                          <span className="font-medium">{value}</span>
                        </div>
                      ))}
                    </div>
                    {imagenSeleccionada.observaciones && (
                      <p className="text-xs text-violet-700 bg-violet-50 rounded px-2 py-1 mt-1">
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

      {/* Panel de decisión */}
      {revisable ? (
        <Card className="border-2 border-violet-200">
          <CardHeader className="pb-3">
            <CardTitle className="font-display text-base">Decisión de Revisión</CardTitle>
            <CardDescription>
              Revisa el dataset completo antes de tomar una decisión. Los comentarios son obligatorios para rechazar o solicitar correcciones.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="observaciones">Comentarios / Observaciones</Label>
              <Textarea
                id="observaciones"
                placeholder="Escribe aquí tus comentarios sobre el dataset, criterios de calidad, correcciones necesarias o justificación de la decisión..."
                rows={4}
                value={observaciones}
                onChange={(e) => setObservaciones(e.target.value)}
                className="resize-none"
              />
              <p className="text-xs text-muted-foreground">
                Requerido para rechazar o solicitar correcciones. Recomendado para aprobar.
              </p>
            </div>

            <div className="flex flex-wrap gap-3 pt-1">
              <Button
                variant="success"
                className="flex-1 sm:flex-none"
                onClick={handleAprobar}
                disabled={isPending}
              >
                {aprobando ? <Loader2 className="h-4 w-4 animate-spin" /> : <CheckCircle className="h-4 w-4" />}
                Aprobar Dataset
              </Button>
              <Button
                variant="outline"
                className="border-amber-400 text-amber-700 hover:bg-amber-50 flex-1 sm:flex-none"
                onClick={handleSolicitar}
                disabled={isPending || !observaciones.trim()}
                title={!observaciones.trim() ? "Escribe un comentario primero" : ""}
              >
                {solicitando ? <Loader2 className="h-4 w-4 animate-spin" /> : <AlertCircle className="h-4 w-4" />}
                Solicitar Correcciones
              </Button>
              <Button
                variant="destructive"
                className="flex-1 sm:flex-none"
                onClick={handleRechazar}
                disabled={isPending || !observaciones.trim()}
                title={!observaciones.trim() ? "Escribe un comentario primero" : ""}
              >
                {rechazando ? <Loader2 className="h-4 w-4 animate-spin" /> : <XCircle className="h-4 w-4" />}
                Rechazar
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        aporte.observaciones && (
          <Card className="border-l-4 border-l-violet-400">
            <CardHeader className="pb-2">
              <CardTitle className="font-display text-base">Comentarios del Investigador</CardTitle>
              {aporte.fecha_revision && (
                <CardDescription>{formatDate(aporte.fecha_revision)}</CardDescription>
              )}
            </CardHeader>
            <CardContent>
              <p className="text-sm">{aporte.observaciones}</p>
            </CardContent>
          </Card>
        )
      )}
    </div>
  );
}
