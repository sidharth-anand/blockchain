<script lang="ts">
	import type { Tab } from '../../types';
	import NavLink from './NavLink.svelte';

	export let tabs: Tab[];
</script>

<div class="card card-bg actions-widget text-center">
	<div class="card-body">
		{#each tabs as tab, i (i)}
			<NavLink {tab} />
		{/each}
	</div>
</div>
