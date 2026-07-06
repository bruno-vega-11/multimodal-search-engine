import { useNavigate } from "react-router-dom";
import { Compass } from "lucide-react";
import EmptyState from "../components/ui/EmptyState";
import Button from "../components/ui/Button";
import { ROUTES } from "../lib/constants";

export default function NotFound() {
  const navigate = useNavigate();
  return (
    <div className="mx-auto max-w-2xl px-6 py-24">
      <EmptyState
        icon={<Compass className="size-6" />}
        title="Página no encontrada"
        description="La ruta que buscas no existe."
        action={<Button onClick={() => navigate(ROUTES.HOME)}>Volver al inicio</Button>}
      />
    </div>
  );
}
