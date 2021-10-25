<script>
	import { SERVER_URL } from './../constants';
	import { showAlert, alertMessage, alertType } from './../store/alert';
	import { unverifiedTransactions } from '../store/transactions';

	let loading = false;

	// let sender = '';
	let recipient = '';
	let amount = '';

	const addTransaction = async () => {
		loading = true;

		if (!recipient || !amount) {
			showAlert.update(() => true);
			alertType.update(() => 'danger');
			alertMessage.update(() => 'Please enter all fields');
			loading = false;
			return;
		}

		try {
			const res = await fetch(`${SERVER_URL}/transactions/new`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({ recipient, amount }),
			});

			const data = await res.json();

			console.log(res);
			if (`${res.status}`.startsWith('4')) {
				showAlert.update(() => true);
				alertType.update(() => 'danger');
				alertMessage.update(
					() => data.message || 'Unable to make a transaction'
				);
			} else {
				// unverifiedTransactions.update((data) => {
				// 	return [...data, { recipient, amount }];
				// });
			}
		} catch (err) {
			showAlert.update(() => true);
			alertType.update(() => 'danger');
			alertMessage.update(() => 'Unable to make a transaction');
		}

		recipient = '';
		amount = '';
		loading = false;
	};
</script>

<div class="card card-bg">
	<div class="card-body">
		<div class="d-flex align-items-center text-info mb-4">
			<i class="far fa-credit-card" />
			<h5 class="card-title mb-0 ms-3">Add new transaction</h5>
		</div>
		<form on:submit|preventDefault={addTransaction}>
			<div class="mb-4">
				&nbsp;
				<!-- <label for="sender" class="form-label">Sender</label>
				<input
					bind:value={sender}
					type="text"
					class="form-control"
					id="sender"
				/> -->
			</div>
			<div class="mb-4">
				<label for="recipient" class="form-label">Recipient</label>
				<input
					bind:value={recipient}
					type="text"
					class="form-control"
					id="recipient"
				/>
			</div>
			<div class="mb-5">
				<label for="amount" class="form-label">Amount</label>
				<input
					bind:value={amount}
					type="number"
					class="form-control"
					id="amount"
				/>
			</div>
			<button class="btn btn-primary btn-sm mt-5"
				>{loading ? 'Loading..' : 'Send'}</button
			>
		</form>
	</div>
</div>
