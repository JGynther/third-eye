import type { HandleFetch } from "@sveltejs/kit";

export const handleFetch: HandleFetch = ({ request, fetch }) => {
  const url = new URL(request.url);

  if (url.pathname.startsWith("/api")) {
    url.host = "localhost:8001";
    url.protocol = "http:";
    url.pathname = url.pathname.slice(4);
    return fetch(new Request(url, request));
  }

  return fetch(request);
};
