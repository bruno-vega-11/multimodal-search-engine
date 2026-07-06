import { scoreToPercent, cn } from "../../lib/utils";

export default function ScorePill({ score, withBar = false, className }) {
  const percent = scoreToPercent(score);

  if (!withBar) {
    return (
      <span
        className={cn(
          "inline-flex shrink-0 items-center rounded-full bg-accent-50 px-2.5 py-1 font-mono text-xs font-semibold text-accent-700 dark:bg-accent-500/10 dark:text-accent-400",
          className
        )}
      >
        {percent}%
      </span>
    );
  }

  return (
    <div className={cn("w-full", className)}>
      <div className="mb-1.5 flex items-center justify-between">
        <span className="text-xs font-medium text-zinc-400 dark:text-zinc-500">Similitud</span>
        <span className="font-mono text-sm font-semibold text-accent-600 dark:text-accent-400">
          {percent}%
        </span>
      </div>
      <div className="h-1.5 w-full overflow-hidden rounded-full bg-zinc-100 dark:bg-zinc-800">
        <div
          className="h-full rounded-full bg-accent-500 transition-[width] duration-500 ease-out"
          style={{ width: `${percent}%` }}
        />
      </div>
    </div>
  );
}
