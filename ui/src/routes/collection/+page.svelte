<script lang="ts">
    import type { PageProps } from "./$types";
    let { data }: PageProps = $props();

    import { sortCard } from "$lib/state.svelte";
</script>

<div class="px-10 pt-10">
    <div>
        Total cards: {data.collection.length}
    </div>
    <div>
        Total value maybe: {data.collection
            .reduce((acc, c) => acc + parseFloat(c.price), 0.0)
            .toFixed(2)} €
    </div>
</div>

<div class="p-10 flex flex-wrap gap-5">
    {#each data.collection.sort((a, b) => parseFloat(b.price) - parseFloat(a.price)) as card}
        <div class="w-[200px]">
            <img src={card.image} alt="" class="rounded-lg" />
            <div>
                <a href={card.link} target="_blank">{card.name}</a>
                <p>{sortCard(card)}</p>
                <p>{card.price}€</p>
            </div>
        </div>
    {/each}
</div>
