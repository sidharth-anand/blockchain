<script lang="ts">
	import { chains } from './../../store/transactions';
	import { onMount } from 'svelte';
	import { alertMessage, alertType, showAlert } from '../../store/alert';
	import { SERVER_URL } from '../../constants';

	onMount(async () => {
		try {
			const res = await fetch(`${SERVER_URL}/chain`, {
				headers: {
					'Content-Type': 'application/json',
				},
				method: 'GET',
			});
			const data = await res.json();

			chains.update(() => {
				return data.chain;
			});
		} catch (err) {
			showAlert.update(() => true);
			alertType.update(() => 'danger');
			alertMessage.update(() => 'Something went wrong');
		}
	});
</script>

<div>
	<h5 class="card-title">Chain</h5>
	<table class="table crypto-table">
		<thead>
			<tr>
				<th scope="col">Block Index</th>
				<th scope="col">Previous Hash</th>
				<th scope="col">Proof of Work</th>
				<th scope="col">Timestamps</th>
				<th scope="col"># of Transactions</th>
			</tr>
		</thead>
		<tbody>
			{#each $chains as chain, i (i)}
				<tr>
					<th scope="row">{chain.index}</th>
					<td>
						{chain.previous_hash}
					</td>
					<td class="text-primary">{chain.proof}</td>
					<td>{chain.timestamp}</td>
					<td
						><button type="button" class="btn btn-link"
							>{chain.transactions?.length}</button
						></td
					>
				</tr>
			{/each}
		</tbody>
	</table>
</div>
