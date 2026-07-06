import { useDropzone } from "../../hooks/useDropzone";
import { cn } from "../../lib/utils";

export default function Dropzone({ accept, onFile, hint, icon, preview, fileName }) {
  const { isDragging, dropzoneProps, inputProps } = useDropzone({ onFile });

  return (
    <div
      {...dropzoneProps}
      className={cn(
        "flex cursor-pointer flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed p-10 text-center transition-colors duration-150",
        isDragging
          ? "border-accent-400 bg-accent-50/50 dark:bg-accent-500/5"
          : "border-zinc-200 hover:border-zinc-300 hover:bg-zinc-50 dark:border-zinc-800 dark:hover:border-zinc-700 dark:hover:bg-zinc-900/50"
      )}
    >
      {preview ? (
        <img src={preview} alt="preview" className="h-36 w-36 rounded-lg object-cover" />
      ) : (
        <div className="flex size-12 items-center justify-center rounded-full bg-zinc-100 text-zinc-400 dark:bg-zinc-800 dark:text-zinc-500">
          {icon}
        </div>
      )}
      <p className="text-sm text-zinc-500 dark:text-zinc-400">
        {fileName ? (
          <span className="font-medium text-zinc-800 dark:text-zinc-100">{fileName}</span>
        ) : (
          hint
        )}
      </p>
      <input {...inputProps} accept={accept} />
    </div>
  );
}
