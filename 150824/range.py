from pyspark import SparkContext, SparkConf
import pandas as pd

conf = SparkConf().setAppName("RangePartitionerExample").setMaster("local")
sc = SparkContext(conf=conf)

# Sample skewed data with natural ordering 
# data = [(i, f"value_{i}") for i in range(100)]
# data = [(i, f"value_{i}") for i in [1, 2, 3, 10, 20, 30, 40, 50, 100, 200]]
data = pd.read_csv('data.csv')
data = data['price'].sort_values()
data = data.tolist()
# make data into key-value pairs
data = [(i, f"value_{i}") for i in data]
# print(data)
rdd = sc.parallelize(data, 4)

# Custom range partitioner
def range_partitioner(key):
    if key < 10000:
        return 0
    elif 10000 <= key < 20000:
        return 1
    elif 20000 <= key < 40000:
        return 2
    else:
        return 3

partitioned_rdd = rdd.partitionBy(4, partitionFunc=range_partitioner)

print("Number of items per partition after RangePartitioning:",partitioned_rdd.glom().map(len).collect())
