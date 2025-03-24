<script lang="ts">
	export let tactics: string[] = [];
	export let onSelectTactic: (tactic: string) => void;
</script>

<div class="grid grid-cols-2 gap-4 w-full mt-4 mb-4">
	{#each tactics as tactic}
		<button
			class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-colors"
			on:click={() => onSelectTactic(tactic)}
		>
			{tactic}
		</button>
	{/each}
</div>
