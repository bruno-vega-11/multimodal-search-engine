import { motion } from "framer-motion";
import SearchBar from "../components/search/SearchBar";

export default function Search() {
  return (
    <div className="mx-auto flex min-h-[calc(100vh-4rem)] max-w-2xl flex-col justify-center px-6 py-20">
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35 }}
        className="mb-10 text-center"
      >
        <h1 className="text-3xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
          ¿Qué estás buscando?
        </h1>
        <p className="mt-2 text-zinc-500 dark:text-zinc-400">
          Elige una modalidad y describe o sube tu consulta.
        </p>
      </motion.div>

      <SearchBar />
    </div>
  );
}
