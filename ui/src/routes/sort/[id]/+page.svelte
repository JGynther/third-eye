<script lang="ts">
    import type { PageProps } from "./$types";
    let { data }: PageProps = $props();

    import { sortCard } from "$lib/state.svelte";
</script>

<div class="grid">
    {#each Object.values(data.grouped) as cards}
        <div class="p-10 flex flex-wrap gap-5">
            {#each cards as card}
                <div>
                    <img src={card.image} alt="" class="w-[240px] rounded-xl" />
                    {sortCard(card)}
                    RANK: {card.edhrec ? card.edhrec : "NONE"}
                    PRICE: {parseFloat(card.price).toFixed(2)}€
                </div>
            {/each}
        </div>
    {/each}
</div>
