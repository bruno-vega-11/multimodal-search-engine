import { ChevronDown } from "lucide-react";
import { cn } from "../../lib/utils";

export default function Select({ value, onChange, options, className }) {
  return (
    <div className={cn("relative", className)}>
      <select
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="h-12 w-full appearance-none rounded-xl border border-zinc-200 bg-white px-4 pr-9 text-sm text-zinc-700 transition-colors focus:border-accent-400 focus:outline-none focus:ring-4 focus:ring-accent-500/10 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-200"
      >
        {options.map((opt) => (
          <option key={opt} value={opt}>
            Top {opt}
          </option>
        ))}
      </select>
      <ChevronDown className="pointer-events-none absolute right-3 top-1/2 size-4 -translate-y-1/2 text-zinc-400" />
    </div>
  );
}
