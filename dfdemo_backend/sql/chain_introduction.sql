-- public.chain_introduction definition

-- Drop table标签介绍表

-- DROP TABLE public.chain_introduction;

CREATE TABLE public.chain_introduction (
	id serial4 NOT NULL,
	"type" varchar(255) NOT NULL,
	introduction text NOT NULL,
	create_time timestamp DEFAULT CURRENT_TIMESTAMP NULL,
	CONSTRAINT chain_introduction_pkey PRIMARY KEY (id)
);

INSERT INTO public.chain_introduction ("type",introduction,create_time) VALUES
	 ('Solana','Solana: A high-performance blockchain platform designed for decentralized apps and crypto projects.\nKey Features:\nFast & Scalable: Processes up to 65,000 transactions per second, enabling seamless user experiences.\nLow Fees: Near-zero transaction costs make it ideal for microtransactions and high-frequency trading.\nEco-Friendly: Utilizes an energy-efficient Proof-of-History (PoH) combined with Proof-of-Stake (PoS) consensus.\nExplore More: Solana Official Website','2024-11-11 21:25:45.016814');
