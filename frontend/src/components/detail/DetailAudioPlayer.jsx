export default function DetailAudioPlayer({ src }) {
  if (!src) return null;
  return (
    <div className="rounded-xl border border-zinc-200 bg-zinc-50 p-5 dark:border-zinc-800 dark:bg-zinc-900">
      <audio controls preload="metadata" src={src} className="w-full" />
    </div>
  );
}
