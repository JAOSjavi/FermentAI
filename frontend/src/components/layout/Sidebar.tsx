"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Upload,
  FolderOpen,
  CheckSquare,
  Database,
  BarChart3,
  Microscope,
  Users,
  X,
  Settings,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/hooks/useAuth";

const colabLinks = [
  { href: "/dashboard",                   label: "Inicio",        icon: LayoutDashboard },
  { href: "/dashboard/mis-aportes/subir", label: "Subir Dataset", icon: Upload          },
  { href: "/dashboard/mis-aportes",       label: "Mis Aportes",   icon: FolderOpen      },
  { href: "/dashboard/datasets",          label: "Datasets",      icon: Database        },
  { href: "/dashboard/visualizacion",     label: "Visualización", icon: BarChart3       },
  { href: "/dashboard/ajustes",           label: "Ajustes",       icon: Settings        },
];

const investigadorLinks = [
  { href: "/dashboard/revisar", label: "Revisar Aportes", icon: CheckSquare },
];

const roleConfig = {
  colaborador: {
    label:        "Colaborador",
    RoleIcon:     Users,
    topBar:       "from-indigo-700 via-indigo-500 to-indigo-400",
    badge:        "bg-indigo-50 text-indigo-700 border border-indigo-200/80",
    sectionTxt:   "text-indigo-300",
    active: {
      bg:     "bg-indigo-50",
      text:   "text-indigo-700",
      border: "border-indigo-200/70",
      shadow: "shadow-sm shadow-indigo-200/60",
      icon:   "text-indigo-600",
      dot:    "bg-indigo-500",
    },
    hoverItem:    "hover:bg-indigo-50/70 hover:text-indigo-700",
    extraSection: null as string | null,
  },
  investigador: {
    label:        "Investigador",
    RoleIcon:     Microscope,
    topBar:       "from-violet-800 via-violet-600 to-violet-400",
    badge:        "bg-violet-50 text-violet-700 border border-violet-200/80",
    sectionTxt:   "text-violet-300",
    active: {
      bg:     "bg-violet-50",
      text:   "text-violet-700",
      border: "border-violet-200/70",
      shadow: "shadow-sm shadow-violet-200/60",
      icon:   "text-violet-600",
      dot:    "bg-violet-500",
    },
    hoverItem:    "hover:bg-violet-50/70 hover:text-violet-700",
    extraSection: "Herramientas" as string | null,
  },
};

/* ─── Shared nav content ──────────────────────────────────── */

function SidebarContent({
  cfg,
  mainLinks,
  extraLinks,
  activeHref,
  onClose,
}: {
  cfg:         typeof roleConfig[keyof typeof roleConfig];
  mainLinks:   typeof colabLinks;
  extraLinks:  typeof investigadorLinks;
  activeHref:  string | undefined;
  onClose?:    () => void;
}) {
  const { RoleIcon } = cfg;

  return (
    <>
      {/* Colored top stripe */}
      <div
        className={cn(
          "absolute top-0 left-0 right-0 h-[3px] bg-gradient-to-r origin-left animate-role-stripe",
          cfg.topBar
        )}
      />

      {/* Role badge row */}
      <div className="px-4 pt-6 pb-2 flex items-center justify-between animate-fade-in">
        <span
          className={cn(
            "inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-semibold tracking-wide",
            cfg.badge
          )}
        >
          <RoleIcon className="h-3 w-3" />
          {cfg.label}
        </span>
        {onClose && (
          <button
            onClick={onClose}
            className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition-colors"
            aria-label="Cerrar menú"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex flex-col gap-0.5 px-3 pt-2 pb-4 flex-1 overflow-y-auto scrollbar-thin">
        <p className={cn(
          "text-[10px] font-bold tracking-[0.15em] uppercase px-3 mb-1.5",
          cfg.sectionTxt
        )}>
          Navegación
        </p>

        {mainLinks.map(({ href, label, icon: Icon }, i) => {
          const active = href === activeHref;
          return (
            <Link
              key={href}
              href={href}
              onClick={onClose}
              style={{ animationDelay: `${i * 40}ms` }}
              className={cn(
                "group flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium",
                "transition-all duration-200 animate-slide-in-left",
                active
                  ? cn(cfg.active.bg, cfg.active.text, "border", cfg.active.border, cfg.active.shadow)
                  : cn("text-slate-500 border border-transparent", cfg.hoverItem)
              )}
            >
              <Icon
                className={cn(
                  "h-[18px] w-[18px] flex-shrink-0 transition-transform duration-200 group-hover:scale-110",
                  active ? cfg.active.icon : "text-slate-400 group-hover:text-current"
                )}
              />
              <span className="flex-1 truncate">{label}</span>
              {active && (
                <span className={cn("h-1.5 w-1.5 rounded-full flex-shrink-0", cfg.active.dot)} />
              )}
            </Link>
          );
        })}

        {extraLinks.length > 0 && (
          <>
            <div className="my-3 mx-1 border-t border-slate-100" />
            <p className={cn(
              "text-[10px] font-bold tracking-[0.15em] uppercase px-3 mb-1.5",
              cfg.sectionTxt
            )}>
              {cfg.extraSection}
            </p>
            {extraLinks.map(({ href, label, icon: Icon }, i) => {
              const active = href === activeHref;
              return (
                <Link
                  key={href}
                  href={href}
                  onClick={onClose}
                  style={{ animationDelay: `${(mainLinks.length + i) * 40}ms` }}
                  className={cn(
                    "group flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium",
                    "transition-all duration-200 animate-slide-in-left",
                    active
                      ? cn(cfg.active.bg, cfg.active.text, "border", cfg.active.border, cfg.active.shadow)
                      : cn("text-slate-500 border border-transparent", cfg.hoverItem)
                  )}
                >
                  <Icon
                    className={cn(
                      "h-[18px] w-[18px] flex-shrink-0 transition-transform duration-200 group-hover:scale-110",
                      active ? cfg.active.icon : "text-slate-400 group-hover:text-current"
                    )}
                  />
                  <span className="flex-1 truncate">{label}</span>
                  {active && (
                    <span className={cn("h-1.5 w-1.5 rounded-full flex-shrink-0", cfg.active.dot)} />
                  )}
                </Link>
              );
            })}
          </>
        )}
      </nav>

      {/* Bottom label */}
      <div className="px-4 py-3 border-t border-slate-100">
        <p className="text-[10px] text-slate-400 font-medium text-center tracking-widest uppercase">
          FermentAI · UCC
        </p>
      </div>
    </>
  );
}

/* ─── Exported Sidebar ────────────────────────────────────── */

export function Sidebar({
  mobileOpen = false,
  onClose,
}: {
  mobileOpen?: boolean;
  onClose?: () => void;
}) {
  const pathname  = usePathname();
  const { user }  = useAuth();

  const role      = user?.rol === "investigador" ? "investigador" : "colaborador";
  const cfg       = roleConfig[role];
  const mainLinks = colabLinks;
  const extraLinks = role === "investigador" ? investigadorLinks : [];

  const allLinks  = [...mainLinks, ...extraLinks];
  const activeHref = allLinks
    .filter(({ href }) =>
      pathname === href || (href !== "/dashboard" && pathname.startsWith(href + "/"))
    )
    .sort((a, b) => b.href.length - a.href.length)[0]?.href;

  return (
    <>
      {/* Desktop sidebar */}
      <aside className="hidden md:flex w-60 flex-col border-r border-slate-100 bg-white min-h-[calc(100vh-4rem)] relative overflow-hidden">
        <SidebarContent
          cfg={cfg}
          mainLinks={mainLinks}
          extraLinks={extraLinks}
          activeHref={activeHref}
        />
      </aside>

      {/* Mobile overlay drawer */}
      {mobileOpen && (
        <div className="fixed inset-0 z-50 md:hidden">
          {/* Backdrop */}
          <div
            className="absolute inset-0 bg-black/40 backdrop-blur-sm"
            onClick={onClose}
            aria-hidden="true"
          />
          {/* Drawer panel */}
          <aside className="absolute left-0 top-0 bottom-0 w-72 flex flex-col bg-white shadow-2xl overflow-hidden animate-drawer-slide">
            <SidebarContent
              cfg={cfg}
              mainLinks={mainLinks}
              extraLinks={extraLinks}
              activeHref={activeHref}
              onClose={onClose}
            />
          </aside>
        </div>
      )}
    </>
  );
}
