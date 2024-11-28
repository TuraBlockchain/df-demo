-- public.up_chain_data definition

-- Drop table

-- DROP TABLE public.up_chain_data;

CREATE TABLE public.up_chain_data (
	id serial4 NOT NULL,
	address varchar(255) NOT NULL,
	"type" varchar(255) NOT NULL,
	"json" jsonb NOT NULL,
	create_time timestamp DEFAULT CURRENT_TIMESTAMP NULL,
	CONSTRAINT up_chain_data_pkey PRIMARY KEY (id)
);