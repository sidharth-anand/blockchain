export type Tab = {
	text: string;
	icon: string;
	color: string;
	activeStyle: string;
	component: any;
};

export type Chain = {
	index: number;
	difficulty: number;
	minter_address: string;
	previous_hash: string;
	minter_balance: number;
	timestamp: string | number | Date;
	transactions: any;
};

export type TransactionIn = {
	signature: string;
	transaction_out_id: string;
	transaction_out_index: number;
};

export type TransactionOut = {
	address: string;
	amount: number;
};

export type TransactionPool = {
	id: string;
	transaction_ins: TransactionIn[];
	transaction_outs: TransactionOut[];
	type: string;
};
