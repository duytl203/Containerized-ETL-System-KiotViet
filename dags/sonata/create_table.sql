CREATE TABLE customers (
    customer_id VARCHAR PRIMARY KEY,
    customer_name VARCHAR NOT NULL,
    created_date TIMESTAMP NOT NULL,
    updated_date TIMESTAMP
);
CREATE TABLE products (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    category_id NUMERIC,
    original_price NUMERIC,
    created_date TIMESTAMP NOT NULL,
    unit VARCHAR,
    updated_date TIMESTAMP
);
CREATE TABLE categories (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    created_date TIMESTAMP NOT NULL,
    updated_date TIMESTAMP
);
CREATE TABLE branches (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    address VARCHAR,
    location_name VARCHAR,
    contact_number VARCHAR,
    created_date TIMESTAMP NOT NULL,
    updated_date TIMESTAMP
);
CREATE TABLE invoices (
    id VARCHAR PRIMARY KEY,
    created_date TIMESTAMP NOT NULL,
    branch_id NUMERIC NOT NULL,
    staff_name VARCHAR,
    revenue NUMERIC,
    total_payment NUMERIC,
    statusValue VARCHAR,
    updated_date TIMESTAMP,
    invoiceDetails JSONB
);
GRANT ALL PRIVILEGES ON invoices,customers,products,branches,categories TO duytl;

