"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Bell, LogOut, FlaskConical } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/useAuth";
import { useNotificaciones } from "@/hooks/useNotificaciones";
import { cn } from "@/lib/utils";

const roleStyles = {
  colaborador: {
    logoGradient: "from-indigo-500 to-indigo-700",
    logoGlow:     "shadow-indigo-500/40",
    badge:        "bg-indigo-50 text-indigo-700 border-indigo-200",
    notifBg:      "bg-indigo-600",
    notifGlow:    "shadow-indigo-500/50",
  },
  investigador: {
    logoGradient: "from-violet-500 to-violet-800",
    logoGlow:     "shadow-violet-500/40",
    badge:        "bg-violet-50 text-violet-700 border-violet-200",
    notifBg:      "bg-violet-600",
    notifGlow:    "shadow-violet-500/50",
  },
};

export function Navbar() {
  const { user, logout } = useAuth();
  const { data: notifs } = useNotificaciones();
  const router = useRouter();

  const unread = notifs?.filter((n) => !n.leida).length ?? 0;
  const role   = (user?.rol ?? "colaborador") as keyof typeof roleStyles;
  const rs     = roleStyles[role] ?? roleStyles.colaborador;

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  return (
    <header className="sticky top-0 z-40 border-b border-slate-100 bg-white/95 backdrop-blur-sm">
      <div className="flex h-16 items-center justify-between px-6">

        {/* Logo */}
        <Link href="/dashboard" className="flex items-center gap-2.5 group">
          <div
            className={cn(
              "h-8 w-8 rounded-xl bg-gradient-to-br flex items-center justify-center shadow-md",
              "transition-all duration-200 group-hover:scale-105 group-hover:shadow-lg",
              rs.logoGradient,
              rs.logoGlow
            )}
          >
            <FlaskConical className="h-4 w-4 text-white" />
          </div>
          <span className="font-display text-xl font-bold tracking-tight text-slate-800">
            FermentAI
          </span>
        </Link>

        {/* Right side */}
        <div className="flex items-center gap-1.5">

          {/* Notifications bell */}
          <Link href="/dashboard/notificaciones" className="relative">
            <Button
              variant="ghost"
              size="icon"
              className="h-9 w-9 text-slate-500 hover:bg-slate-100 hover:text-slate-700 transition-colors"
            >
              <Bell className="h-[18px] w-[18px]" />
            </Button>
            {unread > 0 && (
              <span
                className={cn(
                  "absolute -right-0.5 -top-0.5 flex h-[18px] w-[18px] items-center justify-center",
                  "rounded-full text-[9px] font-bold text-white shadow-md animate-badge-bounce",
                  rs.notifBg,
                  rs.notifGlow
                )}
              >
                {unread > 9 ? "9+" : unread}
              </span>
            )}
          </Link>

          {/* Vertical divider */}
          <div className="h-5 w-px bg-slate-200 mx-1" />

          {/* User identity */}
          <div className="flex items-center gap-2">
            <span className="hidden sm:block text-sm font-medium text-slate-700">
              {user?.nombre}
            </span>
            <span
              className={cn(
                "rounded-full px-2.5 py-1 text-xs font-semibold capitalize border transition-all",
                rs.badge
              )}
            >
              {user?.rol}
            </span>
          </div>

          {/* Logout */}
          <Button
            variant="ghost"
            size="icon"
            onClick={handleLogout}
            title="Cerrar sesión"
            className="h-9 w-9 ml-1 text-slate-500 hover:bg-red-50 hover:text-red-600 transition-colors"
          >
            <LogOut className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </header>
  );
}
