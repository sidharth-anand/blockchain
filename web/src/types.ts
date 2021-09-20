export type Tab = {
	text: string;
	icon: string;
	color: string;
	activeStyle: string;
	component: any;
};

export type UnverifiedTransaction = {
	sender: string;
	recipient: string;
	amount: number;
};

export type VerifiedTransaction = UnverifiedTransaction & {
	timestamp: string | number | Date;
	blockIndex: number;
};

export type Chain = {
	index: number;
	previous_hash: string;
	proof: number;
	timestamp: string | number | Date;
	transactions: any;
};
