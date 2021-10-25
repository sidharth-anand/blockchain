import type {
	Chain,
	TransactionPool,
	UnverifiedTransaction,
	VerifiedTransaction,
} from './../types';
import { writable } from 'svelte/store';

export const unverifiedTransactions = writable<UnverifiedTransaction[]>([]);
export const chains = writable<Chain[]>([]);

export const transactions = writable<TransactionPool[]>([]);
export const transactionPool = writable<TransactionPool[]>([]);
