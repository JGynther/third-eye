import type { PageLoad } from "./$types";
import { loadSession, getCards } from "$lib";
import type { Card } from "$lib/state.svelte";

type Session = [number, string, string, string][];

const load: PageLoad = async ({ params }) => {
  const session: Session = await loadSession(params.id);
  const ids = session.map(([, id]) => id);
  const cards: Card[] = await getCards(ids);

  const grouped: Record<string, Card[]> = {};

  for (let i = 0; i < session.length; i++) {
    const object_id = session[i][2];
    const card = cards[i];
    if (!grouped[object_id]) grouped[object_id] = [];
    grouped[object_id].push(card);
  }

  return { grouped };
};

export { load };
