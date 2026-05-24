"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { FlaskConical, Loader2, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuth } from "@/hooks/useAuth";

export default function LoginPage() {
  const { login } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
      router.push("/dashboard");
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(msg || "Error al iniciar sesión");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* Left Panel — decorative */}
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
            Ciencia colaborativa
            <br />
            <span className="bg-gradient-to-r from-violet-300 to-indigo-300 bg-clip-text text-transparent">
              al alcance de todos
            </span>
          </h2>
          <p className="text-slate-300 text-lg leading-relaxed">
            Gestiona datasets de fermentación de café con imágenes y datos HPLC.
            Plataforma científica de la Universidad Cooperativa de Colombia.
          </p>
        </div>

        <div className="flex gap-4 relative">
          {[
            { val: "HPLC", label: "Datos fisicoquímicos" },
            { val: "ZIP", label: "Formato estándar" },
            { val: "18", label: "Columnas de datos" },
          ].map(({ val, label }) => (
            <div key={val} className="rounded-xl border border-white/10 bg-white/5 px-4 py-3 backdrop-blur">
              <p className="text-2xl font-bold text-white">{val}</p>
              <p className="text-xs text-slate-400 mt-0.5">{label}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Right Panel — form */}
      <div className="flex-1 flex items-center justify-center p-8 bg-slate-50">
        <div className="w-full max-w-md">
          <div className="flex items-center gap-2 mb-8 lg:hidden">
            <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center">
              <FlaskConical className="h-4 w-4 text-white" />
            </div>
            <span className="text-xl font-bold text-slate-900">FermentAI</span>
          </div>

          <h1 className="text-3xl font-bold text-slate-900 mb-1">Iniciar Sesión</h1>
          <p className="text-slate-500 mb-8">Ingresa con tus credenciales para acceder</p>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="space-y-2">
              <Label htmlFor="email" className="text-slate-700 font-medium">
                Email
              </Label>
              <Input
                id="email"
                type="email"
                placeholder="tu@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="h-11 border-slate-200 focus-visible:ring-violet-500"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="password" className="text-slate-700 font-medium">
                Contraseña
              </Label>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="h-11 border-slate-200 focus-visible:ring-violet-500"
                required
              />
            </div>

            {error && (
              <div className="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">
                {error}
              </div>
            )}

            <Button
              type="submit"
              disabled={loading}
              className="w-full h-11 bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-700 hover:to-indigo-700 text-white border-0 shadow-lg shadow-violet-500/30 font-semibold text-base"
            >
              {loading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <ArrowRight className="h-4 w-4" />
              )}
              Ingresar
            </Button>
          </form>

          <p className="mt-4 text-center text-sm">
            <Link href="/forgot-password" className="font-semibold text-violet-600 hover:text-violet-700 hover:underline">
              ¿Olvidaste tu contraseña?
            </Link>
          </p>

          <p className="mt-3 text-center text-sm text-slate-500">
            ¿No tienes cuenta?{" "}
            <Link href="/registro" className="font-semibold text-violet-600 hover:text-violet-700 hover:underline">
              Regístrate como colaborador
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
