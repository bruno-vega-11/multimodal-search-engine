import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { ArrowRight } from "lucide-react";
import Button from "../ui/Button";
import { Badge } from "../ui/Badge";
import { ROUTES } from "../../lib/constants";

export default function Hero() {
  const navigate = useNavigate();

  return (
    <section className="relative overflow-hidden px-6 pb-24 pt-28 sm:pt-36">
      <div
        aria-hidden
        className="pointer-events-none absolute inset-x-0 top-0 -z-10 h-[560px] bg-[radial-gradient(ellipse_60%_50%_at_50%_-10%,rgba(249,115,22,0.12),transparent)]"
      />
      <div className="mx-auto flex max-w-3xl flex-col items-center text-center">
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          <Badge tone="accent">Proyecto de Base de Datos 2</Badge>
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.05 }}
          className="mt-6 text-4xl font-semibold tracking-tight text-zinc-900 sm:text-6xl dark:text-zinc-50"
        >
          Un motor de búsqueda que entiende
          <span className="text-accent-500"> texto, imagen y audio</span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.1 }}
          className="mt-6 max-w-xl text-balance text-lg leading-relaxed text-zinc-500 dark:text-zinc-400"
        >
          Sistema de recuperación de información heterogéneo construido desde cero: índices
          invertidos propios, cuantización visual y huellas acústicas — sin motores de búsqueda de
          terceros.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.15 }}
          className="mt-10"
        >
          <Button size="lg" variant="accent" onClick={() => navigate(ROUTES.SEARCH)}>
            Comenzar a buscar
            <ArrowRight className="size-4" />
          </Button>
        </motion.div>
      </div>
    </section>
  );
}
