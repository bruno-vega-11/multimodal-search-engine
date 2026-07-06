import { API_URL, parseMetrics, parseErrorDetail } from "./client";

export async function searchImage(file, topK = 5) {
  const formData = new FormData();
  formData.append("query_image", file);

  const response = await fetch(`${API_URL}/search/image?top_k=${topK}`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error(await parseErrorDetail(response));
  }

  const data = await response.json();
  return { data, metrics: parseMetrics(response) };
}

export function getImageRenderUrl(imagenId) {
  return `${API_URL}/imagen/render/${imagenId}`;
}
