<script lang="ts">
	import { chains, transactions } from '../../store/transactions';
	import { alertMessage, alertType, showAlert } from '../../store/alert';
	import { onMount } from 'svelte';
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

			console.log(data);

			chains.update(() => {
				return data.chain;
			});

			let t = [];

			$chains.forEach((e) => {
				if (e.transactions.length) {
					e.transactions.forEach((el) => {
						t.push(el);
					});
				}
			});

			transactions.update(() => t);
		} catch (err) {
			showAlert.update(() => true);
			alertType.update(() => 'danger');
			alertMessage.update(() => 'Unable to fetch data');
		}
	});
</script>

<div class="card card-bg">
	<div class="card-body">
		<h5 class="card-title">Verified Transactions</h5>
		<table class="table crypto-table">
			<thead>
				<tr>
					<th>#</th>
					<th scope="col">Type</th>
					<th scope="col">Amount</th>
					<th scope="col">Recipient</th>
				</tr>
			</thead>
			<tbody>
				{#each $transactions as transaction, i (i)}
					<tr>
						<th scope="row">{i + 1}</th>
						<td>
							{transaction.type}
						</td>
						<td class="text-success">
							{transaction?.transaction_outs[0].amount}
						</td>
						<td>
							{transaction.transaction_outs[0].address}
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
</div>
