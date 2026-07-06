import { AudioLines } from "lucide-react";
import Dropzone from "../ui/Dropzone";
import { MODALITY_META, MODALITIES } from "../../lib/constants";

export default function AudioSearchInput({ file, onFile }) {
  return (
    <Dropzone
      accept={MODALITY_META[MODALITIES.AUDIO].accept}
      onFile={onFile}
      icon={<AudioLines className="size-5" />}
      hint="Arrastra un archivo .mp3/.wav/.ogg o haz clic para seleccionarlo"
      fileName={file?.name}
    />
  );
}
