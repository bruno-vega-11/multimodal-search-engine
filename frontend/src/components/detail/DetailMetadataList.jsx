export default function DetailMetadataList({ items }) {
  const visible = items.filter((item) => item.value !== undefined && item.value !== null && item.value !== "");

  return (
    <dl className="divide-y divide-zinc-100 rounded-xl border border-zinc-200 dark:divide-zinc-800 dark:border-zinc-800">
      {visible.map(({ label, value, muted }) => (
        <div key={label} className="flex items-center justify-between gap-4 px-4 py-3">
          <dt className="text-sm text-zinc-500 dark:text-zinc-400">{label}</dt>
          <dd
            className={`truncate text-right text-sm font-medium ${
              muted ? "text-zinc-400 dark:text-zinc-600" : "text-zinc-800 dark:text-zinc-100"
            }`}
          >
            {value}
          </dd>
        </div>
      ))}
    </dl>
  );
}
