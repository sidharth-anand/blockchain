<script lang="ts">
	import { onMount } from 'svelte';
	import { SERVER_URL } from '../../constants';
	import { linkedNodes } from '../../store/linkedNodes';
	let error = false;

	onMount(async () => {
		try {
			const res = await fetch(`${SERVER_URL}/nodes`);
			const data = await res.json();
			console.log('Linked nodes', data);
			linkedNodes.update(() => {
				return [...data];
			});
		} catch (err) {
			error = true;
		}
	});
</script>

<div class="card card-bg">
	<div class="card-body">
		<h5 class="card-title">Linked Nodes</h5>
		{#if error}
			<div class="alert alert-danger">Could not fetch data</div>
		{:else}
			{#each $linkedNodes as node (node)}
				<li class="mb-2">
					<a href={'http://' + node} class="text-decoration-underline">{node}</a
					>
				</li>
			{/each}
		{/if}
	</div>
</div>
