import { API_URL, parseMetrics, parseErrorDetail } from "./client";

export async function searchAudio(file, topK = 5) {
  const formData = new FormData();
  formData.append("query_audio", file);

  const response = await fetch(`${API_URL}/search/audio?top_k=${topK}`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error(await parseErrorDetail(response));
  }

  const data = await response.json();
  return { data, metrics: parseMetrics(response) };
}

export function getAudioStreamUrl(audioId) {
  return `${API_URL}/audio/stream/${audioId}`;
}
