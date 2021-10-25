<script lang="ts">
	import { onMount } from 'svelte';

	import { SERVER_URL } from '../constants';

	let wallet: any = null;
	let loading = false;

	onMount(async () => {
		loading = true;
		try {
			const res = await fetch(`${SERVER_URL}/wallet`);
			const data = await res.json();
			wallet = data;
		} catch (err) {}
		loading = false;
	});

	$: {
		console.log(wallet);
	}
</script>

{#if loading && !wallet}
	<h1 class="py-4 text-center">Loading...</h1>
{:else}
	<div class="container">
		<h3 class="text-center mb-5">
			<i class="far fa-credit-card me-3 text-primary" />
			Your Wallet
		</h3>
		<div class="card card-bg content-card">
			<div class="card-body">
				<h4 class="display-5 text-center mb-4 ">
					<span class="text-warning">
						{wallet?.balance}
					</span>
					coins
				</h4>
				<div class="text-center mb-5">
					<h5>Address</h5>
					<p>{wallet?.address[0]}</p>
				</div>
				{#if !wallet?.is_validator}
					<div class="text-center">
						<button class="btn btn-success"> Become Validator </button>
					</div>
				{/if}
			</div>
		</div>
	</div>
{/if}
