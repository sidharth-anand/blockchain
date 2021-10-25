import type { Chain, TransactionPool } from './../types';
import { writable } from 'svelte/store';

export const chains = writable<Chain[]>([]);
export const transactions = writable<TransactionPool[]>([]);
export const transactionPool = writable<TransactionPool[]>([]);
