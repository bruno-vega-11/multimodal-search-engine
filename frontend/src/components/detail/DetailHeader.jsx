import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowLeft } from "lucide-react";
import Button from "../ui/Button";
import { Badge } from "../ui/Badge";
import ScorePill from "../ui/ScorePill";
import { DATASET_TYPE_LABELS } from "../../lib/constants";

export default function DetailHeader({ title, datasetType, score }) {
  const navigate = useNavigate();

  return (
    <motion.div
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="mb-8"
    >
      <Button variant="ghost" size="sm" onClick={() => navigate(-1)} className="-ml-3 mb-6">
        <ArrowLeft className="size-4" />
        Volver a resultados
      </Button>

      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <Badge tone="neutral" className="mb-3">
            {DATASET_TYPE_LABELS[datasetType] ?? datasetType}
          </Badge>
          <h1 className="text-2xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
            {title}
          </h1>
        </div>
        <ScorePill score={score} withBar className="w-full max-w-55" />
      </div>
    </motion.div>
  );
}
