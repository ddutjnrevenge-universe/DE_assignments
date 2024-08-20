<!-- Số core/executor > số executor/worker
 
Số partition = bội số worker -> tính toán phân tán
Số partition/worker = bội số executor
=> Số partition = n * (số worker * số executor/worker) với n là số nguyên dương.
 
Số executor/worker = (Số cores/worker) / (Số cores/executor)

Chạy code đó trên cùng cluster, nhưng giờ mỗi worker có
1. Số executor/worker > số worker/cluster (6>3)
2. Số core/executor > số executor/worker (6>1)
so sánh running time với trường hợp trên. Trong TH trên, số executor/worker = 1. Có thể x6 là số partition phù hợp trong TH này nhưng so với số (1. và 2.) thì có thể không. -->
# 1. "Difference" between `repartition down` and `coalesce`
## Repartition
- **Function:** repartition(n) allows you to increase or decrease the number of partitions to a specific number (n), and it involves a full shuffle of data across the network.
- **Operation Type**: expensive operation because it redistributes all data across the partitions, leading to a network shuffle.
- **Use Case:** used when you want to **`increase the number of partitions`** (for example, after reading a large dataset to improve parallelism) or **`evenly distribute data across partitions`** (if the current partitioning is skewed or not optimal).
## Coalesce
- **Function:** coalesce(n) is used to reduce the number of partitions in a DataFrame or RDD by merging existing partitions. Unlike repartition, coalesce avoids a full shuffle and only merges adjacent partitions.
- **Operation Type:** It is a more efficient operation than repartition because it avoids a full shuffle, only consolidating partitions.
- **Use Case:** It is used when you want to **`reduce the number of partitions`** (e.g., after a large reduction in data size) but want to **`avoid the cost of a full shuffle`**. It is particularly useful when the current number of partitions is unnecessarily high, causing overhead.

## When to Use Which?
- Use coalesce for efficient reduction of partitions without a full shuffle.
- Use repartition when you need to either increase partitions or ensure an even distribution, accepting the cost of a shuffle.

## Keynote: 
Even though coalesce is available, you might still need repartition when:
- The current partitioning is heavily skewed or uneven, and you want to create evenly distributed partitions.
- Need to strictly control the number of partitions after transformations that might have caused imbalance, even if it means incurring the cost of a shuffle.

# 2. Figure out how to use `HashPartitioner` and `RangePartitioner` on skew data.
In Spark, data are split into chunk of rows and stored on worker nodes, each "chunk" is called a **partition** and a given wormer can have any number of partitions of any size. (but it's best to evenly spread out the data so that each worker has an equal amount of data to process)

-> When the data are not balanced between workers, we call the data “skewed”

## Why care about "skewed" data?
- Slow stages/tasks runtime: certain operations may work with too much data over others
- Spill data to disk: if data not fit in memory on a worker it will be written to disk and takes much longer
- OOM

->  "Skewed" data: uneven utilization of compute and memory resources

## `HashPartitioner`
- Partition data based on the hash of the key, assigns each key-value pair to a partition based on the hash value of the key modulo the number of partitions
- Use HashPartitioner when your key distribution is relatively uniform or when want to evenly distribute data across partitions to avoid skew.
- Particularly useful for key-based operations like `joins`, `groupBy`, or `reduceByKey`, where evenly distributed keys are crucial for performance.
### Example:
```python
# Simulate HashPartitioner by partitioning using a hash function
# as Spark’s HashPartitioner is not directly available in the Python API
def hash_partitioner(key):
    return hash(key) % 4 
hash_partitioned_rdd = rdd.partitionBy(4, partitionFunc=hash_partitioner)
```
## `RangePartitioner`
- Distribute data based on ranges of keys. It is more suitable when the keys have a natural ordering (e.g., numbers, strings).
- Divide the key space into contiguous ranges and assigns each range to a partition. 
- Particularly useful where need sorted data or want to minimize skew by defining explicit ranges.
### Example: 
```python
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

range_partitioned_rdd = rdd.partitionBy(4, partitionFunc=range_partitioner)
```
## Handling Skewed Data
### Identifying Skew:
Before applying a partitioner, identify if  data is skewed.(`countByKey()` or `glom()` to inspect how keys are distributed across partitions)
### Dealing with Skew:
`HashPartitioner`: If keys are skewed, `HashPartitioner` might still cause imbalance if the hash values of the keys are also skewed.

- **Salt the keys**: Append a random prefix to keys before partitioning to spread them more evenly across partitions.
- **Custom Partitioning Logic**: Implement a custom partitioner that can distribute specific skewed keys more evenly.

`RangePartitioner`: If using `RangePartitioner`, must ensure that the range boundaries are chosen to avoid large data concentrations in specific partitions.
- **Pre-sample the data**: Pre-sample a subset of the data to estimate the distribution and set more balanced range boundaries.
- **Custom Ranges**: Define custom ranges that account for skewed data distributions.

### Example: Mitigating Skew with HashPartitioner and Salting
```python 
# Salt the keys to distribute the skewed data
def salt_key(key, num_salts=4):
    salt = random.randint(0, num_salts-1)
    return (f"{salt}_{key}", key)

salted_partitioned_rdd = rdd.map(lambda x: (salt_key(x[0]),x[1])).partitionBy(4, partitionFunc=hash_partitioner)
```

# 3. Study the memory management in spark

## Memory Allocation

- Overhead memo: shuffle exchange/ reading partition data from remote storage (network read buffer)

### Driver memory

- `spark.driver.memory` (e.g. = 1GB) → JVM memory
- `spark.driver.memoryOverhead` = 0.1 (default is 0.1) (max 10% or 384MB)
    
    → Total memory for the container is 1GB + 384MB
    
    
    - **Overhead memory** is used by container process or any other non JVM process within the container
    - **Spark driver** uses all JVM heap but nothing from overhead

### Executor memory

- Total memory allocated to the executor container is sum of:
    1. Overhead memo: `spark.executor.memoryOverhead`
    2. Heap memo: `spark.executor.memory`
    3. Off Heap memo: `spark.memory.offHeap.size`
        - Adding off-heap memo is an indirect method of increasing the executor and storage memo pools
        
        → If needed it will be used to buffer Spark dataframe operations and cache the dataframes
        
    
    
    1. PySpark memo: `spark.executor.pyspark.memory`
- E.g. ask for executor memo = 8gb → overhead = 10% = 800mb (by default offheapmemo and pysparkmemo is 0) ⇒ total container memo: 8800mb
    - If worker node is a 6GB machine → YARN cannot allocate a 8GB container on a 6GB machine → not enough physical memo
    
    ⇒ Before asking for driver or executor memo, should check with your cluster admin for maximum allowed value

- In this example, Spark driver cannot use more than 4GB & non JVM workload in container cannot use more than 400mb → container cannot use more than 4.4gb of memory in total
- Executor JVM cannot use more than 8GB & non JVM processes cannot use more than 800mb → container cannot use more than 8.8gb of memory
- What is PySpark executor memory? → PySpark is not a JVM process, so get nothing from jvm memo, all PySpark executor have is 800mb of overhead memo, while 300-400mb of this is constantly consumed by the container processes and other internal processes ⇒ **Get approximately 400mb in total**

## Memory Management

- Executor memory includes JVM heap and Overhead

### JVM Heap

- 3 parts:
    
    `spark.executor.memory` 
    
    `spark.executor.cores` 
    
    
    1. **Reserved memo**: fixed reserve for Spark Engine
    2. **Spark Memory**: (by default: `spark.memory.fraction` = 0.6) 
        
        <aside>
        ❗ 0.6 of (**total executor memory - reserved memory)**
        
        </aside>
        
        - Used for DataFrame (**Operations + Caching)**
        - Seperated into 2 subpools
            1. **Storage Memo pool**: (default:`spark.memory.storageFraction` = 0.5)
            
            → Cache memo for DataFrame
            
            - long-term
            1.  **Executor Memo pool**: the rest
            
            → Buffer memo for DataFrame operations (e.g. aggregating or performing some calculation)
            
            - Short-lived: used for operations and free immediately as soon as execution complete
    3. **User Memory**: the rest (0.4 by default)
        - **User-defined data structures** (hash maps,…)
        - **Spark internal metadata**
        - **UDFs created by user**
        - **RDD conversion operations**
            - If using DataFrame operations, this DO NOT USE user memo even if the df is internally translated and compiled into RDD
            - Using user memo only if **apply RDD operations directly** in your code
        - **RDD linage and dependency**

## Core view

- E.g. we have `spark.executor.cores` =4

→ have 4 slots/threads equivalent to 4 tasks that can run in parallel 

(all these slots are threads within the same JVM)

- 4 threads to share 2 memory pools
- Before spark 1.6: equally divided to all the slots
- Later: Unified memory manager
    - tries to implement fair allocation amongst the **active tasks**
    - nothing reserved for any task        
    - If executor memory fully consumed → memory manager also allocate executor memory from storage memory if available and vice versa
        

