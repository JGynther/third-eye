const API_URL = "http://localhost:8001";

const uploadImage = async (file: File): Promise<string> => {
  const form = new FormData();
  form.append("image", file);

  const response = await fetch(`${API_URL}/upload-image`, {
    method: "POST",
    body: form,
  });

  return response.json();
};

const findSimilar = async (
  id: string,
): Promise<{ img: string; matches: { id: string; score: number }[] }[]> => {
  const response = await fetch(`${API_URL}/similar-from-image/${id}`);
  return response.json();
};

const putMatch = async (id: string, src: string, session: string) => {
  const params = new URLSearchParams({ id, src, session });
  const response = await fetch(`${API_URL}/match?${params}`, { method: "PUT" });
  return response.json();
};

const getCards = async (ids: string[]) => {
  const query = ids.map((id) => `ids=${id}`).join("&");
  const response = await fetch(`${API_URL}/cards?${query}`);
  return response.json() || [];
};

const loadSession = async (id: string) => {
  const response = await fetch(`${API_URL}/session/${id}`);
  return response.json();
};

const listSessions = async () => {
  const response = await fetch(`${API_URL}/sessions`);
  return response.json();
};

const makeTmpImageUrl = (image: string) =>
  `${API_URL}/tmp/images/${image.slice(5)}`;

const getCollection = async () => {
  const response = await fetch(`${API_URL}/collection`);
  return response.json();
};

export {
  uploadImage,
  findSimilar,
  putMatch,
  getCards,
  loadSession,
  listSessions,
  makeTmpImageUrl,
  getCollection,
};
