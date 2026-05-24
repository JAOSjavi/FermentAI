"use client";
import { useState } from "react";
import { Loader2, Mail, Lock, CheckCircle2, XCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card } from "@/components/ui/card";
import { PasswordInput } from "@/components/ui/password-input";
import { PasswordStrength } from "@/components/ui/password-strength";
import { useCambiarEmail, useCambiarPassword } from "@/hooks/useAjustes";
import { useAuth } from "@/hooks/useAuth";

function Feedback({ type, message }: { type: "success" | "error"; message: string }) {
  const isSuccess = type === "success";
  return (
    <div
      className={`flex items-start gap-2.5 rounded-lg border px-4 py-3 text-sm ${
        isSuccess
          ? "bg-green-50 border-green-200 text-green-800"
          : "bg-red-50 border-red-200 text-red-700"
      }`}
    >
      {isSuccess ? (
        <CheckCircle2 className="h-4 w-4 mt-0.5 flex-shrink-0 text-green-600" />
      ) : (
        <XCircle className="h-4 w-4 mt-0.5 flex-shrink-0 text-red-500" />
      )}
      <span>{message}</span>
    </div>
  );
}

function CambiarEmailSection() {
  const { user } = useAuth();
  const mutation = useCambiarEmail();
  const [nuevoEmail, setNuevoEmail] = useState("");
  const [passwordActual, setPasswordActual] = useState("");
  const [feedback, setFeedback] = useState<{ type: "success" | "error"; message: string } | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFeedback(null);
    mutation.mutate(
      { nuevo_email: nuevoEmail, password_actual: passwordActual },
      {
        onSuccess: (data) => {
          setFeedback({ type: "success", message: data.message });
          setNuevoEmail("");
          setPasswordActual("");
        },
        onError: (err) => {
          const msg = err?.response?.data?.detail ?? "No se pudo actualizar el email.";
          setFeedback({ type: "error", message: msg });
        },
      }
    );
  };

  return (
    <Card className="p-6 border-slate-200 shadow-sm">
      <div className="flex items-center gap-3 mb-5">
        <div className="h-9 w-9 rounded-xl bg-indigo-50 flex items-center justify-center">
          <Mail className="h-5 w-5 text-indigo-600" />
        </div>
        <div>
          <h2 className="text-base font-semibold text-slate-900">Cambiar correo electrónico</h2>
          {user?.email && (
            <p className="text-xs text-slate-400 mt-0.5">Actual: {user.email}</p>
          )}
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="nuevo-email" className="text-slate-700 font-medium text-sm">Nuevo correo</Label>
          <Input
            id="nuevo-email"
            type="email"
            placeholder="nuevo@email.com"
            value={nuevoEmail}
            onChange={(e) => setNuevoEmail(e.target.value)}
            className="h-10 border-slate-200 focus-visible:ring-indigo-500"
            required
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="pw-email" className="text-slate-700 font-medium text-sm">Contraseña actual</Label>
          <PasswordInput
            id="pw-email"
            placeholder="••••••••"
            value={passwordActual}
            onChange={(e) => setPasswordActual(e.target.value)}
            className="h-10 border-slate-200 focus-visible:ring-indigo-500"
            required
          />
        </div>

        {feedback && <Feedback type={feedback.type} message={feedback.message} />}

        <Button
          type="submit"
          disabled={mutation.isPending}
          className="w-full h-10 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-700 hover:to-violet-700 text-white border-0 shadow-sm font-semibold"
        >
          {mutation.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
          Actualizar correo
        </Button>
      </form>
    </Card>
  );
}

function CambiarPasswordSection() {
  const mutation = useCambiarPassword();
  const [passwordActual, setPasswordActual] = useState("");
  const [passwordNuevo, setPasswordNuevo] = useState("");
  const [passwordConfirm, setPasswordConfirm] = useState("");
  const [feedback, setFeedback] = useState<{ type: "success" | "error"; message: string } | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFeedback(null);

    if (passwordNuevo !== passwordConfirm) {
      setFeedback({ type: "error", message: "Las contraseñas nuevas no coinciden." });
      return;
    }
    if (passwordNuevo.length < 8) {
      setFeedback({ type: "error", message: "La nueva contraseña debe tener al menos 8 caracteres." });
      return;
    }

    mutation.mutate(
      {
        password_actual: passwordActual,
        password_nuevo: passwordNuevo,
        password_nuevo_confirm: passwordConfirm,
      },
      {
        onSuccess: (data) => {
          setFeedback({ type: "success", message: data.message });
          setPasswordActual("");
          setPasswordNuevo("");
          setPasswordConfirm("");
        },
        onError: (err) => {
          const msg = err?.response?.data?.detail ?? "No se pudo actualizar la contraseña.";
          setFeedback({ type: "error", message: msg });
        },
      }
    );
  };

  return (
    <Card className="p-6 border-slate-200 shadow-sm">
      <div className="flex items-center gap-3 mb-5">
        <div className="h-9 w-9 rounded-xl bg-violet-50 flex items-center justify-center">
          <Lock className="h-5 w-5 text-violet-600" />
        </div>
        <div>
          <h2 className="text-base font-semibold text-slate-900">Cambiar contraseña</h2>
          <p className="text-xs text-slate-400 mt-0.5">Mínimo 8 caracteres</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="pw-actual" className="text-slate-700 font-medium text-sm">Contraseña actual</Label>
          <PasswordInput
            id="pw-actual"
            placeholder="••••••••"
            value={passwordActual}
            onChange={(e) => setPasswordActual(e.target.value)}
            className="h-10 border-slate-200 focus-visible:ring-violet-500"
            required
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="pw-nuevo" className="text-slate-700 font-medium text-sm">Nueva contraseña</Label>
          <PasswordInput
            id="pw-nuevo"
            placeholder="Mínimo 8 caracteres"
            value={passwordNuevo}
            onChange={(e) => setPasswordNuevo(e.target.value)}
            className="h-10 border-slate-200 focus-visible:ring-violet-500"
            required
          />
          <PasswordStrength password={passwordNuevo} />
        </div>

        <div className="space-y-2">
          <Label htmlFor="pw-confirm" className="text-slate-700 font-medium text-sm">Confirmar nueva contraseña</Label>
          <PasswordInput
            id="pw-confirm"
            placeholder="Repite la contraseña"
            value={passwordConfirm}
            onChange={(e) => setPasswordConfirm(e.target.value)}
            className="h-10 border-slate-200 focus-visible:ring-violet-500"
            required
          />
        </div>

        {feedback && <Feedback type={feedback.type} message={feedback.message} />}

        <Button
          type="submit"
          disabled={mutation.isPending}
          className="w-full h-10 bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-700 hover:to-indigo-700 text-white border-0 shadow-sm font-semibold"
        >
          {mutation.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
          Actualizar contraseña
        </Button>
      </form>
    </Card>
  );
}

export default function AjustesPage() {
  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Ajustes de cuenta</h1>
        <p className="text-slate-500 text-sm mt-1">Actualiza tu correo o contraseña de acceso.</p>
      </div>

      <CambiarEmailSection />
      <CambiarPasswordSection />
    </div>
  );
}
