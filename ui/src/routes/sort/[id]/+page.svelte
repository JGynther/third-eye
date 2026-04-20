<script lang="ts">
    import type { PageProps } from "./$types";
    let { data }: PageProps = $props();

    import { sortCard } from "$lib/state.svelte";
</script>

<div class="grid">
    {#each Object.values(data.grouped).reverse() as cards}
        <div class="p-4 md:p-10 flex flex-wrap gap-3 md:gap-5">
            {#each cards as card}
                <div class="w-[calc(50%-6px)] md:w-auto">
                    <img src={card.image} alt="" class="w-full md:w-[240px] rounded-xl" />
                    {sortCard(card)}
                    RANK: {card.edhrec ? card.edhrec : "NONE"}
                    PRICE: {parseFloat(card.price).toFixed(2)}€
                </div>
            {/each}
        </div>
    {/each}
</div>
