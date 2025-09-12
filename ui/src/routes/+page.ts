import type { PageLoad } from "./$types";
import { listSessions } from "$lib";

const load: PageLoad = async () => {
  const sessions: string[][] = await listSessions();
  return { sessions: sessions.map(([session]) => session) };
};

export { load };
