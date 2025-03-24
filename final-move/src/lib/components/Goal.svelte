<script lang="ts">
	import { onMount } from 'svelte';
	import hljs from 'highlight.js';
	import leanHljs from 'highlightjs-lean';

	export let baseUrl: string = '';
	export let goal: any[] = [];

	// Add a key that will change when we want to force a re-render
	let renderKey = 0;

	export function setGoal(newGoal: any[]) {
		goal = newGoal;

		renderKey++;

		setTimeout(() => {
			const code = document.querySelector('code');
			if (code) {
				hljs.highlightElement(code);
			}
		}, 0);
	}

	function confirmNavigation(event: MouseEvent) {
		if (confirm('This is cheating! Are you sure you want to see the solution?')) {
			let url = baseUrl + goal[0] + '#L' + (goal[1] + 1);
			window.open(url, '_blank', 'noopener,noreferrer');
		}
	}

	onMount(async () => {
		try {
			hljs.registerLanguage('lean', leanHljs);
		} catch (error) {
			console.error('Failed to load Lean language highlighting:', error);
		}
	});
</script>

{#key renderKey}
	<div class="mb-4 w-full">
		<pre class="rounded-lg overflow-hidden"><code class="language-lean">{goal[2] || ''}</code></pre>
		<div class="flex justify-end">
			{#if goal.length > 0}
				<button class="goal-link" on:click|preventDefault={confirmNavigation}
					>See in mathlib ↗️</button
				>
			{/if}
		</div>
	</div>
{/key}

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
