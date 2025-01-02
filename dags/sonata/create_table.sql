CREATE TABLE customers (
    customer_id VARCHAR PRIMARY KEY,
    customer_name VARCHAR,
    created_date TIMESTAMP,
    updated_date TIMESTAMP
);

CREATE TABLE products (
    id VARCHAR PRIMARY KEY,
    name VARCHAR,
    category_id NUMERIC,
    original_price NUMERIC,
    created_date TIMESTAMP,
    unit VARCHAR,
    updated_date TIMESTAMP
);

CREATE TABLE categories (
    id NUMERIC PRIMARY KEY,
    name VARCHAR,
    created_date TIMESTAMP,
    updated_date TIMESTAMP
);

CREATE TABLE branches (
    id NUMERIC PRIMARY KEY,
    name VARCHAR,
    address VARCHAR,
    location_name VARCHAR,
    contact_number VARCHAR,
    created_date TIMESTAMP,
    updated_date TIMESTAMP
);

CREATE TABLE invoices (
    id VARCHAR PRIMARY KEY,
    created_date TIMESTAMP,
    branch_id NUMERIC,
    staff_name VARCHAR,
    revenue NUMERIC,
    total_payment NUMERIC,
    status_value VARCHAR,
    updated_date TIMESTAMP,
    invoice_details JSONB
);
