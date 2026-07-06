import { useState } from "react";
import { ImageOff } from "lucide-react";
import { getImageRenderUrl } from "../../../api";

export default function ImageCardBody({ result }) {
  const [broken, setBroken] = useState(false);

  return (
    <div className="flex flex-1 flex-col gap-3">
      <div className="aspect-square w-full overflow-hidden rounded-lg bg-zinc-100 dark:bg-zinc-800">
        {broken ? (
          <div className="flex h-full w-full flex-col items-center justify-center gap-2 text-zinc-400 dark:text-zinc-600">
            <ImageOff className="size-6" />
            <span className="text-xs">Imagen no disponible</span>
          </div>
        ) : (
          <img
            src={getImageRenderUrl(result.id)}
            alt={result.metadata.nombre_archivo}
            loading="lazy"
            onError={() => setBroken(true)}
            className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-[1.03]"
          />
        )}
      </div>
      <p className="truncate text-sm font-medium text-zinc-700 dark:text-zinc-300">
        {result.metadata.nombre_archivo}
      </p>
    </div>
  );
}
