# Find functions that can be used with subquery and learn how these functions are executed logically and explain performance differences.
E.g: Compare EXISTS with IN, which is faster, why?

Some common functions/clauses that can be used with subqueries:
- EXISTS 
- IN
- WHERE
- in FROM 
- in SELECT
- Correlated Subqueries
    - in WHERE
    - in SELECT
- ANY/SOME
- ALL


## EXISTS
```sql
-- EXISTS
SELECT title 
FROM movies m
WHERE EXISTS (
    SELECT 1 
    FROM movies sub
    WHERE sub.id = m.id 
    AND sub.vote_count > 100
);
```
![alt text](<exists.svg>)

- Logical Execution:

    - The EXISTS subquery checks for existence rather than collecting results.
    - For each row in the outer query (SELECT title FROM movies m WHERE EXISTS (...)), it runs the inner query (SELECT 1 FROM movies sub WHERE sub.id = m.id AND sub.vote_count > 100).
    - If any row exists in the subquery result, the outer row is included in the result set.

- Performance Analysis:
    - Execution Time: 378.897 ms
    - Execution Plan: Similar to IN, utilizes a Parallel Hash Semi Join. Executes Parallel Seq Scans and applies a Hash Condition.

## IN
![alt text](<in.svg>)
```sql
-- IN
SELECT title 
FROM movies
WHERE id IN (
    SELECT id 
    FROM movies
    WHERE vote_count > 100
);
```
- Logical Execution:

    - The IN subquery first executes the inner query (SELECT id FROM movies WHERE vote_count > 100).

    - It collects all ids where vote_count is greater than 100.

    - The outer query (SELECT title, vote_count FROM movies WHERE id IN (...)) then filters rows from the movies table where the id matches any of those collected in the subquery.

- Performance Analysis:
    - Execution Time: 382.187 ms
    - Execution Plan:
        - Utilizes a Parallel Hash Semi Join.
        - Performs a Parallel Seq Scan on movies and movies_1.
        - Hashes the id columns for comparison.

- Summary:

**Both `IN` and `EXISTS` use parallel processing and hash joins.
They have similar performance characteristics with execution times around 380 ms.**

## NOT EXISTS
```sql
SELECT title, vote_count
FROM movies m
WHERE NOT EXISTS (
    SELECT 1
    FROM movies mv
    WHERE mv.vote_count > 100
    AND mv.id = m.id
);
```
![alt text](<not-exists.svg>)

- Logical Execution:
    - The NOT EXISTS subquery checks for non-existence.
    - It filters rows where the condition specified in the subquery (mv.vote_count > 100 AND mv.id = m.id) does not match.
    - Rows are included in the result set only if no matching row is found in the subquery.
- Performance Analysis:
    - Execution Time: 840.656 ms
    - Execution Plan:
        - Uses a Hash Anti Join, which identifies rows from movies that do not have corresponding matches in mv.
        - Executes a Parallel Seq Scan on movies and uses a Hash condition.

## NOT IN
```sql
SELECT title, vote_count
FROM movies
WHERE id NOT IN (
    SELECT id
    FROM movies
    WHERE vote_count > 100
);
```
![alt text](<not-in.svg>)
- Logical Execution:
    - The NOT IN subquery first executes the inner query (SELECT id FROM movies WHERE vote_count > 100).
    - It collects all ids where vote_count is greater than 100.
    - The outer query (SELECT title, vote_count FROM movies WHERE id NOT IN (...)) filters rows from the movies table where the id does not match any collected in the subquery.
- Performance Analysis:
    - Execution Time: 805.188 ms
    - Execution Plan:
        - Uses a Seq Scan on movies with a Filter condition for NOT (hashed SubPlan 1).
        - Executes a Parallel Seq Scan on movies_1 in the subquery and applies a Filter condition.
### Performance Differences:
- **Parallel Execution:** Both IN and EXISTS use Parallel Hash Semi Joins, leveraging parallel processing capabilities to speed up execution.
- **Anti Join vs Semi Join:** NOT EXISTS and NOT IN use Anti Join techniques (Hash Anti Join for NOT EXISTS and NOT IN) which can be more costly due to the need to hash and match rows explicitly.
- **Subquery Type:** EXISTS and NOT EXISTS are typically faster than IN and NOT IN when checking for existence due to their nature of early termination once a match is found or not found.

### SUMMARY
- `IN` vs `EXISTS`: Similar performance due to parallel processing and hash joins.

- `NOT IN` vs `NOT EXISTS`: Slower due to Hash Anti Join and sequential scans.

**Use `IN` and `EXISTS` for inclusion checks, and `NOT IN` and `NOT EXISTS` with caution for exclusion checks due to potential performance implications.**

## SUBQUERIES in FROM
    
```sql
--- find avg lifetime spend per customer
select round(avg(total_amount),2) as avg_lifetime_spent
from
(select customer_id, sum(amount) as total_amount from payment
group by customer_id) as subquery
--- What is the average total amount spent per day (avg daily revenue)?
select round(avg(daily_spent),2) as daily_avg_spent
from
(select sum(amount) as daily_spent, date(payment_date) from payment
group by date(payment_date)) a
```
    

## SUBQUERIES in SELECT
    
```sql
-- show all the payments together with how much the
-- payment amount is below the maximum payment amount
select 
*, (select max(amount) from payment)-amount as difference
from payment
```
    

## CORRELATED SUBQUERIES
- Every single row in subquery gets evaluated independently
- Subquery does **NOT** work independently
### in **WHERE**
```sql
-- Correlated Subquery in WHERE
-- get all people that are above avg of their city
select first_name, sales from employees e1
where sales > 
(select avg(sales) from employees e2
where e1.city = e2.city)
-- Show only those payments that have the highest amount per customer
select customer_id, amount from payment p1
where amount = (select max(amount) from payment p2
                where p1.customer_id = p2.customer_id)
order by customer_id
```
    
### in **SELECT**
```sql
-- get an additional column with the
-- minimum sale amount for every city
select first_name, sales,
(select min(sales) from employees e3
where e1.city = e3.city)
from employees e1
where sales > 
(select avg(sales) from employees e2
where e1.city = e2.city)
-- Maximum amount for every customer
select *,
(select max(amount) from payment p3
where p1.customer_id = p3.customer_id)
from payment p1
order by customer_id asc

-- show payments with highest payment 
-- for each customer's first name
-- including payment_id
select first_name, amount, payment_id
from payment p1
inner join customer c
on p1.customer_id = c.customer_id
where amount = (select max(amount) from payment p2
                where p1.customer_id=p2.customer_id)
-- solve it if you would not need to use payment_id
select first_name, max(amount)
from payment p1
inner join customer c
on p1.customer_id = c.customer_id
group by first_name
```