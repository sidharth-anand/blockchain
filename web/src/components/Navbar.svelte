<script lang="ts">
	import { Link } from 'svelte-navigator';
</script>

<nav class="navbar navbar-expand-lg">
	<div class="container-fluid">
		<div class="header-title flex-fill">
			<h5>Dexter Coffee Shop</h5>
		</div>

		<ul class="navbar-nav align-items-center justify-content-end">
			<li class="nav-item mb-0">
				<Link to="/" class="nav-link">Home</Link>
			</li>
			<li class="nav-item">
				<Link to="/my-wallet" class="nav-link">Wallet</Link>
			</li>
			<li class="nav-item">
				<a
					href="https://github.com/sidharth-anand/blockchain.git"
					class="btn text-white fs-3"
				>
					<i class="fab fa-github" />
				</a>
			</li>
		</ul>
	</div>
</nav>
