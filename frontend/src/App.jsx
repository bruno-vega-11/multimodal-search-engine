import { BrowserRouter, Routes, Route, useLocation } from "react-router-dom";
import { AnimatePresence } from "framer-motion";
import { ThemeProvider } from "./context/ThemeContext";
import { SearchProvider } from "./context/SearchContext";
import Navbar from "./components/ui/Navbar";
import PageTransition from "./components/ui/PageTransition";
import Landing from "./routes/Landing";
import Search from "./routes/Search";
import Results from "./routes/Results";
import Detail from "./routes/Detail";
import NotFound from "./routes/NotFound";

function AnimatedRoutes() {
  const location = useLocation();

  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        <Route path="/" element={<PageTransition><Landing /></PageTransition>} />
        <Route path="/search" element={<PageTransition><Search /></PageTransition>} />
        <Route path="/results" element={<PageTransition><Results /></PageTransition>} />
        <Route path="/results/:modality/:id" element={<PageTransition><Detail /></PageTransition>} />
        <Route path="*" element={<PageTransition><NotFound /></PageTransition>} />
      </Routes>
    </AnimatePresence>
  );
}

export default function App() {
  return (
    <ThemeProvider>
      <SearchProvider>
        <BrowserRouter>
          <div className="min-h-screen bg-white dark:bg-zinc-950">
            <Navbar />
            <AnimatedRoutes />
          </div>
        </BrowserRouter>
      </SearchProvider>
    </ThemeProvider>
  );
}
