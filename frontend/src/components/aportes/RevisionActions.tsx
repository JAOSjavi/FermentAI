"use client";
import { useState } from "react";
import { CheckCircle, XCircle, AlertCircle, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter,
} from "@/components/ui/dialog";
import { useAprobar, useRechazar, useSolicitarCorrecciones } from "@/hooks/useAportes";

interface Props {
  aporteId: number;
  onDone: () => void;
}

type Accion = "rechazar" | "correcciones";

export function RevisionActions({ aporteId, onDone }: Props) {
  const [dialogo, setDialogo] = useState<Accion | null>(null);
  const [observaciones, setObservaciones] = useState("");

  const { mutate: aprobar, isPending: aprobando } = useAprobar();
  const { mutate: rechazar, isPending: rechazando } = useRechazar();
  const { mutate: solicitarCorrecciones, isPending: solicitando } = useSolicitarCorrecciones();

  const handleAprobar = () => {
    aprobar(aporteId, { onSuccess: onDone });
  };

  const handleConfirmarDialogo = () => {
    if (!observaciones.trim()) return;
    if (dialogo === "rechazar") {
      rechazar({ id: aporteId, observaciones }, { onSuccess: () => { setDialogo(null); onDone(); } });
    } else {
      solicitarCorrecciones({ id: aporteId, observaciones }, { onSuccess: () => { setDialogo(null); onDone(); } });
    }
  };

  const isLoading = aprobando || rechazando || solicitando;

  return (
    <>
      <div className="flex flex-wrap gap-3">
        <Button
          variant="default"
          className="bg-emerald-600 hover:bg-emerald-700 text-white"
          onClick={handleAprobar}
          disabled={isLoading}
        >
          {aprobando ? <Loader2 className="h-4 w-4 animate-spin" /> : <CheckCircle className="h-4 w-4" />}
          Aprobar
        </Button>
        <Button
          variant="outline"
          className="border-amber-400 text-amber-700 hover:bg-amber-50"
          onClick={() => { setObservaciones(""); setDialogo("correcciones"); }}
          disabled={isLoading}
        >
          <AlertCircle className="h-4 w-4" />
          Solicitar Correcciones
        </Button>
        <Button
          variant="destructive"
          onClick={() => { setObservaciones(""); setDialogo("rechazar"); }}
          disabled={isLoading}
        >
          <XCircle className="h-4 w-4" />
          Rechazar
        </Button>
      </div>

      <Dialog open={!!dialogo} onOpenChange={(o) => !o && setDialogo(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {dialogo === "rechazar" ? "Rechazar Aporte" : "Solicitar Correcciones"}
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-3 py-2">
            <Label htmlFor="obs">Observaciones (requeridas)</Label>
            <Textarea
              id="obs"
              placeholder="Describe el motivo o las correcciones necesarias..."
              rows={4}
              value={observaciones}
              onChange={(e) => setObservaciones(e.target.value)}
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogo(null)}>Cancelar</Button>
            <Button
              variant={dialogo === "rechazar" ? "destructive" : "default"}
              className={dialogo === "correcciones" ? "bg-amber-600 hover:bg-amber-700" : ""}
              disabled={!observaciones.trim() || isLoading}
              onClick={handleConfirmarDialogo}
            >
              {isLoading && <Loader2 className="h-4 w-4 animate-spin" />}
              Confirmar
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
