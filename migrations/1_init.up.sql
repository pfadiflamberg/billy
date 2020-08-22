CREATE TYPE bulk_invoice_state AS ENUM ('created', 'issued', 'closed');

CREATE TABLE bulk_invoice (
    id SERIAL,

    state bulk_invoice_state,

    issuing_date TIMESTAMP,
    due_date TIMESTAMP,

    text_invoice TEXT,
    text_reminder TEXT,

    create_time TIMESTAMP NOT NULL DEFAULT NOW(),
    update_time TIMESTAMP NOT NULL,
);

CREATE TYPE invoice_state AS ENUM ('pending', 'paid', 'annulled');

CREATE TABLE invoice (
    bulk_invoice_id INT,
    FOREIGN KEY (bulk_invoice_id) REFERENCES bulk_invoice (id),

    state invoice_state,
    state_message TEXT,

    recipient INT,
    recipient_name TEXT,

    create_time TIMESTAMP NOT NULL DEFAULT NOW(),
    update_time TIMESTAMP NOT NULL,
);