<script lang="ts">
	import { fade } from 'svelte/transition';
	import type { Tab } from '../../types';

	export let activeTab = 'chain';
	export let tabs: Tab[];
</script>

<div class="card card-bg content-card ">
	<div class="card-body content-card-overflow">
		{#each tabs as { component: Component, text }, i (i)}
			{#if activeTab === text}
				<div in:fade>
					<Component />
				</div>
			{/if}
		{/each}
	</div>
</div>
