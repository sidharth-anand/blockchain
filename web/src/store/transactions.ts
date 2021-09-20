import type {
	Chain,
	UnverifiedTransaction,
	VerifiedTransaction,
} from './../types';
import { writable } from 'svelte/store';

export const unverifiedTransactions = writable<UnverifiedTransaction[]>([]);
export const chains = writable<Chain[]>([]);
export const transactions = writable<VerifiedTransaction[]>([]);
