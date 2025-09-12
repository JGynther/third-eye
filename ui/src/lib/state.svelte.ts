type Card = {
  id: string;
  score: number;
  name: string;
  link: string;
  set: string;
  set_name: string;
  image: string;
  price: string;
  edhrec: string;
};

type Candidate = {
  cards: Card[];
  img: string;
  status: "CONFIRMED" | "DISCARDED" | "WAITING";
  matchId: string | null;
};

type Upload = {
  id: string;
  file: File;
  objectURL: string;
  matches: Candidate[];
  active: number;
};

type AppState = {
  sessionId: string;
  uploads: Upload[];
};

const appState = $state<AppState>({
  sessionId: crypto.randomUUID(),
  uploads: [],
});

type Category = "BULK" | "EDH" | "SLEEVE" | "BINDER";

const sortCard = (card: Card): Category => {
  const price = parseFloat(card.price);
  const rank = parseInt(card.edhrec);

  if (price > 0.98) {
    if (price > 10) return "BINDER";
    return "SLEEVE";
  }

  if (rank !== 0 && rank < 2000) return "EDH";

  // Else bulk
  return "BULK";
};

export { appState, sortCard };
export type { Card, Candidate, Upload };
