<script lang="ts">
	import { SERVER_URL } from '../../constants';
	import { chains, transactions } from './../../store/transactions';
	import type { Tab } from '../../types';
	import NavLink from './NavLink.svelte';

	let body = '';
	let loading = false;
	let errorText = '';

	export let setTab: (name: string) => void;
	export let tabs: Tab[];
	export let activeTab;

	const handleTabSwitch = (tabName: string) => setTab(tabName);

	const resetValue = () => {
		body = '';
		errorText = '';
	};

	const resolveConflicts = async () => {
		errorText = '';
		body = '';
		loading = true;
		try {
			const res = await fetch(`${SERVER_URL}/nodes/resolve`);
			const data = await res.json();
			chains.update(() => {
				if (data.new_chain) {
					return data.new_chain;
				}
				return [...data.chain];
			});
			body = data?.message || '';

			let t = [];

			$chains.forEach((e) => {
				if (e.transactions.length) {
					t.push({
						...e.transactions,
						blockIndex: e.index,
						timestamp: e.timestamp,
					});
				}
			});

			transactions.update(() => t);
		} catch (err) {
			errorText = 'something went wrong';
		}

		loading = false;
	};
</script>

<div
	on:click={() => resetValue()}
	class="modal fade"
	id="resolve-conflicts"
	tabindex="-1"
	aria-labelledby="resolve-conflictsLabel"
	aria-hidden="true"
>
	<div class="modal-dialog">
		<div class="modal-content modal-dark">
			<div class="modal-header text-light">
				<h5 class="modal-title" id="exampleModalLabel">Resolve Conflicts</h5>
			</div>
			<div class="modal-body ">
				{#if body.length > 0}
					<p class="text-success">
						{body}
					</p>
				{/if}

				{loading ? 'Loading...' : ''}

				{#if errorText.length > 0}
					<p class="text-danger">
						{errorText}
					</p>
				{/if}
			</div>

			<div class="modal-footer">
				<button
					on:click={() => {
						resetValue();
					}}
					type="button"
					class="btn btn-danger"
					data-bs-dismiss="modal"
				>
					<i class="fas fa-times" />
					<span class="ms-1">No</span>
				</button>
				<button
					on:click={() => {
						resolveConflicts();
					}}
					type="button"
					class="btn btn-success"
				>
					<i class="fas fa-check" />
					<span class="ms-1">{'Yes'}</span>
				</button>
			</div>
		</div>
	</div>
</div>

<div class="card card-bg actions-widget text-center">
	<div class="card-body">
		{#each tabs as tab, i (i)}
			<NavLink {activeTab} {tab} {handleTabSwitch} />
		{/each}

		<div class="actions-widget-item">
			<button
				type="button"
				data-bs-toggle="modal"
				data-bs-target="#resolve-conflicts"
				class="btn btn-circle text-danger"
			>
				<i class="fas fa-bolt" />
			</button>

			<span class="actions-widget-item-title text-capitalize">
				Resolve Conflicts
			</span>
		</div>
	</div>
</div>
