import { Search } from "lucide-react";
import TextField from "../ui/TextField";

export default function TextSearchInput({ value, onChange }) {
  return (
    <div className="relative">
      <Search className="pointer-events-none absolute left-4 top-1/2 size-4 -translate-y-1/2 text-zinc-400" />
      <TextField
        autoFocus
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Escribe una frase o palabras clave..."
        className="h-14 pl-11 text-base"
      />
    </div>
  );
}
