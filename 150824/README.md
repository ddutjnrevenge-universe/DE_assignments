Số core/executor > số executor/worker
 
Số partition = bội số worker -> tính toán phân tán
Số partition/worker = bội số executor
=> Số partition = n * (số worker * số executor/worker) với n là số nguyên dương.
 
Số executor/worker = (Số cores/worker) / (Số cores/executor)

Chạy code đó trên cùng cluster, nhưng giờ mỗi worker có
1. Số executor/worker > số worker/cluster (6>3)
2. Số core/executor > số executor/worker (6>1)
so sánh running time với trường hợp trên. Trong TH trên, số executor/worker = 1. Có thể x6 là số partition phù hợp trong TH này nhưng so với số (1. và 2.) thì có thể không.
Mọi người cũng nên tìm hiểu thêm về memory management trong spark nữa.
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






