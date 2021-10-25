<script lang="ts">
	import { useNavigate } from 'svelte-navigator';

	import { showAlert, alertMessage, alertType } from './../store/alert';
	import { onMount } from 'svelte';

	import { SERVER_URL } from '../constants';

	let wallet: any = null;
	let loading = false;
	const navigate = useNavigate();

	onMount(async () => {
		loading = true;
		try {
			const res = await fetch(`${SERVER_URL}/wallet`);
			const data = await res.json();

			wallet = data;
		} catch (err) {}
		loading = false;
	});

	const becomeValidator = async () => {
		try {
			const res = await fetch(`${SERVER_URL}/transactions/validator`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
			});

			const data = await res.json();

			if (`${res.status}`.startsWith('4')) {
				showAlert.update(() => true);
				alertType.update(() => 'danger');
				alertMessage.update(() => data);
			} else {
				showAlert.update(() => true);
				alertType.update(() => 'success');
				alertMessage.update(
					() =>
						"Your transaction is added. You'll be a validator once the block is minted"
				);

				setTimeout(() => {
					navigate('/');
				}, 1200);
			}
		} catch (err) {}
	};
</script>

<div>
	{#if loading && !wallet}
		<h1 class="py-4 text-center">Loading...</h1>
	{:else}
		<div class="container">
			<h3 class="text-center mb-5">
				<i class="far fa-credit-card me-3 text-primary" />
				Your Wallet
			</h3>
			<div class="card card-bg content-card">
				{#if wallet?.is_validator}
					<div class="d-flex justify-content-end align-items-center">
						<span class="badge m-3 rounded-pill bg-success"> Validator </span>
					</div>
				{/if}
				<div class="card-body">
					<div class="mb-5 text-center">
						<h4 class="text-primary">Address</h4>
						<p>{wallet?.address[0]}</p>
					</div>

					<div class="row">
						<div class="col-md-6 col-12">
							<h3 class="d-block text-center">Balance</h3>
							<h1 class="text-warning text-center">
								{wallet?.balance}
							</h1>
						</div>

						<div class="col-md-6 col-12">
							<h3 class="d-block text-center">Stake</h3>
							<h1 class="text-info text-center">
								{wallet?.stake}
							</h1>
						</div>
					</div>

					{#if !wallet?.is_validator}
						<div class="mt-5">
							{#if wallet?.balance >= 10}
								<div class="text-center">
									<button on:click={becomeValidator} class="btn btn-success">
										Become Validator
									</button>
								</div>
							{:else}
								<div class="text-center">
									<p class="mb-0 ">
										You need atleast 10 coins to become a validator
									</p>
								</div>
							{/if}
						</div>
					{/if}
				</div>
			</div>
		</div>
	{/if}
</div>
