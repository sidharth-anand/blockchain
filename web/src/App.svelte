<script lang="ts">
	import { showAlert, alertType, alertMessage } from './store/alert';
	import type { Tab } from './types';
	import AddTransaction from './components/AddTransaction.svelte';
	import Content from './components/content/index.svelte';
	import Navigation from './components/navigation/Navigation.svelte';
	import Navbar from './components/Navbar.svelte';
	import RegisterNode from './components/RegisterNode.svelte';
	import Chain from './components/content/Chain.svelte';
	import VerifiedTransactions from './components/content/VerifiedTransactions.svelte';
	import UnVerifiedTransactions from './components/content/UnVerifiedTransactions.svelte';
	import LinkedNodes from './components/content/LinkedNodes.svelte';
	import { onMount } from 'svelte';

	const tabs: Tab[] = [
		{
			color: 'text-primary',
			icon: 'fas fa-link',
			text: 'chain',
			activeStyle: 'text-white bg-primary border-none',
			component: Chain,
		},
		{
			color: 'text-success',
			activeStyle: 'text-white bg-success',
			icon: 'fas fa-user-check',
			text: 'verified transactions',
			component: VerifiedTransactions,
		},
		{
			color: 'text-warning',
			activeStyle: 'text-white bg-warning',
			icon: 'fas fa-user-times',
			text: 'unverified transactions',
			component: UnVerifiedTransactions,
		},
		{
			color: 'text-info',
			activeStyle: 'text-white bg-info',
			icon: 'node',
			text: 'linked nodes',
			component: LinkedNodes,
		},
	];

	let activeTab = 'chain';
	const setTab: (n: string) => void = (tabName) => {
		activeTab = tabName;
		localStorage.setItem('tab', activeTab);
	};

	onMount(() => {
		let tab = localStorage.getItem('tab');
		if (!tab) {
			localStorage.setItem('tab', activeTab);
		} else {
			activeTab = tab;
		}
	});

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

<main>
	<div class="page-container">
		<div class="page-content py-3 px-5 ms-0">
			<div class="page-header position-relative m-0 w-100">
				<Navbar />
			</div>
			<div class="main-wrapper">
				<div class="row">
					<div class="col-lg-8">
						<Navigation {tabs} {setTab} {activeTab} />
					</div>
					<div class="col-lg-4">
						<RegisterNode />
					</div>
				</div>
				<div class="row">
					<div class="col-lg-8 col-md-12">
						<Content {tabs} {activeTab} />
					</div>
					<div class="col-lg-4 col-md-12">
						<AddTransaction />
					</div>
				</div>
			</div>
		</div>
	</div>
</main>

<footer class="text-center">
	Developed by

	<a href="https://github.com/sreekarnv">Sreekar V Nutulapati</a>,
	<a href="https://github.com/sidharth-anand/blockchain.git">
		Sidharth Anand
	</a>
	&
	<a href="https://github.com/saiankit"> Sai Ankit B </a>
</footer>
