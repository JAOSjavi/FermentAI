import Link from "next/link";
import { FlaskConical, Database, Shield, BarChart3, ArrowRight, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Header */}
      <header className="sticky top-0 z-50 flex items-center justify-between px-8 py-4 border-b border-white/10 bg-slate-950/80 backdrop-blur">
        <div className="flex items-center gap-2.5">
          <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-violet-500/40">
            <FlaskConical className="h-4.5 w-4.5 text-white" />
          </div>
          <span className="text-xl font-bold bg-gradient-to-r from-violet-400 to-indigo-400 bg-clip-text text-transparent">
            FermentAI
          </span>
        </div>
        <div className="flex gap-3">
          <Button variant="ghost" className="text-slate-300 hover:text-white hover:bg-white/10" asChild>
            <Link href="/login">Iniciar Sesión</Link>
          </Button>
          <Button
            className="bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-700 hover:to-indigo-700 text-white border-0 shadow-lg shadow-violet-500/30"
            asChild
          >
            <Link href="/registro">Registrarse</Link>
          </Button>
        </div>
      </header>

      {/* Hero */}
      <section className="relative mx-auto max-w-6xl px-8 py-32 text-center overflow-hidden">
        <div className="absolute inset-0 -z-10 pointer-events-none">
          <div className="absolute top-1/3 left-1/4 w-96 h-96 bg-violet-600/20 rounded-full blur-3xl" />
          <div className="absolute top-1/4 right-1/4 w-80 h-80 bg-indigo-600/20 rounded-full blur-3xl" />
          <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />
        </div>

        <div className="inline-flex items-center gap-2 rounded-full border border-violet-500/30 bg-violet-500/10 px-4 py-1.5 text-sm font-medium text-violet-300 mb-8">
          <Zap className="h-3.5 w-3.5" />
          Data Lake Científico · Universidad Cooperativa de Colombia
        </div>

        <h1 className="text-5xl sm:text-6xl font-extrabold tracking-tight mb-6 leading-tight">
          Gestión de Datasets de{" "}
          <span className="bg-gradient-to-r from-violet-400 via-fuchsia-400 to-indigo-400 bg-clip-text text-transparent">
            Fermentación de Café
          </span>
        </h1>

        <p className="text-xl text-slate-400 max-w-2xl mx-auto mb-10 leading-relaxed">
          Plataforma para la carga, revisión y consulta de imágenes de fermentación correlacionadas
          con datos fisicoquímicos HPLC. Ciencia abierta y colaborativa.
        </p>

        <div className="flex gap-4 justify-center flex-wrap">
          <Button
            size="lg"
            className="bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-700 hover:to-indigo-700 text-white shadow-xl shadow-violet-500/40 border-0 h-12 px-8 text-base font-semibold"
            asChild
          >
            <Link href="/registro">
              Comenzar como Colaborador
              <ArrowRight className="h-4 w-4" />
            </Link>
          </Button>
          <Button
            size="lg"
            variant="outline"
            className="border-white/20 text-white bg-transparent hover:bg-white/10 h-12 px-8 text-base"
            asChild
          >
            <Link href="/login">Acceder a Datasets</Link>
          </Button>
        </div>
      </section>

      {/* Features */}
      <section className="mx-auto max-w-5xl px-8 pb-32 grid md:grid-cols-3 gap-6">
        {[
          {
            icon: Database,
            gradient: "from-violet-500 to-purple-600",
            glow: "shadow-violet-500/30",
            title: "Data Lake Estructurado",
            desc: "Datasets ZIP con imágenes y metadatos HPLC en formato estandarizado. Validación automática de estructura y contenido.",
          },
          {
            icon: Shield,
            gradient: "from-indigo-500 to-blue-600",
            glow: "shadow-indigo-500/30",
            title: "Revisión Científica",
            desc: "Investigadores verifican cada aporte antes de su publicación. Ciclo completo de aprobación, correcciones y retroalimentación.",
          },
          {
            icon: BarChart3,
            gradient: "from-fuchsia-500 to-pink-600",
            glow: "shadow-fuchsia-500/30",
            title: "Exploración de Datos",
            desc: "Visualiza correlaciones entre imágenes de fermentación y compuestos como glucosa, etanol y ácidos orgánicos.",
          },
        ].map(({ icon: Icon, gradient, glow, title, desc }) => (
          <div
            key={title}
            className="rounded-2xl border border-white/10 bg-white/5 backdrop-blur p-6 hover:bg-white/8 hover:border-white/20 transition-all"
          >
            <div className={`mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br ${gradient} shadow-lg ${glow}`}>
              <Icon className="h-6 w-6 text-white" />
            </div>
            <h3 className="text-lg font-semibold mb-2 text-white">{title}</h3>
            <p className="text-sm text-slate-400 leading-relaxed">{desc}</p>
          </div>
        ))}
      </section>

      <footer className="border-t border-white/10 py-8 text-center text-sm text-slate-500">
        FermentAI — Universidad Cooperativa de Colombia &copy; {new Date().getFullYear()}
      </footer>
    </div>
  );
}
