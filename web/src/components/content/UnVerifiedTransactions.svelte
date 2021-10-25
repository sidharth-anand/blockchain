<script>
	import { onMount } from 'svelte';
	import { SERVER_URL } from '../../constants';
	import { alertMessage, alertType, showAlert } from '../../store/alert';
	import { activeTab } from '../../store/tabs';
	import { transactionPool } from '../../store/transactions';

	let error = false;
	let is_validator = false;

	onMount(async () => {
		try {
			const res = await fetch(`${SERVER_URL}/transactions/pool`);
			const res2 = await fetch(`${SERVER_URL}/wallet/validator`);
			const data = await res.json();
			const data2 = await res2.json();

			console.log(res2);

			is_validator = data2;

			transactionPool.update(() => {
				return [...data];
			});
		} catch (err) {
			error = true;
		}
	});

	const mine = async () => {
		try {
			const res = await fetch(`${SERVER_URL}/mint`, {
				headers: {
					'Content-Type': 'application/json',
				},
				method: 'GET',
			});
			const data = await res.json();
			if (`${res.status}`.startsWith('4')) {
				showAlert.update(() => true);
				alertType.update(() => 'danger');
				alertMessage.update(() => data);
			} else {
				transactionPool.update(() => {
					return [];
				});

				showAlert.update(() => true);
				alertType.update(() => 'success');
				alertMessage.update(() => data);

				setTimeout(() => {
					activeTab.update(() => 'verified transactions');
				}, 1200);
			}
		} catch (err) {
			showAlert.update(() => true);
			alertType.update(() => 'danger');
			alertMessage.update(() => 'Something went wrong');
		}
	};
</script>

<div class="card card-bg">
	<div class="card-body">
		<div class="row mb-5 mb-md-0">
			<div class="col-md-6">
				<h5 class="card-title">Unverified Transactions</h5>
			</div>
			<div
				class="col-md-6 d-flex align-items-center justify-content-start justify-content-md-end"
			>
				{#if is_validator && $transactionPool.length}
					<button on:click={mine} class="btn btn-primary btn-sm">Mine</button>
				{/if}
			</div>
		</div>
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
				{#each $transactionPool as transaction, i (i)}
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
