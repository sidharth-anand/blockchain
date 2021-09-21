<script>
	import { SERVER_URL } from '../../constants';
	import { alertMessage, alertType, showAlert } from '../../store/alert';
	import { unverifiedTransactions } from '../../store/transactions';

	const mine = async () => {
		try {
			const res = await fetch(`${SERVER_URL}/mine`, {
				headers: {
					'Content-Type': 'application/json',
				},
				method: 'GET',
			});
			await res.json();
			unverifiedTransactions.update(() => {
				return [];
			});
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
				{#if $unverifiedTransactions.length}
					<button on:click={mine} class="btn btn-primary btn-sm">Mine</button>
				{/if}
			</div>
		</div>
		<table class="table crypto-table">
			<thead>
				<tr>
					<th>#</th>
					<th scope="col">Sender</th>
					<th scope="col">Recipient</th>
					<th scope="col">Amount ($)</th>
				</tr>
			</thead>
			<tbody>
				{#each $unverifiedTransactions as transaction, i (i)}
					<tr>
						<th scope="row">{i + 1}</th>
						<td>
							{transaction.sender}
						</td>
						<td>{transaction.recipient}</td>
						<td class="text-success">{transaction.amount}</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
</div>
