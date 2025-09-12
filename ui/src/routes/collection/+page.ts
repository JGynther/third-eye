import type { PageLoad } from "./$types";
import { getCollection } from "$lib";
import type { Card } from "$lib/state.svelte";

const load: PageLoad = async () => {
  const collection: Card[] = await getCollection();
  return { collection };
};

export { load };
