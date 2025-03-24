<script lang="ts">
	import { onMount } from 'svelte';
	import Game from '$lib/components/Game.svelte';
	import Notification from '$lib/components/Notification.svelte';

	let notification = '';
	let showNotification = false;

	function handleNotification(message: string) {
		notification = message;
		showNotification = true;

		setTimeout(() => {
			showNotification = false;
		}, 1200);
	}

	onMount(() => {
		import('highlight.js').then((hljs) => {
			import('highlightjs-lean').then(() => {
				hljs.default.highlightAll();
			});
		});
	});
</script>

<svelte:head>
	<title>Final Move</title>
</svelte:head>

<div class="bg-gray-100 flex flex-col items-center justify-center min-h-screen">
	<Notification {notification} {showNotification} />
	<Game onNotification={handleNotification} />
</div>
