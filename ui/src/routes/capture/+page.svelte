<script lang="ts">
    import { queueImage, listQueue } from "$lib";
    import type { PageProps } from "./$types";

    let { data }: PageProps = $props();

    let queued = $state(data.queued);
    let uploading = $state(false);

    const refreshCount = async () => {
        const items = await listQueue();
        queued = items.length;
    };

    const handleCapture = async (event: Event) => {
        const input = event.target as HTMLInputElement;
        const file = input.files?.[0];
        if (!file) return;

        uploading = true;
        await queueImage(file);
        input.value = "";
        uploading = false;
        await refreshCount();
    };
</script>

<main class="flex flex-col items-center justify-center min-h-screen p-4 gap-8">
    <div class="text-4xl font-mono">{queued} in queue</div>

    <label
        class="flex items-center justify-center w-64 h-64 border-4 border-neutral-600 border-dashed rounded-2xl cursor-pointer bg-neutral-800 active:bg-neutral-700 text-2xl"
        class:opacity-50={uploading}
    >
        <input
            type="file"
            accept="image/*"
            capture="environment"
            onchange={handleCapture}
            disabled={uploading}
            class="hidden"
        />
        {uploading ? "Uploading..." : "Take photo"}
    </label>

    <a href="/" class="text-neutral-400 underline"> Back to review </a>
</main>
