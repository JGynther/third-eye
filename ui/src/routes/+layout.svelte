<script lang="ts">
    import { page } from "$app/state";
    import "../app.css";
    let { children } = $props();
</script>

<div class="flex flex-col min-h-screen">
    <nav class="flex gap-4 p-4 bg-neutral-900 text-sm text-neutral-400">
        {#each [
            { href: "/", label: "Review" },
            { href: "/capture", label: "Capture" },
            { href: "/collection", label: "Collection" },
            { href: "/collection/search", label: "Search" },
        ] as { href, label }}
            <a {href} class="hover:text-white" class:text-white={page.url.pathname === href}>
                {label}
            </a>
        {/each}
    </nav>

    {@render children?.()}
</div>
