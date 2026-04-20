<script lang="ts">
    import {
        uploadImage,
        findSimilar,
        putMatch,
        getCards,
        makeTmpImageUrl,
        listQueue,
        dequeue,
        makeObjectUrl,
        newSession,
    } from "$lib";
    import { appState, type Upload, type Candidate } from "$lib/state.svelte";
    import { goto } from "$app/navigation";

    import type { PageProps } from "./$types";
    let { data }: PageProps = $props();

    let files = $state<File[]>([]);

    let uploadIndex = $state(0);
    let cardIndex = $state(0);

    let queue = $state(data.queue);
    let reviewingQueue = $state(false);

    appState.sessionId = data.sessionId;

    const refreshQueue = async () => {
        queue = await listQueue();
    };

    let numOfNewCards = $derived(
        appState.uploads.reduce(
            (acc, cur) =>
                acc +
                cur.matches.filter((c) => c.status === "CONFIRMED").length,
            0,
        ),
    );

    const processUpload = async (upload: Upload) => {
        const similar = await findSimilar(upload.id);

        if (similar.length === 0) return;

        const allIds = similar.flatMap((row) => row.matches.map((m) => m.id));
        const allCards = await getCards(allIds);
        const cardsById = Object.fromEntries(
            allCards.map((c) => [c.id, c]),
        );

        const candidates: Candidate[] = similar.map((row) => ({
            cards: row.matches.map((match) => ({
                ...match,
                ...cardsById[match.id],
            })),
            img: makeTmpImageUrl(row.img),
            status: "WAITING",
            matchId: null,
        }));

        upload.matches.push(...candidates);
        appState.uploads.push(upload);
    };

    const onFiles = (event: Event) => {
        const target = event.target as HTMLInputElement;
        files = Array.from(target.files || []);
    };

    const handleSubmit = async () => {
        if (files.length === 0) return;

        const tmpFiles = [...files];
        files = [];

        for (const file of tmpFiles) {
            const upload: Upload = {
                id: await uploadImage(file),
                objectURL: URL.createObjectURL(file),
                matches: [],
                active: 0,
            };

            await processUpload(upload);
        }
    };

    const handleReviewQueue = async () => {
        if (queue.length === 0) return;
        reviewingQueue = true;

        try {
            for (const item of queue) {
                const upload: Upload = {
                    id: item.object_id,
                    objectURL: makeObjectUrl(item.object_id),
                    matches: [],
                    active: 0,
                };

                await processUpload(upload);
                await dequeue(item.id);
            }
        } finally {
            await refreshQueue();
            reviewingQueue = false;
        }
    };

    const handleComplete = async () => {
        const currentSession = appState.sessionId;

        for (const upload of appState.uploads) {
            for (const candidate of upload.matches) {
                if (candidate.matchId) {
                    await putMatch(
                        candidate.matchId,
                        upload.id,
                        appState.sessionId,
                    );
                }
            }
        }

        // Reset session
        appState.sessionId = await newSession();
        appState.uploads = [];

        // Navigate to report
        goto(`/sort/${currentSession}`);
    };

    const renderScore = (score: number): string => {
        if (score < 15) return "Great match";
        if (score < 25) return "Good match";
        if (score < 35) return "Weak match";
        return "Probably incorrect";
    };
</script>

<main class="m-4 flex flex-col gap-6 md:gap-10">
    <div class="flex flex-col gap-4 md:flex-row md:gap-10 md:justify-between md:items-center">
        <div>
            <h2 class="font-mono text-sm mb-3 md:mb-5">
                SESSION: {appState.sessionId}
            </h2>

            <div class="flex flex-wrap gap-3 items-center">
                <label
                    class="flex justify-center items-center h-24 w-full md:h-28 md:w-68 border-2 border-neutral-600 border-dashed rounded-lg cursor-pointer bg-neutral-800 hover:bg-neutral-700"
                >
                    <input
                        type="file"
                        multiple
                        accept="image/*"
                        onchange={onFiles}
                        class="hidden"
                    />
                    <div class="text-center">
                        <p>Drag & drop or click</p>
                        {#if files.length}
                            <p class="italic opacity-60">
                                Selected {files.length}
                                {files.length === 1 ? "image" : "images"}
                            </p>
                        {/if}
                    </div>
                </label>
                <button
                    class="bg-neutral-800 hover:bg-neutral-700 disabled:bg-neutral-600 p-2 rounded"
                    onclick={handleSubmit}
                    disabled={files.length === 0}
                >
                    Upload images
                </button>
                <button
                    class="bg-neutral-800 hover:bg-neutral-700 disabled:bg-neutral-600 p-2 rounded"
                    onclick={handleReviewQueue}
                    disabled={queue.length === 0 || reviewingQueue}
                >
                    {reviewingQueue
                        ? "Processing..."
                        : `Review queue (${queue.length})`}
                </button>
            </div>
        </div>

        <div class="flex gap-4">
            <a
                href="/collection"
                class="border-2 border-neutral-600 bg-neutral-800 hover:bg-neutral-700 py-2 px-4 rounded-lg inline-block"
            >
                Collection
            </a>
            <a
                href="/collection/search"
                class="border-2 border-neutral-600 bg-neutral-800 hover:bg-neutral-700 py-2 px-4 rounded-lg inline-block"
            >
                Search
            </a>
        </div>

        <div>
            <button
                class="w-full md:w-auto text-xl bg-neutral-800 hover:bg-neutral-700 disabled:bg-neutral-600 py-5 px-10 rounded"
                disabled={numOfNewCards === 0}
                onclick={handleComplete}
            >
                <div>Complete & sort</div>
                <div>{numOfNewCards} new cards</div>
            </button>
        </div>
    </div>

    <div>
        Previous sessions
        <div class="flex gap-2 flex-wrap font-mono mt-2">
            {#each data.sessions as session}
                <div>
                    <a
                        href={`/sort/${session}`}
                        class="border-2 border-neutral-600 border-dashed bg-neutral-800 hover:bg-neutral-700 py-1 px-2 rounded-lg inline-block"
                    >
                        {session.slice(0, 8)}
                    </a>
                </div>
            {/each}
        </div>
    </div>

    {#if uploadIndex <= appState.uploads.length - 1}
        {@const upload = appState.uploads[uploadIndex]}
        {@const match = upload.matches[upload.active]}
        {@const card = match?.cards[cardIndex]}

        <div class="flex flex-col gap-10">
            <div class="flex flex-col">
                {#if card}
                    <div class="flex flex-col md:flex-row gap-4 md:gap-10 mb-6 md:mb-10">
                        <div class="flex gap-4 md:gap-10">
                            <img
                                src={card.image}
                                alt=""
                                class="w-[140px] md:w-[300px] border-4 border-sky-500 border-dashed rounded-2xl"
                            />
                            <img
                                src={match.img}
                                alt=""
                                class="w-[140px] md:w-[300px] border-4 border-rose-500 border-dashed rounded-2xl"
                            />
                        </div>
                        <div>
                            <div class="mb-4 md:mb-10 text-lg md:text-2xl">
                                <div>{card.name}</div>
                                <div>{card.set_name} ({card.set})</div>
                                <div>
                                    {renderScore(card.score)} ({card.score.toFixed(
                                        4,
                                    )})
                                </div>
                                <div class="mt-2 md:mt-4 text-sm md:text-base font-mono">
                                    PRICE: {card.price}€ RANK: {card.edhrec}
                                </div>
                            </div>
                            <div class="flex text-lg md:text-xl gap-3 md:gap-5 items-center">
                                <button
                                    class="bg-neutral-800 hover:bg-neutral-700 py-2 px-4 md:py-3 md:px-6 rounded"
                                    onclick={() => {
                                        match.status = "CONFIRMED";
                                        match.matchId = card.id;
                                        upload.active += 1;
                                        cardIndex = 0;
                                    }}
                                >
                                    Confirm
                                </button>
                                <button
                                    class="bg-neutral-800 hover:bg-neutral-700 py-2 px-4 md:py-3 md:px-6 rounded"
                                    onclick={() => {
                                        match.status = "DISCARDED";
                                        upload.active += 1;
                                        cardIndex = 0;
                                    }}
                                >
                                    Discard
                                </button>
                                <span>
                                    {upload.active + 1} /
                                    {upload.matches.length}
                                </span>
                            </div>
                            <a
                                href={card.link}
                                target="_blank"
                                class="bg-neutral-800 hover:bg-neutral-700 p-2 my-4 rounded inline-block"
                            >
                                Open in Scryfall
                            </a>
                        </div>
                    </div>
                {:else}
                    <div class="text-2xl">All done!</div>
                {/if}

                {#if card}
                    <div class="flex flex-wrap gap-1">
                        {#each match.cards as card, index}
                            <button onclick={() => (cardIndex = index)}>
                                <img
                                    src={card.image}
                                    alt=""
                                    class="max-w-[100px] md:max-w-[200px] rounded-xl hover:opacity-50 cursor-pointer"
                                />
                            </button>
                        {/each}
                    </div>
                {/if}
            </div>

            <div class="flex flex-col md:flex-row gap-4">
                <div class="w-full md:w-[600px] mb-4">
                    <img
                        src={upload.objectURL}
                        alt=""
                        class="max-w-full max-h-full"
                    />
                </div>
                <div class="flex flex-col gap-5">
                    <h2 class="font-mono text-sm">UPLOAD: {upload.id}</h2>
                    <div>
                        <button
                            class="w-24 bg-neutral-800 hover:bg-neutral-700 disabled:bg-neutral-600 p-2 rounded"
                            onclick={() => {
                                if (uploadIndex - 1 >= 0) {
                                    uploadIndex -= 1;
                                    cardIndex = 0;
                                }
                            }}
                            disabled={uploadIndex - 1 < 0}
                        >
                            Previous
                        </button>
                        <button
                            class="w-24 bg-neutral-800 hover:bg-neutral-700 disabled:bg-neutral-600 p-2 rounded"
                            onclick={() => {
                                if (
                                    uploadIndex + 1 <=
                                    appState.uploads.length - 1
                                ) {
                                    uploadIndex += 1;
                                    cardIndex = 0;
                                }
                            }}
                            disabled={uploadIndex + 1 >=
                                appState.uploads.length}
                        >
                            Next
                        </button>
                    </div>
                </div>
            </div>
        </div>
    {/if}
</main>
