import { useEffect, useRef, useState } from "react";

export function useObjectUrl() {
  const [url, setUrl] = useState(null);
  const previous = useRef(null);

  useEffect(() => {
    return () => {
      if (previous.current) URL.revokeObjectURL(previous.current);
    };
  }, []);

  function set(file) {
    if (previous.current) URL.revokeObjectURL(previous.current);
    if (!file) {
      previous.current = null;
      setUrl(null);
      return;
    }
    const next = URL.createObjectURL(file);
    previous.current = next;
    setUrl(next);
  }

  return [url, set];
}
