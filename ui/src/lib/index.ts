type QueueItem = { id: number; object_id: string; created_at: string };

const postFile = async (endpoint: string, file: File) => {
  const form = new FormData();
  form.append("image", file);

  const response = await fetch(`/api${endpoint}`, {
    method: "POST",
    body: form,
  });

  return response.json();
};

const uploadImage = async (file: File): Promise<string> => {
  return postFile("/upload-image", file);
};

const findSimilar = async (
  id: string,
): Promise<{ img: string; matches: { id: string; score: number }[] }[]> => {
  const response = await fetch(`/api/similar-from-image/${id}`);
  return response.json();
};

const putMatch = async (id: string, src: string, session: string) => {
  const params = new URLSearchParams({ id, src, session });
  const response = await fetch(`/api/match?${params}`, { method: "PUT" });
  return response.json();
};

const getCards = async (ids: string[], f = fetch) => {
  const query = ids.map((id) => `ids=${id}`).join("&");
  const response = await f(`/api/cards?${query}`);
  if (!response.ok) return [];
  return response.json();
};

const loadSession = async (id: string, f = fetch) => {
  const response = await f(`/api/session/${id}`);
  return response.json();
};

const listSessions = async (f = fetch) => {
  const response = await f(`/api/sessions`);
  return response.json();
};

const makeTmpImageUrl = (image: string) =>
  `/api/tmp/images/${image.slice(5)}`;

const getCollection = async (f = fetch) => {
  const response = await f(`/api/collection`);
  return response.json();
};

const detectImage = async (
  file: File,
): Promise<{ object_id: string; count: number }> => {
  return postFile("/detect", file);
};

const queueById = async (objectId: string) => {
  await fetch(`/api/queue/${objectId}`, { method: "POST" });
};

const listQueue = async (f = fetch): Promise<QueueItem[]> => {
  const response = await f(`/api/queue`);
  return response.json();
};

const dequeue = async (id: number) => {
  await fetch(`/api/queue/${id}`, { method: "DELETE" });
};

const makeObjectUrl = (id: string) => `/api/objects/${id}`;

const newSession = async (f = fetch): Promise<string> => {
  const response = await f("/api/new-session", { method: "POST" });
  return response.json();
};

export type { QueueItem };
export {
  uploadImage,
  findSimilar,
  putMatch,
  getCards,
  loadSession,
  listSessions,
  makeTmpImageUrl,
  getCollection,
  detectImage,
  queueById,
  listQueue,
  dequeue,
  makeObjectUrl,
  newSession,
};
