"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Bell, LogOut, FlaskConical } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/useAuth";
import { useNotificaciones } from "@/hooks/useNotificaciones";

export function Navbar() {
  const { user, logout } = useAuth();
  const { data: notifs } = useNotificaciones();
  const router = useRouter();

  const unread = notifs?.filter((n) => !n.leida).length ?? 0;

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  return (
    <header className="sticky top-0 z-40 border-b border-slate-200 bg-white shadow-sm">
      <div className="flex h-16 items-center justify-between px-6">
        <Link href="/dashboard" className="flex items-center gap-2.5">
          <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-coffee-500 to-coffee-700 flex items-center justify-center shadow-md shadow-coffee-500/30">
            <FlaskConical className="h-4 w-4 text-white" />
          </div>
          <span className="text-xl font-bold bg-gradient-to-r from-coffee-600 to-coffee-800 bg-clip-text text-transparent">
            FermentAI
          </span>
        </Link>

        <div className="flex items-center gap-3">
          <Link href="/dashboard/notificaciones" className="relative">
            <Button variant="ghost" size="icon" className="hover:bg-slate-100">
              <Bell className="h-5 w-5 text-slate-600" />
              {unread > 0 && (
                <span className="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full bg-coffee-600 text-[10px] font-bold text-white shadow-md">
                  {unread > 9 ? "9+" : unread}
                </span>
              )}
            </Button>
          </Link>

          <div className="flex items-center gap-2 text-sm">
            <span className="text-slate-600 hidden sm:block">{user?.nombre}</span>
            <span className="rounded-full bg-coffee-100 px-2.5 py-0.5 text-xs font-semibold text-coffee-700 capitalize border border-coffee-200">
              {user?.rol}
            </span>
          </div>

          <Button
            variant="ghost"
            size="icon"
            onClick={handleLogout}
            title="Cerrar sesión"
            className="hover:bg-red-50 hover:text-red-600"
          >
            <LogOut className="h-5 w-5" />
          </Button>
        </div>
      </div>
    </header>
  );
}
