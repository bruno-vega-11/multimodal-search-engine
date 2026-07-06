import { useParams, useNavigate } from "react-router-dom";
import DetailHeader from "../components/detail/DetailHeader";
import DetailMetadataList from "../components/detail/DetailMetadataList";
import DetailAudioPlayer from "../components/detail/DetailAudioPlayer";
import DetailImagePreview from "../components/detail/DetailImagePreview";
import EmptyState from "../components/ui/EmptyState";
import Button from "../components/ui/Button";
import { useSearch } from "../context/SearchContext";
import { getImageRenderUrl } from "../api";
import { formatDuration } from "../lib/utils";
import { ROUTES } from "../lib/constants";
import { FileQuestion } from "lucide-react";

export default function Detail() {
  const { modality, id } = useParams();
  const navigate = useNavigate();
  const { findResultById } = useSearch();
  const result = findResultById(modality, id);

  if (!result) {
    return (
      <div className="mx-auto max-w-2xl px-6 py-20">
        <EmptyState
          icon={<FileQuestion className="size-6" />}
          title="Este resultado ya no está disponible"
          description="Es probable que la página se haya refrescado y se perdió la referencia a esta búsqueda. Realiza una nueva búsqueda para continuar."
          action={<Button onClick={() => navigate(ROUTES.SEARCH)}>Ir a buscar</Button>}
        />
      </div>
    );
  }

  const { metadata } = result;

  let title = metadata.title ?? metadata.nombre_archivo ?? metadata.filename ?? `Resultado ${result.id}`;
  let body = null;

  if (modality === "text-song") {
    body = <DetailMetadataList items={[{ label: "Título", value: metadata.title }, { label: "Artista", value: metadata.artist }, { label: "ID", value: result.id }]} />;
  } else if (modality === "text-chunk") {
    body = (
      <div className="flex flex-col gap-6">
        <blockquote className="rounded-xl border border-zinc-200 bg-zinc-50 p-6 text-lg italic leading-relaxed text-zinc-700 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-300">
          "{metadata.text}"
        </blockquote>
        <DetailMetadataList items={[{ label: "Título", value: metadata.title }, { label: "Artista", value: metadata.artist }, { label: "ID de fragmento", value: result.id }]} />
      </div>
    );
  } else if (modality === "audio") {
    body = (
      <div className="flex flex-col gap-6">
        <DetailAudioPlayer src={metadata.audio_url} />
        <DetailMetadataList
          items={[
            { label: "Título", value: metadata.title },
            { label: "Artista", value: metadata.artist },
            { label: "Álbum", value: metadata.album },
            { label: "Duración", value: formatDuration(metadata.duration_seconds) },
            { label: "Archivo", value: metadata.filename },
          ]}
        />
      </div>
    );
  } else if (modality === "image") {
    body = (
      <div className="flex flex-col gap-6 sm:flex-row">
        <DetailImagePreview src={getImageRenderUrl(result.id)} alt={metadata.nombre_archivo} />
        <div className="flex-1">
          <DetailMetadataList
            items={[
              { label: "Nombre de archivo", value: metadata.nombre_archivo },
              { label: "ID", value: result.id },
              { label: "Ruta en servidor", value: metadata.ruta_original, muted: true },
            ]}
          />
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl px-6 py-12">
      <DetailHeader title={title} datasetType={result.dataset_type} score={result.score} />
      {body}
    </div>
  );
}
