import { Link, NavLink } from "react-router-dom";
import { Search as SearchIcon } from "lucide-react";
import ThemeToggle from "./ThemeToggle";
import { ROUTES } from "../../lib/constants";
import { cn } from "../../lib/utils";

export default function Navbar() {
  return (
    <header className="sticky top-0 z-40 border-b border-zinc-200/80 bg-white/80 backdrop-blur-md dark:border-zinc-800/80 dark:bg-zinc-950/80">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
        <Link to={ROUTES.HOME} className="flex items-center gap-2">
          <div className="flex size-7 items-center justify-center rounded-lg bg-zinc-900 text-white dark:bg-white dark:text-zinc-900">
            <SearchIcon className="size-3.5" />
          </div>
          <span className="text-sm font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
            Multimodal
          </span>
        </Link>

        <nav className="flex items-center gap-1">
          <NavLink
            to={ROUTES.SEARCH}
            className={({ isActive }) =>
              cn(
                "rounded-lg px-3 py-1.5 text-sm font-medium transition-colors",
                isActive
                  ? "text-zinc-900 dark:text-zinc-50"
                  : "text-zinc-500 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-100"
              )
            }
          >
            Buscar
          </NavLink>
          <div className="mx-1 h-4 w-px bg-zinc-200 dark:bg-zinc-800" />
          <ThemeToggle />
        </nav>
      </div>
    </header>
  );
}
