<script>
	import { linkedNodes } from '../store/linkedNodes';
	import NodeIcon from '../icons/NodeIcon.svelte';
	import { alertMessage, alertType, showAlert } from '../store/alert';
	import { SERVER_URL } from '../constants';

	let loading = false;
	let inputField = '';

	const registerNode = async () => {
		loading = true;
		try {
			if (!inputField) {
				showAlert.update(() => true);
				alertType.update(() => 'danger');
				alertMessage.update(() => 'Please enter all fields');
				loading = false;
				return;
			}

			const nodes = [...$linkedNodes, inputField];

			const res = await fetch(`${SERVER_URL}/nodes/register`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({ nodes }),
			});

			const data = await res.json();
			linkedNodes.update(() => {
				return [...data.total_nodes];
			});
			showAlert.update(() => true);
			alertType.update(() => 'success');
			alertMessage.update(() => data.message || 'Success');
			console.log(data);
		} catch (err) {
			console.log({ ...err });
			showAlert.update(() => true);
			alertType.update(() => 'danger');
			alertMessage.update(() => err.message || 'Could not register node');
		}
		inputField = '';
		loading = false;
	};
</script>

<div class="card card-bg">
	<div class="card-body">
		<div>
			<div class="d-flex align-items-center mb-2 text-warning">
				<NodeIcon />
				<h5 class="text-white card-title mb-0 ms-3">Register Node</h5>
			</div>
			<form
				class="d-flex align-items-center"
				on:submit|preventDefault={() => registerNode()}
			>
				<input
					bind:value={inputField}
					placeholder="Neighbour Url"
					type="text"
					class="form-control"
					id="node-url"
				/>
				<button type="submit" disabled={loading} class="btn btn-success btn-sm">
					{loading ? 'Loading...' : 'Add'}
				</button>
			</form>
		</div>
	</div>
</div>
