"use client";
import { useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { FlaskConical, Loader2, CheckCircle2, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import api from "@/lib/api";

function ResetPasswordForm() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const token = searchParams.get("token") ?? "";

  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [done, setDone] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (password !== confirm) {
      setError("Las contraseñas no coinciden");
      return;
    }
    if (password.length < 8) {
      setError("La contraseña debe tener al menos 8 caracteres");
      return;
    }

    setLoading(true);
    try {
      await api.post("/api/auth/reset-password", { token, nueva_password: password });
      setDone(true);
      setTimeout(() => router.push("/login"), 3000);
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(msg || "Token inválido o expirado. Solicita un nuevo enlace.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md">
      <div className="flex items-center gap-2 mb-8 lg:hidden">
        <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center">
          <FlaskConical className="h-4 w-4 text-white" />
        </div>
        <span className="text-xl font-bold text-slate-900">FermentAI</span>
      </div>

      {done ? (
        <div className="text-center">
          <div className="mx-auto mb-5 h-16 w-16 rounded-full bg-green-50 border border-green-200 flex items-center justify-center">
            <CheckCircle2 className="h-8 w-8 text-green-600" />
          </div>
          <h1 className="text-2xl font-bold text-slate-900 mb-2">¡Contraseña actualizada!</h1>
          <p className="text-slate-500 mb-6">Serás redirigido al inicio de sesión en unos segundos.</p>
          <Link
            href="/login"
            className="inline-flex items-center gap-2 text-sm font-semibold text-violet-600 hover:text-violet-700 hover:underline"
          >
            <ArrowLeft className="h-4 w-4" />
            Ir al inicio de sesión
          </Link>
        </div>
      ) : (
        <>
          <h1 className="text-3xl font-bold text-slate-900 mb-1">Nueva contraseña</h1>
          <p className="text-slate-500 mb-8">Elige una contraseña segura para tu cuenta.</p>

          {!token && (
            <div className="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700 mb-5">
              Enlace inválido. Solicita un nuevo enlace de recuperación.
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="space-y-2">
              <Label htmlFor="password" className="text-slate-700 font-medium">Nueva contraseña</Label>
              <Input
                id="password"
                type="password"
                placeholder="Mínimo 8 caracteres"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="h-11 border-slate-200 focus-visible:ring-violet-500"
                required
                disabled={!token}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="confirm" className="text-slate-700 font-medium">Confirmar contraseña</Label>
              <Input
                id="confirm"
                type="password"
                placeholder="Repite la contraseña"
                value={confirm}
                onChange={(e) => setConfirm(e.target.value)}
                className="h-11 border-slate-200 focus-visible:ring-violet-500"
                required
                disabled={!token}
              />
            </div>

            {error && (
              <div className="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">
                {error}
              </div>
            )}

            <Button
              type="submit"
              disabled={loading || !token}
              className="w-full h-11 bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-700 hover:to-indigo-700 text-white border-0 shadow-lg shadow-violet-500/30 font-semibold text-base"
            >
              {loading && <Loader2 className="h-4 w-4 animate-spin" />}
              Guardar contraseña
            </Button>
          </form>

          <p className="mt-6 text-center text-sm">
            <Link
              href="/forgot-password"
              className="inline-flex items-center gap-1.5 font-semibold text-violet-600 hover:text-violet-700 hover:underline"
            >
              <ArrowLeft className="h-3.5 w-3.5" />
              Solicitar nuevo enlace
            </Link>
          </p>
        </>
      )}
    </div>
  );
}

export default function ResetPasswordPage() {
  return (
    <div className="min-h-screen flex">
      {/* Left panel */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-violet-900 via-indigo-900 to-slate-900 relative overflow-hidden flex-col justify-between p-12">
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-1/4 -left-10 w-72 h-72 bg-violet-600/30 rounded-full blur-3xl" />
          <div className="absolute bottom-1/4 right-0 w-80 h-80 bg-indigo-600/20 rounded-full blur-3xl" />
        </div>
        <div className="flex items-center gap-3 relative">
          <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-violet-400 to-indigo-500 flex items-center justify-center shadow-lg shadow-violet-500/40">
            <FlaskConical className="h-5 w-5 text-white" />
          </div>
          <span className="text-2xl font-bold text-white">FermentAI</span>
        </div>
        <div className="relative">
          <h2 className="text-4xl font-bold text-white mb-4 leading-tight">
            Crea una contraseña
            <br />
            <span className="bg-gradient-to-r from-violet-300 to-indigo-300 bg-clip-text text-transparent">
              más segura
            </span>
          </h2>
          <p className="text-slate-300 text-lg leading-relaxed">
            Elige una contraseña robusta para proteger tu cuenta en FermentAI.
          </p>
        </div>
        <div className="flex gap-4 relative">
          {[
            { val: "8+", label: "Caracteres mínimos" },
            { val: "bcrypt", label: "Cifrado seguro" },
            { val: "UCC", label: "Plataforma oficial" },
          ].map(({ val, label }) => (
            <div key={val} className="rounded-xl border border-white/10 bg-white/5 px-4 py-3 backdrop-blur">
              <p className="text-2xl font-bold text-white">{val}</p>
              <p className="text-xs text-slate-400 mt-0.5">{label}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Right panel */}
      <div className="flex-1 flex items-center justify-center p-8 bg-slate-50">
        <Suspense>
          <ResetPasswordForm />
        </Suspense>
      </div>
    </div>
  );
}
