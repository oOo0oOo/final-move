<script lang="ts">
	import { onMount } from 'svelte';
	import Goal from './Goal.svelte';
	import Tactics from './Tactics.svelte';

	export let onNotification: (message: string) => void;

	let score = 0;
	let currentTier = 0;
	let gameData: any = [];
	let tactics: string[] = [];
	let availableGoals: any[] = [];
	let currentGoal: any[] = [];
	let nextTierCost = 0;
	let nextTierTactics = '';
	let loading = true;
	let baseUrl: string = '';
	let goalComponent: any;

	onMount(async () => {
		try {
			const response = await fetch('/data.json');
			let data = await response.json();
			baseUrl = data.mathlib_url;
			gameData = data.tiers;
			setTier(0);
			loading = false;
		} catch (error) {
			console.error('Failed to load game data:', error);
			onNotification('Error loading data');
		}
	});

	function setTier(tier: number) {
		currentTier = tier;
		tactics = [];
		availableGoals = [];

		// Collect all tactics and goals up to the current tier
		for (let i = 0; i <= currentTier; i++) {
			const tierData = gameData[i];
			if (tierData) {
				// Add all tactics from this tier
				tierData.tactics.forEach((tactic: any) => {
					if (!tactics.includes(tactic)) {
						tactics.push(tactic);
					}
				});

				// Add all goals from this tier
				tierData.goals.forEach((goal: string) => {
					availableGoals.push(goal);
				});
			}
		}

		updateUnlockInfo();
		setNewGoal();
	}

	function setNewGoal() {
		if (availableGoals.length === 0) return;
		currentGoal = availableGoals[Math.floor(Math.random() * availableGoals.length)];

		// Use timeout to allow Goal component to be ready
		setTimeout(() => {
			if (goalComponent) {
				goalComponent.setGoal(currentGoal);
			}
		}, 0);
		console.log(currentGoal[3]);
	}

	function updateUnlockInfo() {
		if (gameData[currentTier + 1]) {
			nextTierCost = gameData[currentTier + 1].cost;
			nextTierTactics = gameData[currentTier + 1].tactics.join(', ');
		} else {
			nextTierCost = 0;
			nextTierTactics = '';
		}
	}

	function handleTactic(tactic: string) {
		if (currentGoal[3].includes(tactic)) {
			score += 2;
			onNotification('👍');
			setNewGoal();
		} else {
			score -= 1;
			onNotification('👎');
		}
	}

	function unlockNewTier() {
		if (score >= nextTierCost) {
			score -= nextTierCost;
			setTier(currentTier + 1);
		} else {
			onNotification(`Missing ${nextTierCost - score} ⚡`);
		}
	}
</script>

<div
	class="container flex flex-col items-center max-w-3xl w-full mx-auto p-4 bg-white rounded-lg shadow-md"
>
	<div class="w-full flex justify-between items-center">
		<h1 class="text-3xl font-bold mb-4">Final Move</h1>
		<span class="text-3xl font-bold">⚡ {score}</span>
	</div>

	{#if loading}
		<p class="text-center py-6">Loading game data...</p>
	{:else}
		<Goal bind:this={goalComponent} {baseUrl} />

		<Tactics {tactics} onSelectTactic={handleTactic} />

		{#if nextTierCost > 0}
			<div class="mt-4 w-full">
				<button
					on:click={unlockNewTier}
					class="bg-gray-300 text-black px-4 py-2 rounded w-full hover:bg-gray-400"
				>
					Unlock new tactics for {nextTierCost} ⚡: {nextTierTactics}
				</button>
			</div>
		{/if}
	{/if}
</div>

<style>
	.container {
		margin: 2rem;
	}
</style>
