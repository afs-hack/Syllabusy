<script lang="ts">
	import favicon from '$lib/assets/favicon.svg';
	import { onMount } from "svelte";
	import { initAuth } from "$lib/auth";
	
	onMount(() => {
		initAuth();
	});

	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

{@render children?.()}

