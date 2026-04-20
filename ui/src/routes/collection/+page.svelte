<script lang="ts">
    import type { PageProps } from "./$types";
    let { data }: PageProps = $props();

    import { sortCard } from "$lib/state.svelte";
</script>

<div class="px-4 pt-4 md:px-10 md:pt-10">
    <div>
        Total cards: {data.collection.length}
    </div>
    <div>
        Total value maybe: {data.collection
            .reduce((acc, c) => {
                let float = parseFloat(c.price);

                if (float < 0.95) {
                    return acc;
                }

                return acc + float;
            }, 0.0)
            .toFixed(2)} €
    </div>
</div>

<div class="p-4 md:p-10 flex flex-wrap gap-3 md:gap-5">
    {#each data.collection
        .sort((a, b) => parseFloat(b.price) - parseFloat(a.price))
        .slice(0, 250) as card}
        <div class="w-[calc(50%-6px)] md:w-[200px]">
            <a href={card.link} target="_blank">
                <img src={card.image} alt="" class="rounded-lg" />
            </a>
            <div>
                <p>{card.name}</p>
                <p>{sortCard(card)}</p>
                <p>{card.price}€</p>
            </div>
        </div>
    {/each}
</div>
