interface Props {
  password: string;
}

const LEVELS = [
  { label: "Muy débil",  bar: "w-1/6",  bg: "bg-red-500",     text: "text-red-500"     },
  { label: "Débil",      bar: "w-2/6",  bg: "bg-orange-500",  text: "text-orange-500"  },
  { label: "Regular",    bar: "w-3/6",  bg: "bg-yellow-500",  text: "text-yellow-500"  },
  { label: "Buena",      bar: "w-4/6",  bg: "bg-lime-500",    text: "text-lime-600"    },
  { label: "Fuerte",     bar: "w-5/6",  bg: "bg-green-500",   text: "text-green-600"   },
  { label: "Muy fuerte", bar: "w-full", bg: "bg-emerald-500", text: "text-emerald-600" },
];

function score(pw: string): number {
  let s = 0;
  if (pw.length >= 8)            s++;
  if (pw.length >= 12)           s++;
  if (/[a-z]/.test(pw))          s++;
  if (/[A-Z]/.test(pw))          s++;
  if (/[0-9]/.test(pw))          s++;
  if (/[^a-zA-Z0-9]/.test(pw))  s++;
  return s;
}

export function PasswordStrength({ password }: Props) {
  if (!password) return null;
  const s = score(password);
  const idx = Math.max(0, Math.min(s - 1, 5));
  const { label, bar, bg, text } = LEVELS[idx];

  return (
    <div className="space-y-1.5 mt-1">
      <div className="h-1.5 w-full rounded-full bg-slate-100 overflow-hidden">
        <div className={`h-full rounded-full transition-all duration-300 ${bar} ${bg}`} />
      </div>
      <p className={`text-xs font-medium ${text}`}>{label}</p>
    </div>
  );
}
