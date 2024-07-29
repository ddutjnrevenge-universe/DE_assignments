# Spark Exercise

## Exercise 1: Average Value Calculation Using Spark
**Summary**
- **Objective**: Compare groupByKey() and reduceByKey() in Spark to calculate the average value for each key in a dataset of key-value pairs.

1. Data Generation:

Created a text file data/keyValuePairs.txt with 10,000 lines of random key-value pairs, where keys are random uppercase letters and values are random integers.

2. Spark Operations:
- groupByKey():
    - Groups values by key and calculates the average.
    - Time taken: 2.88 seconds.
    - Result:
```python
[('N', 5023.275462962963), ('O', 4956.304785894206), ('C', 4970.28493150685), ...]
```
- reduceByKey():
    - Combines values by key and calculates the average using a tuple of (sum, count).
    - Time taken: 2.67 seconds.
    - Result:
```python
[('N', 5023.275462962963), ('O', 4956.304785894206), ('C', 4970.28493150685), ...]
```
3. Comparison:
- Both methods produced identical results.
- reduceByKey() was slightly faster.
### Key Insights:
- reduceByKey() is generally preferred for performance when computing aggregate functions due to its ability to reduce data in intermediate stages.
- groupByKey() can be more expensive as it shuffles all values with the same key to a single reducer.

## Exercise 2: Prime Number Identification in a Large Dataset
**Summary**
- **Objective**: Identify all prime numbers from a dataset of 10,000,000 arbitrary numbers and save them to a new text file.

1. Data Generation:

Created a text file data/numbers.txt with 10,000,000 random numbers ranging from 1 to 100,000,000.

2. Spark Operations:

- Prime Number Detection:

Converted the text file into an RDD.
Applied a filter function to check for prime numbers using the is_prime function.
- Results:

Collected prime numbers from the dataset.
- Output File:

Saved the identified prime numbers to a new text file.
### Key Insights:
- Prime number detection is computationally intensive, especially for large datasets.
- Spark's distributed computing capability allows for efficient processing of large-scale data but can be limited by the performance of the is_prime function.
- Ensure that when running these operations, sufficient resources and memory are available to handle the large dataset and Spark operations efficiently.