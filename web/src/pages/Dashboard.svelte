<script lang="ts">
	import type { Tab } from './../types';
	import AddTransaction from '../components/AddTransaction.svelte';
	import Content from '../components/content/index.svelte';
	import Navigation from '../components/navigation/Navigation.svelte';
	import RegisterNode from '../components/RegisterNode.svelte';
	import Chain from '../components/content/Chain.svelte';
	import VerifiedTransactions from '../components/content/VerifiedTransactions.svelte';
	import UnVerifiedTransactions from '../components/content/UnVerifiedTransactions.svelte';
	import LinkedNodes from '../components/content/LinkedNodes.svelte';
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
</script>

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
