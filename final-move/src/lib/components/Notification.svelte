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
		transition: opacity 2.5s ease-out;
		animation: notificationAppear 0.3s ease-in;
	}

	.fade-out {
		opacity: 0;
	}

	.hidden {
		display: none;
	}

	@keyframes notificationAppear {
		0% {
			opacity: 0;
			transform: scale(0.8);
		}
		100% {
			opacity: 1;
			transform: scale(1);
		}
	}
</style>
