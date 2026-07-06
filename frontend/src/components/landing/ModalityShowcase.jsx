import { motion } from "framer-motion";
import { FileText, Image as ImageIcon, AudioLines } from "lucide-react";
import Card from "../ui/Card";

const ITEMS = [
  {
    icon: FileText,
    title: "Búsqueda por texto",
    description:
      "Escribe una frase o palabras clave. Un índice invertido (SPIMI) con tf-idf y similitud de coseno rankea canciones y fragmentos por relevancia semántica.",
  },
  {
    icon: ImageIcon,
    title: "Búsqueda por imagen",
    description:
      "Sube una foto de una prenda. El sistema extrae descriptores SIFT, los cuantiza contra un codebook visual y compara histogramas para hallar prendas similares.",
  },
  {
    icon: AudioLines,
    title: "Búsqueda por audio",
    description:
      "Sube un fragmento de audio. El motor calcula una huella acústica y la compara contra la colección para encontrar canciones parecidas.",
  },
];

const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.1 } },
};

const item = {
  hidden: { opacity: 0, y: 16 },
  show: { opacity: 1, y: 0, transition: { duration: 0.4 } },
};

export default function ModalityShowcase() {
  return (
    <section className="mx-auto max-w-6xl px-6 py-20">
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-80px" }}
        transition={{ duration: 0.4 }}
        className="mb-12 text-center"
      >
        <h2 className="text-2xl font-semibold tracking-tight text-zinc-900 sm:text-3xl dark:text-zinc-50">
          Tres modalidades, un solo motor
        </h2>
        <p className="mx-auto mt-3 max-w-xl text-zinc-500 dark:text-zinc-400">
          Cada modalidad tiene su propio pipeline de indexado y recuperación, unificados detrás de
          una sola interfaz.
        </p>
      </motion.div>

      <motion.div
        variants={container}
        initial="hidden"
        whileInView="show"
        viewport={{ once: true, margin: "-80px" }}
        className="grid gap-5 sm:grid-cols-3"
      >
        {ITEMS.map(({ icon: Icon, title, description }) => (
          <motion.div key={title} variants={item}>
            <Card hoverable className="h-full p-6">
              <div className="flex size-11 items-center justify-center rounded-xl bg-accent-50 text-accent-600 dark:bg-accent-500/10 dark:text-accent-400">
                <Icon className="size-5" />
              </div>
              <h3 className="mt-5 text-base font-semibold text-zinc-900 dark:text-zinc-50">
                {title}
              </h3>
              <p className="mt-2 text-sm leading-relaxed text-zinc-500 dark:text-zinc-400">
                {description}
              </p>
            </Card>
          </motion.div>
        ))}
      </motion.div>
    </section>
  );
}
