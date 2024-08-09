from pyspark.sql import SparkSession
from pyspark import SparkConf, SparkContext
import time
import csv
import os

# Configuration for Spark
# conf = SparkConf().set("spark.executor.cores", "2")\
                #   .set("spark.executor.memory", "2g")\
                #    .set("spark.executor.instances", "3")\
                #   .set("spark.dynamicAllocation.enabled", "false")
# set number of cores in each worker is 2 
# given 3 workers, 36 cores in total, 6 cores for each worker, now just want to use 2 cores for each worker, 2gb memory for each worker
# so 6 cores used in total, 3 workers, 2gb memory for each worker
conf = SparkConf().set("spark.executor.cores", "2")\
                  .set("spark.executor.memory", "2g")\
                  .set("spark.executor.instances", "3")\
                  .set("spark.dynamicAllocation.enabled", "false")

sc = SparkContext(appName="Test", conf=conf)

from math import sqrt, ceil

def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, ceil(sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

# Start the timer
start_time = time.time()

# Path to the numbers file and output path
numbers_file = "/opt/spark/data/numbers.txt"
prime_numbers_rdd_output_path = "/opt/spark/data/results/prime_numbers_rdd.txt"

# Load the numbers and process them
numbers_rdd = sc.textFile(numbers_file)
num_partitions = 6 
numbers_rdd = numbers_rdd.repartition(num_partitions)  # Set the number of partitions
numbers_rdd = numbers_rdd.map(lambda x: int(x))
prime_numbers_rdd = numbers_rdd.filter(is_prime)
print(prime_numbers_rdd.collect())

# End the timer
end_time = time.time()
interval = end_time - start_time
print(f"Execution time: {interval} seconds")

# Check the number of workers
sc_java = sc._jsc.sc()
n_workers = len([executor.host() for executor in sc_java.statusTracker().getExecutorInfos()]) - 1

# Get memory status and executor count
executor_memory_status = sc_java.getExecutorMemoryStatus().keys()
executor_count = len([executor.host() for executor in sc_java.statusTracker().getExecutorInfos()]) - 1

# Print memory status and executor count
print(f"Executor memory status: {executor_memory_status}")
print(f"Executor count (excluding driver): {executor_count}")

# Path to the CSV file for logging
csv_file_path = "/opt/spark/data/results/execution_statistics.csv"

# Check if CSV file exists, if not, write the header
file_exists = os.path.isfile(csv_file_path)
with open(csv_file_path, mode='a', newline='') as file:
    writer = csv.writer(file)
    if not file_exists:
        writer.writerow(["Execution Time (s)", "Number of Workers","Number of Partitions",  "Executor Cores",  "Executor Memory"])

    # Write the statistics to the CSV file
    writer.writerow([interval, n_workers, num_partitions, conf.get("spark.executor.cores"), conf.get("spark.executor.memory")])

print(f"Statistics saved to {csv_file_path}")
