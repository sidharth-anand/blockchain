<script lang="ts">
	import { Router, Route } from 'svelte-navigator';
	import { showAlert, alertType, alertMessage } from './store/alert';
	import Dashboard from './pages/Dashboard.svelte';
	import Navbar from './components/Navbar.svelte';
	import Footer from './components/Footer.svelte';
	import WalletPage from './pages/WalletPage.svelte';
	import StakeCoins from './pages/StakeCoins.svelte';

	$: if ($showAlert) {
		setTimeout(() => {
			showAlert.update(() => false);
		}, 2500);
	}
</script>

{#if $showAlert}
	<div class="position-fixed w-25 alert-z-100">
		<div
			class={$alertType === 'danger'
				? 'alert alert-danger'
				: 'alert alert-success'}
			role="alert"
		>
			{$alertMessage}
		</div>
	</div>
{/if}

<Router primary={false}>
	<main>
		<div class="page-container">
			<div class="page-content py-3 px-5 ms-0">
				<div class="page-header position-relative m-0 w-100">
					<Navbar />
				</div>
				<div class="main-wrapper">
					<Route path="/">
						<Dashboard />
					</Route>

					<Route path="/my-wallet">
						<WalletPage />
					</Route>

					<Route path="/stake-coins">
						<StakeCoins />
					</Route>
				</div>
			</div>
		</div>
	</main>

	<Footer />
</Router>
