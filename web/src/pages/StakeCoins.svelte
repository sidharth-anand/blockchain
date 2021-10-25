<script lang="ts">
	import { activeTab } from '../store/tabs';
	import { showAlert, alertMessage, alertType } from '../store/alert';
	import { SERVER_URL } from '../constants';
	import { useNavigate } from 'svelte-navigator';

	let loading = false;
	let amount: string = '';
	const navigate = useNavigate();

	const stakeCoins = async (e) => {
		e.preventDefault();
		try {
			const res = await fetch(`${SERVER_URL}/transactions/stake`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({ amount }),
			});
			console.log(res);
			const data = await res.json();

			if (`${res.status}`.startsWith('4')) {
				showAlert.update(() => true);
				alertType.update(() => 'danger');
				alertMessage.update(() => data || 'Could not perform this action');
			} else {
				showAlert.update(() => true);
				alertType.update(() => 'success');
				alertMessage.update(() => data || 'Success!');

				setTimeout(() => {
					navigate('/');
					activeTab.update(() => 'unverified transactions');
				}, 1200);
			}
		} catch (err) {
			showAlert.update(() => true);
			alertType.update(() => 'danger');
			alertMessage.update(() => err.message || 'Something went wrong');
		}
	};
</script>

<div class="p-3">
	<div class="container">
		<h1 class="text-center mb-4">Stake Coins</h1>
		<form class="card card-bg p-3" autocomplete="off" on:submit={stakeCoins}>
			<div class="container">
				<div class="mb-1">
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
			</div>
		</form>
	</div>
</div>
