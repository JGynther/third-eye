import type { PageLoad } from "./$types";
import { getCollection } from "$lib";
import type { Card } from "$lib/state.svelte";

const load: PageLoad = async ({ fetch }) => {
  const collection: Card[] = await getCollection(fetch);
  return { collection };
};

export { load };
