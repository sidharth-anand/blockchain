import { writable } from 'svelte/store';

export const showAlert = writable(false);
export const alertType = writable('success');
export const alertMessage = writable('');
