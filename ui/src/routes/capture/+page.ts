import type { PageLoad } from "./$types";
import { listQueue } from "$lib";

const load: PageLoad = async ({ fetch }) => {
  const queue = await listQueue(fetch);
  return { queued: queue.length };
};

export { load };
