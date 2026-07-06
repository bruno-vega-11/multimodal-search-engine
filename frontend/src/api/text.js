import { API_URL, parseMetrics, parseErrorDetail } from "./client";

export async function searchText(queryText, topK = 5) {
  const formData = new FormData();
  formData.append("query_text", queryText);

  const response = await fetch(`${API_URL}/search/text?top_k=${topK}`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error(await parseErrorDetail(response));
  }

  const data = await response.json();
  return { data, metrics: parseMetrics(response) };
}
