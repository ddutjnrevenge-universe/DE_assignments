from pyspark import SparkContext, SparkConf
from pyspark.rdd import RDD
import pandas as pd
import random

conf = SparkConf().setAppName("HashPartitionerExample").setMaster("local")
sc = SparkContext(conf=conf)

# Sample skewed data
# data = [(i % 5, f"value_{i}") for i in range(100)]
data = pd.read_csv('data.csv')
data = data['price'].sort_values()
data = data.tolist()
# make data into key-value pairs
data = [(i, f"value_{i}") for i in data]
# print(data)
rdd = sc.parallelize(data, 4)

# Simulate HashPartitioner by partitioning using a hash function
def hash_partitioner(key):
    return hash(key) % 4 
# What this function does is to return the remainder of the division of the hash of the key by 4.

# partitioned_rdd = rdd.partitionBy(4, partitionFunc=hash_partitioner)

# Salt the keys to distribute the skewed data
def salt_key(key, num_salts=4):
    salt = random.randint(0, num_salts-1)
    return (f"{salt}_{key}", key)

salted_partitioned_rdd = rdd.map(lambda x: (salt_key(x[0]),x[1])).partitionBy(4, partitionFunc=hash_partitioner)
# print("Number of items per partition after HashPartitioning:",partitioned_rdd.glom().map(len).collect())

print("Number of items per partition after salting and HashPartitioning:",salted_partitioned_rdd.glom().map(len).collect())