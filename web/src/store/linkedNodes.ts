import { writable } from 'svelte/store';

export const linkedNodes = writable<string[]>([]);
