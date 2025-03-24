<script lang="ts">
	export let baseUrl: string = '';
	export let goal: any[] = [];

	function confirmNavigation(event: MouseEvent) {
		if (confirm('This is cheating! Are you sure you want to see the solution?')) {
			let url = baseUrl + goal[0] + '#L' + (goal[1] + 1);
			window.open(url, '_blank', 'noopener,noreferrer');
		}
	}
</script>

<div class="mb-4 w-full">
	<pre class="rounded-lg overflow-hidden"><code class="language-lean">{goal[2]}</code></pre>
	<div class="flex justify-end">
		<button class="goal-link" on:click|preventDefault={confirmNavigation}>See in mathlib ↗️</button>
	</div>
</div>

<style>
	pre {
		margin: 0;
		background-color: #f5f5f5;
	}

	code {
		border-radius: 8px;
		padding: 1rem;
		display: block;
		overflow: auto;
	}

	.goal-link {
		margin-top: 5px;
		color: #3182ce;
	}
</style>
