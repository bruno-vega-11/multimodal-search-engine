import MetricBadge from "../ui/Badge";

export default function MetricsBar({ metrics }) {
  if (!metrics) return null;

  const accesosDisco = (metrics.accesos_lectura_disco ?? 0) + (metrics.accesos_escritura_disco ?? 0);

  return (
    <div className="flex flex-wrap gap-2">
      <MetricBadge label="Latencia" value={`${metrics.latencia_ms} ms`} tone="accent" />
      <MetricBadge label="Memoria usada" value={`${metrics.memoria_usada_mb} MB`} />
      <MetricBadge label="Memoria proceso" value={`${metrics.memoria_proceso_mb} MB`} />
      <MetricBadge label="Throughput" value={`${metrics.throughput_consultas_seg} q/s`} tone="success" />
      <MetricBadge label="Accesos a disco" value={accesosDisco} />
    </div>
  );
}
