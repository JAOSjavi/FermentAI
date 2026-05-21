"use client";
import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, FileArchive, X, CheckCircle2, AlertCircle, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useSubirAporte } from "@/hooks/useAportes";
import { cn } from "@/lib/utils";

interface Props {
  onSuccess: (aporteId: number) => void;
}

export function SubirZipForm({ onSuccess }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [errors, setErrors] = useState<string[]>([]);
  const { mutate: subir, isPending } = useSubirAporte();

  const onDrop = useCallback((accepted: File[]) => {
    setErrors([]);
    if (accepted[0]) setFile(accepted[0]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/zip": [".zip"] },
    maxFiles: 1,
    maxSize: 2 * 1024 * 1024 * 1024,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;
    setErrors([]);
    subir(file, {
      onSuccess: (aporte) => onSuccess(aporte.id),
      onError: (err: unknown) => {
        const detail = (err as { response?: { data?: { detail?: { errores?: string[] } | string } } })
          ?.response?.data?.detail;
        if (typeof detail === "object" && detail?.errores) {
          setErrors(detail.errores);
        } else {
          setErrors([typeof detail === "string" ? detail : "Error al subir el archivo"]);
        }
      },
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div
        {...getRootProps()}
        className={cn(
          "border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-colors",
          isDragActive
            ? "border-coffee-500 bg-coffee-50"
            : file
              ? "border-emerald-400 bg-emerald-50"
              : "border-muted-foreground/30 hover:border-coffee-400 hover:bg-coffee-50/50"
        )}
      >
        <input {...getInputProps()} />
        {file ? (
          <div className="flex flex-col items-center gap-2">
            <CheckCircle2 className="h-12 w-12 text-emerald-500" />
            <p className="font-medium text-emerald-700">{file.name}</p>
            <p className="text-sm text-muted-foreground">
              {(file.size / 1024 / 1024).toFixed(2)} MB
            </p>
            <button
              type="button"
              onClick={(e) => { e.stopPropagation(); setFile(null); }}
              className="mt-1 flex items-center gap-1 text-xs text-red-500 hover:underline"
            >
              <X className="h-3 w-3" /> Quitar archivo
            </button>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-3">
            {isDragActive ? (
              <FileArchive className="h-12 w-12 text-coffee-500 animate-bounce" />
            ) : (
              <Upload className="h-12 w-12 text-muted-foreground" />
            )}
            <div>
              <p className="font-medium">
                {isDragActive ? "Suelta el archivo aquí" : "Arrastra tu ZIP o haz clic para seleccionar"}
              </p>
              <p className="text-sm text-muted-foreground mt-1">
                Estructura: FERM##/imagenes/*.jpg + FERM##/FERM##_metadata.csv · Máx 2 GB
              </p>
            </div>
          </div>
        )}
      </div>

      {errors.length > 0 && (
        <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4 space-y-1">
          <div className="flex items-center gap-2 text-destructive font-medium text-sm">
            <AlertCircle className="h-4 w-4" />
            {errors.length} error{errors.length > 1 ? "es" : ""} de validación
          </div>
          <ul className="list-disc list-inside text-sm text-destructive space-y-0.5 ml-1">
            {errors.map((e, i) => <li key={i}>{e}</li>)}
          </ul>
        </div>
      )}

      <Button
        type="submit"
        variant="coffee"
        className="w-full"
        disabled={!file || isPending}
      >
        {isPending ? (
          <>
            <Loader2 className="h-4 w-4 animate-spin" />
            Procesando y validando...
          </>
        ) : (
          <>
            <Upload className="h-4 w-4" />
            Subir Dataset
          </>
        )}
      </Button>
    </form>
  );
}
