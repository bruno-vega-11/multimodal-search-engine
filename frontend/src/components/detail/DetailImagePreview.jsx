import { useState } from "react";
import { ImageOff } from "lucide-react";

export default function DetailImagePreview({ src, alt }) {
  const [broken, setBroken] = useState(false);

  return (
    <div className="flex aspect-square w-full max-w-md items-center justify-center overflow-hidden rounded-xl bg-zinc-100 dark:bg-zinc-800">
      {broken ? (
        <div className="flex flex-col items-center gap-2 text-zinc-400 dark:text-zinc-600">
          <ImageOff className="size-8" />
          <span className="text-sm">Imagen no disponible</span>
        </div>
      ) : (
        <img src={src} alt={alt} onError={() => setBroken(true)} className="h-full w-full object-cover" />
      )}
    </div>
  );
}
