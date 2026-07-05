import os
import time

import psutil


class MetricsTracker:
    """Mide latencia, memoria y accesos a disco de un bloque de codigo.

    Uso:
        with MetricsTracker() as m:
            hacer_algo()
        print(m.result)
    """

    def __init__(self):
        self._process = psutil.Process(os.getpid())
        self.result = None

    def __enter__(self):
        self._t0 = time.perf_counter()
        self._mem0 = self._process.memory_info().rss
        self._io0 = self._process.io_counters()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        elapsed_ms = (time.perf_counter() - self._t0) * 1000
        mem1 = self._process.memory_info().rss
        io1 = self._process.io_counters()

        self.result = {
            "latencia_ms": round(elapsed_ms, 3),
            "memoria_proceso_mb": round(mem1 / 1024 / 1024, 3),
            "memoria_usada_mb": round((mem1 - self._mem0) / 1024 / 1024, 3),
            "accesos_lectura_disco": io1.read_count - self._io0.read_count,
            "accesos_escritura_disco": io1.write_count - self._io0.write_count,
            "bytes_leidos_disco": io1.read_bytes - self._io0.read_bytes,
            "bytes_escritos_disco": io1.write_bytes - self._io0.write_bytes,
        }
        return False
