<script lang="ts">
	import NodeIcon from '../../icons/NodeIcon.svelte';
	import type { Tab } from '../../types';
	import { activeTab } from './../../store/tabs';

	export let tab: Tab;
	const handleTabSwitch = () => {
		activeTab.update(() => tab.text);
	};

	$: isActive = $activeTab === tab.text;
	$: btnClass = isActive
		? `${tab.activeStyle} nav-btn-border-transparent`
		: tab.color;
	$: textClass = isActive ? tab.color : '';
</script>

<div class="actions-widget-item">
	<button
		type="button"
		on:click={() => handleTabSwitch()}
		class="btn btn-circle {btnClass}"
	>
		{#if tab.icon.startsWith('fa')}
			<i class={tab.icon} />
		{:else}
			<NodeIcon />
		{/if}
	</button>
	<span class="actions-widget-item-title text-capitalize {textClass}">
		{tab.text}
	</span>
</div>
