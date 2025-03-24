<script lang="ts">
	export let notification: string = '';
	export let showNotification: boolean = false;
</script>

<div
	class="notification fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-6xl z-50 pointer-events-none"
	class:fade-out={!showNotification}
	class:hidden={!showNotification}
>
	{notification}
</div>

<style>
	.notification {
		opacity: 1;
		transition: opacity 0.5s;
	}

	.fade-out {
		opacity: 0;
	}

	.hidden {
		display: none;
	}
</style>
