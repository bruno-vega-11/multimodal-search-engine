import { forwardRef } from "react";
import { cn } from "../../lib/utils";

const TextField = forwardRef(function TextField({ className, ...props }, ref) {
  return (
    <input
      ref={ref}
      className={cn(
        "h-12 w-full rounded-xl border border-zinc-200 bg-white px-4 text-sm text-zinc-900 placeholder:text-zinc-400 transition-colors focus:border-accent-400 focus:outline-none focus:ring-4 focus:ring-accent-500/10 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-100 dark:placeholder:text-zinc-600 dark:focus:border-accent-500",
        className
      )}
      {...props}
    />
  );
});

export default TextField;
