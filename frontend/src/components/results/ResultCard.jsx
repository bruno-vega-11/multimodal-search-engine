import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowUpRight } from "lucide-react";
import Card from "../ui/Card";
import ScorePill from "../ui/ScorePill";
import SongCardBody from "./cards/SongCardBody";
import ChunkCardBody from "./cards/ChunkCardBody";
import AudioCardBody from "./cards/AudioCardBody";
import ImageCardBody from "./cards/ImageCardBody";
import { ROUTES } from "../../lib/constants";

const BODIES = {
  song: SongCardBody,
  chunk: ChunkCardBody,
  audio: AudioCardBody,
  image: ImageCardBody,
};

const ROUTE_KIND = {
  song: "text-song",
  chunk: "text-chunk",
  audio: "audio",
  image: "image",
};

export const cardEntrance = {
  hidden: { opacity: 0, y: 14 },
  show: { opacity: 1, y: 0, transition: { duration: 0.35 } },
};

export default function ResultCard({ result, rank, kind }) {
  const Body = BODIES[kind];
  const path = ROUTES.detail(ROUTE_KIND[kind], result.id);

  return (
    <motion.div variants={cardEntrance} className="h-full">
      <Link to={path} className="group block h-full">
        <Card hoverable className="flex h-full flex-col p-4">
          <div className="mb-3 flex items-center justify-between">
            <span className="font-mono text-xs text-zinc-400 dark:text-zinc-600">
              #{rank.toString().padStart(2, "0")}
            </span>
            <ScorePill score={result.score} />
          </div>

          <Body result={result} />

          <div className="mt-4 flex items-center justify-end gap-1 text-xs font-medium text-zinc-400 transition-colors group-hover:text-accent-600 dark:group-hover:text-accent-400">
            Ver detalle
            <ArrowUpRight className="size-3.5" />
          </div>
        </Card>
      </Link>
    </motion.div>
  );
}
