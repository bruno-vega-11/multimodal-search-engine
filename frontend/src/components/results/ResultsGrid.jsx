import { motion } from "framer-motion";
import { SearchX } from "lucide-react";
import ResultCard from "./ResultCard";
import EmptyState from "../ui/EmptyState";
import { MODALITIES } from "../../lib/constants";

const gridContainer = {
  hidden: {},
  show: { transition: { staggerChildren: 0.06 } },
};

function CardGrid({ children, className }) {
  return (
    <motion.div variants={gridContainer} initial="hidden" animate="show" className={className}>
      {children}
    </motion.div>
  );
}

const NO_RESULTS = (
  <EmptyState
    icon={<SearchX className="size-6" />}
    title="Sin resultados"
    description="No encontramos coincidencias para esta búsqueda. Intenta con otra consulta."
  />
);

export default function ResultsGrid({ modality, results }) {
  if (modality === MODALITIES.TEXTO) {
    const { by_song = [], by_chunk = [] } = results ?? {};
    if (by_song.length === 0 && by_chunk.length === 0) return NO_RESULTS;

    return (
      <div className="grid gap-8 md:grid-cols-2">
        <section>
          <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-zinc-400 dark:text-zinc-500">
            Por canción ({by_song.length})
          </h2>
          {by_song.length === 0 ? (
            <p className="text-sm text-zinc-400">Sin coincidencias.</p>
          ) : (
            <CardGrid className="scroll-thin flex max-h-[70vh] flex-col gap-3 overflow-y-auto pr-1">
              {by_song.map((r, i) => (
                <ResultCard key={r.id} result={r} rank={i + 1} kind="song" />
              ))}
            </CardGrid>
          )}
        </section>

        <section>
          <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-zinc-400 dark:text-zinc-500">
            Por fragmento ({by_chunk.length})
          </h2>
          {by_chunk.length === 0 ? (
            <p className="text-sm text-zinc-400">Sin coincidencias.</p>
          ) : (
            <CardGrid className="scroll-thin flex max-h-[70vh] flex-col gap-3 overflow-y-auto pr-1">
              {by_chunk.map((r, i) => (
                <ResultCard key={r.id} result={r} rank={i + 1} kind="chunk" />
              ))}
            </CardGrid>
          )}
        </section>
      </div>
    );
  }

  const items = results ?? [];
  if (items.length === 0) return NO_RESULTS;

  if (modality === MODALITIES.AUDIO) {
    return (
      <CardGrid className="flex flex-col gap-3">
        {items.map((r, i) => (
          <ResultCard key={r.id} result={r} rank={i + 1} kind="audio" />
        ))}
      </CardGrid>
    );
  }

  return (
    <CardGrid className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
      {items.map((r, i) => (
        <ResultCard key={r.id} result={r} rank={i + 1} kind="image" />
      ))}
    </CardGrid>
  );
}
