<script lang="ts">
    import {
        uploadImage,
        findSimilar,
        putMatch,
        getCards,
        makeTmpImageUrl,
    } from "$lib";
    import { appState, type Upload, type Candidate } from "$lib/state.svelte";
    import { goto } from "$app/navigation";

    import type { PageProps } from "./$types";
    let { data }: PageProps = $props();

    let files = $state<File[]>([]);

    let uploadIndex = $state(0);
    let cardIndex = $state(0);

    let numOfNewCards = $derived(
        appState.uploads.reduce(
            (acc, cur) =>
                acc +
                cur.matches.filter((c) => c.status === "CONFIRMED").length,
            0,
        ),
    );

    const onFiles = (event: Event) => {
        const target = event.target as HTMLInputElement;
        files = Array.from(target.files || []);
    };

    const handleSubmit = async () => {
        if (files.length === 0) return;

        for (const file of files) {
            const upload: Upload = {
                id: await uploadImage(file),
                file: file,
                objectURL: URL.createObjectURL(file),
                matches: [],
                active: 0,
            };

            const similar = await findSimilar(upload.id);

            const candidates: Candidate[] = await Promise.all(
                similar.map(async (row) => {
                    const cards = await getCards(row.matches.map((m) => m.id));
                    return {
                        cards: row.matches.map((match, i) => ({
                            ...match,
                            ...cards[i],
                        })),
                        img: makeTmpImageUrl(row.img),
                        status: "WAITING",
                        matchId: null,
                    };
                }),
            );

            upload.matches.push(...candidates);
            appState.uploads.push(upload);
        }

        files = [];
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
        appState.sessionId = crypto.randomUUID();
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

<main class="m-5 flex flex-col gap-10">
    <div class="flex gap-10 justify-between items-center">
        <div>
            <h2 class="font-mono text-sm mb-5">
                SESSION: {appState.sessionId}
            </h2>

            <div class="flex gap-4 items-center">
                <label
                    class="flex justify-center items-center h-28 w-68 border-2 border-neutral-600 border-dashed rounded-lg cursor-pointer bg-neutral-800 hover:bg-neutral-700"
                >
                    <input
                        type="file"
                        multiple
                        accept="image/*"
                        onchange={onFiles}
                        class="hidden"
                    />
                    Drag & drop or click
                </label>
                <button
                    class="bg-neutral-800 hover:bg-neutral-700 disabled:bg-neutral-600 p-2 rounded"
                    onclick={handleSubmit}
                    disabled={files.length === 0}
                >
                    Upload images
                </button>
            </div>
        </div>

        <div>
            <a
                href="/collection"
                class="border-2 border-neutral-600 bg-neutral-800 hover:bg-neutral-700 py-2 px-4 rounded-lg inline-block"
                >Collection</a
            >
        </div>

        <div>
            <button
                class="text-xl bg-neutral-800 hover:bg-neutral-700 disabled:bg-neutral-600 py-5 px-10 rounded"
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
                    <div class="flex gap-10 mb-10">
                        <img
                            src={card.image}
                            alt=""
                            class="w-[300px] border-4 border-sky-500 border-dashed rounded-2xl"
                        />
                        <img
                            src={match.img}
                            alt=""
                            class="w-[300px] border-4 border-rose-500 border-dashed rounded-2xl"
                        />
                        <div>
                            <div class="mb-10 text-2xl">
                                <div>{card.name}</div>
                                <div>{card.set_name} ({card.set})</div>
                                <div>
                                    {renderScore(card.score)} ({card.score.toFixed(
                                        4,
                                    )})
                                </div>
                                <div class="mt-4 text-base font-mono">
                                    PRICE: {card.price}€ RANK: {card.edhrec}
                                </div>
                            </div>
                            <div class="flex text-xl gap-5 items-center">
                                <button
                                    class="bg-neutral-800 hover:bg-neutral-700 py-3 px-6 rounded"
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
                                    class="bg-neutral-800 hover:bg-neutral-700 py-3 px-6 rounded"
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
                                    class="max-w-[200px] rounded-xl hover:opacity-50 cursor-pointer"
                                />
                            </button>
                        {/each}
                    </div>
                {/if}
            </div>

            <div class="flex gap-4">
                <div class="w-[600px] mb-4">
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
