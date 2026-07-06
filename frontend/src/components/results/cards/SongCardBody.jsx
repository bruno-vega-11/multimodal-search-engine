import { Music } from "lucide-react";
import { Badge } from "../../ui/Badge";
import { DATASET_TYPE_LABELS } from "../../../lib/constants";

export default function SongCardBody({ result }) {
  return (
    <div className="flex flex-1 flex-col gap-3">
      <div className="flex size-10 items-center justify-center rounded-lg bg-zinc-100 text-zinc-500 dark:bg-zinc-800 dark:text-zinc-400">
        <Music className="size-4.5" />
      </div>
      <div className="min-w-0 flex-1">
        <h3 className="truncate text-sm font-semibold text-zinc-900 dark:text-zinc-50">
          {result.metadata.title}
        </h3>
        <p className="truncate text-sm text-zinc-500 dark:text-zinc-400">{result.metadata.artist}</p>
      </div>
      <Badge tone="neutral" className="w-fit">
        {DATASET_TYPE_LABELS[result.dataset_type] ?? result.dataset_type}
      </Badge>
    </div>
  );
}
