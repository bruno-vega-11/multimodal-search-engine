import { Music2 } from "lucide-react";
import { Badge } from "../../ui/Badge";
import { formatDuration } from "../../../lib/utils";
import { DATASET_TYPE_LABELS } from "../../../lib/constants";

export default function AudioCardBody({ result }) {
  const { title, artist, album, duration_seconds, audio_url } = result.metadata;

  return (
    <div className="flex flex-1 items-center gap-4">
      <div className="flex size-11 shrink-0 items-center justify-center rounded-lg bg-zinc-100 text-zinc-500 dark:bg-zinc-800 dark:text-zinc-400">
        <Music2 className="size-5" />
      </div>

      <div className="min-w-0 flex-1">
        <h3 className="truncate text-sm font-semibold text-zinc-900 dark:text-zinc-50">{title}</h3>
        <p className="truncate text-sm text-zinc-500 dark:text-zinc-400">
          {artist} · {album} · {formatDuration(duration_seconds)}
        </p>
        {audio_url && (
          <div onClick={(e) => e.stopPropagation()} onPointerDown={(e) => e.stopPropagation()} className="mt-2">
            <audio controls preload="none" src={audio_url} className="h-8 w-full max-w-xs" />
          </div>
        )}
      </div>

      <Badge tone="neutral" className="hidden shrink-0 sm:inline-flex">
        {DATASET_TYPE_LABELS[result.dataset_type] ?? result.dataset_type}
      </Badge>
    </div>
  );
}
