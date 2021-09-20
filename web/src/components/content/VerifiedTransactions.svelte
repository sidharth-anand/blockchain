<script lang="ts">
	import { chains, transactions } from '../../store/transactions';
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

			chains.update(() => {
				return data.chain;
			});

			let t = [];

			$chains.forEach((e) => {
				if (e.transactions.length) {
					e.transactions.forEach((el) => {
						t.push({ blockIndex: e.index, timestamp: e.timestamp, ...el });
					});
				}
			});

			console.log({ t });

			transactions.update(() => t);
		} catch (err) {
			console.log(err);
		}
	});
</script>

<div class="card card-bg">
	<div class="card-body">
		<h5 class="card-title">Verified Transactions</h5>
		<table class="table crypto-table">
			<thead>
				<tr>
					<th>Block Index</th>
					<th scope="col">Sender</th>
					<th scope="col">Recipient</th>
					<th scope="col">Timestamp</th>
					<th scope="col">Amount ($)</th>
				</tr>
			</thead>
			<tbody>
				{#each $transactions as transaction, i (i)}
					<tr>
						<th scope="row">{transaction.blockIndex}</th>

						<td>
							{transaction.sender}
						</td>
						<td>{transaction.recipient}</td>
						<td>{transaction.timestamp}</td>
						<td class="text-success">{transaction.amount}</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
</div>
