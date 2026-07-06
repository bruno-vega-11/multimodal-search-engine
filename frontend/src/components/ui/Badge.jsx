import { cn } from "../../lib/utils";

const TONES = {
  neutral: "bg-zinc-100 text-zinc-600 dark:bg-zinc-800 dark:text-zinc-300",
  accent: "bg-accent-50 text-accent-700 dark:bg-accent-500/10 dark:text-accent-400",
  success: "bg-emerald-50 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-400",
};

export function Badge({ children, tone = "neutral", className }) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium",
        TONES[tone],
        className
      )}
    >
      {children}
    </span>
  );
}

export default function MetricBadge({ label, value, tone = "neutral" }) {
  return (
    <div className="flex min-w-[110px] flex-col items-start gap-0.5 rounded-lg border border-zinc-200 bg-white px-3 py-2 dark:border-zinc-800 dark:bg-zinc-900">
      <span className="text-[10px] font-medium uppercase tracking-wide text-zinc-400 dark:text-zinc-500">
        {label}
      </span>
      <span
        className={cn(
          "font-mono text-sm font-semibold text-zinc-700 dark:text-zinc-200",
          tone === "accent" && "text-accent-600 dark:text-accent-400",
          tone === "success" && "text-emerald-600 dark:text-emerald-400"
        )}
      >
        {value}
      </span>
    </div>
  );
}
