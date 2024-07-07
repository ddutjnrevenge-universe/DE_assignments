-- CTE (exists in a single query)
EXPLAIN ANALYZE
WITH CTE as (
	select customer_id, count(*) as OrderCount 
	from customer
	group by customer_id
)

select c.customer_id, cte.OrderCount, c.first_name, c.last_name
from customer c
join cte on c.customer_id=cte.customer_id;

-- VIEW (exists outside this session)
CREATE VIEW CustomerPayment AS
SELECT C.customer_id, c.first_name, c.last_name, p.payment_id, p.payment_date
FROM customer C
JOIN payment P ON C.customer_id = P.customer_id;

EXPLAIN ANALYZE
SELECT * FROM CustomerPayment WHERE customer_id = 1;

-- Temporary Tables (just exist in this session)
CREATE TEMPORARY TABLE TempCustomerPayment (
    customer_id INT,
    payment_id INT,
    payment_date TIMESTAMP
);

INSERT INTO TempCustomerPayment (customer_id, payment_id, payment_date)
SELECT customer_id, payment_id, payment_date
FROM payment;

EXPLAIN ANALYZE
SELECT * FROM TempCustomerPayment WHERE customer_id = 1;

DROP TABLE TempCustomerPayment;

-- TABLE VARIABLE (not available in PostgreSQL)
DECLARE @TableVar TABLE (
    customer_id INT,
    payment_id INT,
    payment_date TIMESTAMP
);

INSERT INTO @TableVar (customer_id, payment_id, payment_date)
SELECT customer_id, payment_id, payment_date
FROM payment;

SELECT * FROM @TableVar WHERE customer_id = 1;

-- INLINE TVFs (exists outside session)
CREATE OR REPLACE FUNCTION GetCustomerPayment(cust_id INT)
RETURNS TABLE(payment_id INT, payment_date TIMESTAMP) AS $$
BEGIN
    RETURN QUERY
    SELECT p.payment_id, p.payment_date AT TIME ZONE 'UTC' AS payment_date
    FROM payment p
    WHERE p.customer_id = cust_id;
END;
$$ LANGUAGE plpgsql;

--- Call the function
EXPLAIN ANALYZE
SELECT * FROM GetCustomerPayment(1);

DROP FUNCTION getcustomerpayment(integer)