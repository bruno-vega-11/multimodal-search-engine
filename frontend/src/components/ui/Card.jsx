import { motion } from "framer-motion";
import { cn } from "../../lib/utils";

export default function Card({ hoverable = false, className, children, ...props }) {
  return (
    <motion.div
      className={cn(
        "rounded-xl border border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900",
        hoverable &&
          "transition-all duration-200 hover:-translate-y-0.5 hover:border-zinc-300 hover:shadow-lg hover:shadow-zinc-900/5 dark:hover:border-zinc-700 dark:hover:shadow-black/20",
        className
      )}
      {...props}
    >
      {children}
    </motion.div>
  );
}
