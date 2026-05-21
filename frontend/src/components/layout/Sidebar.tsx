"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard, Upload, FolderOpen, CheckSquare, Database, BarChart3,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/hooks/useAuth";

const colabLinks = [
  { href: "/dashboard", label: "Inicio", icon: LayoutDashboard },
  { href: "/dashboard/mis-aportes/subir", label: "Subir Dataset", icon: Upload },
  { href: "/dashboard/mis-aportes", label: "Mis Aportes", icon: FolderOpen },
  { href: "/dashboard/datasets", label: "Datasets", icon: Database },
  { href: "/dashboard/visualizacion", label: "Visualización", icon: BarChart3 },
];

const investigadorExtra = [
  { href: "/dashboard/revisar", label: "Revisar Aportes", icon: CheckSquare },
];

export function Sidebar() {
  const pathname = usePathname();
  const { user } = useAuth();

  const links = user?.rol === "investigador"
    ? [...colabLinks, ...investigadorExtra]
    : colabLinks;

  const activeHref = links
    .filter(({ href }) => pathname === href || (href !== "/dashboard" && pathname.startsWith(href + "/")))
    .sort((a, b) => b.href.length - a.href.length)[0]?.href;

  return (
    <aside className="hidden md:flex w-64 flex-col border-r border-slate-200 bg-white min-h-[calc(100vh-4rem)]">
      <nav className="flex flex-col gap-1 p-3 pt-5">
        {links.map(({ href, label, icon: Icon }) => {
          const active = href === activeHref;
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all",
                active
                  ? "bg-coffee-50 text-coffee-700 border border-coffee-200/60 shadow-sm"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground"
              )}
            >
              <Icon className={cn("h-5 w-5 flex-shrink-0", active ? "text-coffee-600" : "text-muted-foreground")} />
              {label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
