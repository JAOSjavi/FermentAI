"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { FlaskConical, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { PasswordInput } from "@/components/ui/password-input";
import { PasswordStrength } from "@/components/ui/password-strength";
import api from "@/lib/api";

export default function RegistroPage() {
  const router = useRouter();
  const [form, setForm]   = useState({ nombre: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await api.post("/api/auth/register", form);
      router.push("/login?registered=1");
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(msg || "Error al registrarse");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-50 via-white to-slate-50 p-4">
      <div className="w-full max-w-md">
        <div className="flex flex-col items-center mb-8">
          <Link href="/" className="flex flex-col items-center">
            <div className="h-14 w-14 rounded-2xl bg-gradient-to-br from-indigo-500 to-indigo-700 flex items-center justify-center shadow-lg shadow-indigo-500/30 mb-3">
              <FlaskConical className="h-7 w-7 text-white" />
            </div>
            <h1 className="font-display text-3xl font-bold text-slate-900 tracking-tight">FermentAI</h1>
          </Link>
          <p className="text-muted-foreground text-sm mt-1">Registro de Colaborador</p>
        </div>

        <Card className="border-slate-100 shadow-sm">
          <CardHeader>
            <CardTitle className="font-display">Crear Cuenta</CardTitle>
            <CardDescription>Regístrate para subir datasets de fermentación</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-1.5">
                <Label htmlFor="nombre">Nombre completo</Label>
                <Input
                  id="nombre"
                  name="nombre"
                  placeholder="Tu nombre"
                  value={form.nombre}
                  onChange={handleChange}
                  required
                />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="email">Email institucional</Label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  placeholder="tu@ucc.edu.co"
                  value={form.email}
                  onChange={handleChange}
                  required
                />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="password">Contraseña</Label>
                <PasswordInput
                  id="password"
                  name="password"
                  placeholder="Mínimo 8 caracteres"
                  value={form.password}
                  onChange={handleChange}
                  required
                  minLength={8}
                />
                <PasswordStrength password={form.password} />
              </div>

              {error && (
                <p className="text-sm text-destructive bg-destructive/10 rounded-lg px-3 py-2">
                  {error}
                </p>
              )}

              <Button type="submit" className="w-full" variant="coffee" disabled={loading}>
                {loading && <Loader2 className="h-4 w-4 animate-spin" />}
                Registrarme como Colaborador
              </Button>
            </form>

            <p className="mt-4 text-center text-sm text-muted-foreground">
              ¿Ya tienes cuenta?{" "}
              <Link href="/login" className="font-semibold text-indigo-600 hover:text-indigo-700 hover:underline underline-offset-2">
                Iniciar Sesión
              </Link>
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
