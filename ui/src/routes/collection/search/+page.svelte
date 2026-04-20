<script lang="ts">
    import type { PageProps } from "./$types";
    let { data }: PageProps = $props();
    let { id_to_card, names, ids } = data;

    import { sortCard } from "$lib/state.svelte";

    let query = $state("");
    let searchResults: string[] = $state([]);

    const search = () => {
        let normalized = query.trim().toLowerCase();

        if (normalized === "") {
            searchResults = [];
            return;
        }

        const exact: string[] = [];
        const prefix: string[] = [];
        const substring: string[] = [];

        for (let i = 0; i < names.length; i++) {
            let name = names[i];
            let id = ids[i];

            if (name === normalized) exact.push(id);
            if (name.startsWith(normalized)) prefix.push(id);
            if (name.includes(normalized)) substring.push(id);
        }

        let unique = new Set([...exact, ...prefix, ...substring]);

        searchResults = Array.from(unique);
    };
</script>

<input
    bind:value={query}
    oninput={search}
    placeholder={'Search e.g. "Black Lotus" or "Chrome Mox"'}
    class="border-2 border-neutral-600 border-dashed bg-neutral-800 p-4 mx-4 mt-4 md:mx-10 md:mt-10 w-[calc(100%-2rem)] md:w-lg outline-0 rounded-lg box-border"
/>

{#if searchResults.length > 0}
    <div class="px-4 md:px-10">
        <div class="mt-2 mb-5 opacity-60">
            Found {searchResults.length} matches
        </div>
        <div class="flex flex-wrap gap-3 md:gap-4">
            {#each searchResults as id}
                {@const card = id_to_card[id]}
                <a href={card.link} target="_blank" class="w-[calc(50%-6px)] md:w-[200px]">
                    <img src={card.image} alt="" class=" rounded-lg" />
                    <p>{card.name}</p>
                    <p>{card.price} €</p>
                    <p>{sortCard(card)}</p>
                </a>
            {/each}
        </div>
    </div>
{/if}

{#if searchResults.length === 0}
    <div class="p-4 md:p-10 italic opacity-60">Literally nothing to see here...</div>
{/if}
