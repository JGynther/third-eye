<script lang="ts">
    import { detectImage, queueById, listQueue } from "$lib";
    import type { PageProps } from "./$types";

    let { data }: PageProps = $props();

    let queued = $state(data.queued);
    let status = $state<string | null>(null);
    let rejected = $state(false);

    const refreshCount = async () => {
        const items = await listQueue();
        queued = items.length;
    };

    const handleCapture = async (event: Event) => {
        const input = event.target as HTMLInputElement;
        const file = input.files?.[0];
        if (!file) return;

        rejected = false;
        status = "Detecting...";
        const { object_id, count } = await detectImage(file);

        if (count === 0) {
            status = null;
            rejected = true;
            input.value = "";
            return;
        }

        status = "Queueing...";
        await queueById(object_id);
        input.value = "";
        status = null;
        await refreshCount();
    };
</script>

<main class="flex flex-col items-center justify-center flex-1 p-4 gap-8">
    <div class="text-4xl font-mono">{queued} in queue</div>

    <label
        class="flex items-center justify-center w-64 h-64 border-4 border-dashed rounded-2xl cursor-pointer bg-neutral-800 active:bg-neutral-700 text-2xl"
        class:border-red-500={rejected}
        class:border-neutral-600={!rejected}
        class:opacity-50={!!status}
    >
        <input
            type="file"
            accept="image/*"
            capture="environment"
            onchange={handleCapture}
            disabled={!!status}
            class="hidden"
        />
        {status ?? "Take photo"}
    </label>

    {#if rejected}
        <div class="text-red-400 text-lg">No cards detected</div>
    {/if}

</main>
