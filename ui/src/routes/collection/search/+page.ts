import type { PageLoad } from "./$types";
import { getCollection } from "$lib";
import type { Card } from "$lib/state.svelte";

const load: PageLoad = async () => {
  const collection: Card[] = await getCollection();
  const id_to_card: Record<string, Card> = Object.fromEntries(
    collection.map((c) => [c.id, c]),
  );

  const names = collection.map((c) => c.name.toLowerCase());
  const ids = collection.map((c) => c.id);

  return { id_to_card, names, ids };
};

export { load };
