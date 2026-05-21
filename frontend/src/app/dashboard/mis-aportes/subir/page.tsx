"use client";
import { useRouter } from "next/navigation";
import { ArrowLeft, Info } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { SubirZipForm } from "@/components/aportes/SubirZipForm";

export default function SubirPage() {
  const router = useRouter();

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="icon" asChild>
          <Link href="/dashboard/mis-aportes"><ArrowLeft className="h-4 w-4" /></Link>
        </Button>
        <div>
          <h1 className="text-2xl font-bold">Subir Dataset</h1>
          <p className="text-muted-foreground">Carga un ZIP con imágenes y metadatos HPLC</p>
        </div>
      </div>

      <Card className="border-coffee-200 bg-coffee-50/50">
        <CardContent className="p-4">
          <div className="flex gap-2">
            <Info className="h-5 w-5 text-coffee-600 flex-shrink-0 mt-0.5" />
            <div className="text-sm text-coffee-800 space-y-1">
              <p className="font-semibold">Estructura requerida del ZIP:</p>
              <code className="block bg-coffee-100 rounded px-2 py-1 text-xs font-mono">
                FERM01/<br />
                ├── imagenes/<br />
                │   ├── FERM01_20240101_120000.jpg<br />
                │   └── ...<br />
                └── FERM01_metadata.csv
              </code>
              <p className="mt-2">
                El CSV debe incluir las 18 columnas requeridas. Imágenes máx 20 MB c/u. ZIP máx 2 GB.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Seleccionar Archivo</CardTitle>
          <CardDescription>
            Tu aporte será revisado por un investigador antes de ser publicado.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <SubirZipForm onSuccess={(id) => router.push(`/dashboard/mis-aportes/${id}`)} />
        </CardContent>
      </Card>
    </div>
  );
}
