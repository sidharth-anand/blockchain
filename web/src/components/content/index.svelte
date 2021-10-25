<script lang="ts">
	import { fade } from 'svelte/transition';
	import { tabs, activeTab } from './../../store/tabs';
</script>

<div class="card card-bg content-card ">
	<div class="card-body content-card-overflow">
		{#each $tabs as { component: Component, text }, i (i)}
			{#if $activeTab === text}
				<div in:fade>
					<Component />
				</div>
			{/if}
		{/each}
	</div>
</div>
