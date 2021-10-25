import { writable } from 'svelte/store';
import type { Tab } from '../types';

export const tabs = writable<Tab[]>([]);
export const activeTab = writable<string>('');
