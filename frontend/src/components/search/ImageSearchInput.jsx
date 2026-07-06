import { Image as ImageIcon } from "lucide-react";
import Dropzone from "../ui/Dropzone";
import { useObjectUrl } from "../../hooks/useObjectUrl";
import { MODALITY_META, MODALITIES } from "../../lib/constants";

export default function ImageSearchInput({ file, onFile }) {
  const [previewUrl, setPreviewUrl] = useObjectUrl();

  function handleFile(selected) {
    setPreviewUrl(selected);
    onFile(selected);
  }

  return (
    <Dropzone
      accept={MODALITY_META[MODALITIES.IMAGEN].accept}
      onFile={handleFile}
      icon={<ImageIcon className="size-5" />}
      hint="Arrastra una imagen .jpg/.png/.webp o haz clic para seleccionarla"
      fileName={file?.name}
      preview={previewUrl}
    />
  );
}
