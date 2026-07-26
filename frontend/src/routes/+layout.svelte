<script lang="ts">
	import { onMount } from 'svelte';
	import '../app.css';
	import { apiGet } from '$lib/api';
	import { currentUser, authReady } from '$lib/stores/auth';
	import { initTheme } from '$lib/stores/theme';
	import type { User } from '$lib/types';

	onMount(() => {
		initTheme();

		// Check if user is already authenticated on every page load
		apiGet<User>('/auth/me')
			.then((user) => {
				currentUser.set(user);
			})
			.catch(() => {
				currentUser.set(null);
			})
			.finally(() => {
				authReady.set(true);
			});
	});
</script>

<slot />

