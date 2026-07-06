import { motion } from "framer-motion";

export default function EmptyState({ icon, title, description, action }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="flex flex-col items-center justify-center gap-3 py-24 text-center"
    >
      <div className="flex size-14 items-center justify-center rounded-2xl bg-zinc-100 text-zinc-400 dark:bg-zinc-800 dark:text-zinc-500">
        {icon}
      </div>
      <p className="text-base font-medium text-zinc-700 dark:text-zinc-200">{title}</p>
      {description && (
        <p className="max-w-sm text-sm text-zinc-400 dark:text-zinc-500">{description}</p>
      )}
      {action && <div className="mt-2">{action}</div>}
    </motion.div>
  );
}
