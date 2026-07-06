import { AlertTriangle } from "lucide-react";
import { motion } from "framer-motion";
import Button from "./Button";

export default function ErrorState({ title = "Algo salió mal", description, onRetry }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="flex flex-col items-center justify-center gap-3 rounded-xl border border-red-100 bg-red-50/50 px-6 py-16 text-center dark:border-red-500/20 dark:bg-red-500/5"
    >
      <div className="flex size-12 items-center justify-center rounded-full bg-red-100 text-red-500 dark:bg-red-500/10 dark:text-red-400">
        <AlertTriangle className="size-6" />
      </div>
      <p className="text-base font-medium text-zinc-800 dark:text-zinc-100">{title}</p>
      {description && (
        <p className="max-w-sm text-sm text-zinc-500 dark:text-zinc-400">{description}</p>
      )}
      {onRetry && (
        <Button variant="outline" size="sm" onClick={onRetry} className="mt-2">
          Reintentar
        </Button>
      )}
    </motion.div>
  );
}
