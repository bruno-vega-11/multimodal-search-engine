import { useNavigate } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { motion } from "framer-motion";
import { Badge } from "../ui/Badge";
import Button from "../ui/Button";
import MetricsBar from "./MetricsBar";
import { MODALITY_META, ROUTES } from "../../lib/constants";

export default function ResultsHeader({ modality, label, metrics }) {
  const navigate = useNavigate();

  return (
    <motion.div
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="mb-8"
    >
      <Button variant="ghost" size="sm" onClick={() => navigate(ROUTES.SEARCH)} className="-ml-3 mb-4">
        <ArrowLeft className="size-4" />
        Nueva búsqueda
      </Button>

      <div className="flex flex-wrap items-center gap-3">
        <Badge tone="accent">{MODALITY_META[modality]?.label ?? modality}</Badge>
        {label && (
          <h1 className="truncate text-lg font-medium text-zinc-800 dark:text-zinc-100">"{label}"</h1>
        )}
      </div>

      {metrics && (
        <div className="mt-4">
          <MetricsBar metrics={metrics} />
        </div>
      )}
    </motion.div>
  );
}
