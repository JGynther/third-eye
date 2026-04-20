import type { PageLoad } from "./$types";
import { listSessions, listQueue, newSession } from "$lib";

const load: PageLoad = async ({ fetch }) => {
  const [sessions, queue, sessionId] = await Promise.all([
    listSessions(fetch),
    listQueue(fetch),
    newSession(fetch),
  ]);
  return { sessions: sessions.map(([session]: string[]) => session), queue, sessionId };
};

export { load };
