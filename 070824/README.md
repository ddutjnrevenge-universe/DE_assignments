# Overview

This Spark job calculates the convex hull for a set of 2D points associated with different particles. The convex hull is the smallest convex boundary enclosing a set of points.

### Steps Involved:
- **`Execution time`**: 39.395299673080444 seconds 
1. **Data Generation**: Creates a dataset with 1,000,000 points, each associated with one of 10,000 particles.
2. **DataFrame Creation**: Loads the data into a Spark DataFrame with columns `particle_id`, `x`, and `y`.
3. **Grouping Data**: Groups points by `particle_id`, collecting them into lists.
4. **UDF Application**: A User-Defined Function (UDF) computes the convex hull for each particle's points. The UDF is applied to create a new `convex_hull` column in the DataFrame.
5. **Execution Time Measurement**: Measures the time taken to complete the job.

## UDF Benefits

- **Custom Processing**: UDFs allow complex, non-SQL operations like convex hull computation.
- **Parallel Processing**: UDFs run in parallel across the Spark cluster, enhancing performance.
- **Integration & Reusability**: UDFs integrate seamlessly with Spark's DataFrame API and can be reused across jobs.
- **Scalability**: Leveraging Spark's distributed processing, UDFs handle large datasets efficiently.


## Experimenting running the same job without using UDF
- **`Execution time`**: 48.40280628204346 seconds
### Why does it take longer?
- **Collecting Data to Driver**: The `grouped_df.collect()` statement collects the entire DataFrame to the driver node. This operation is expensive and can cause memory issues if the dataset is large. In contrast, when using a UDF, the data remains distributed across the cluster, and the processing happens on the worker nodes.

- **Processing Locally**: The convex hull computation is done locally on the driver for each particle. This approach doesn't leverage Spark's parallel processing capabilities, leading to a potential bottleneck on the driver node.

- **Re-distributing Data**: After processing the data locally, the results are converted back into a Spark DataFrame and distributed across the cluster. This step is redundant and inefficient, as it involves unnecessary data movement between the driver and the cluster.

<!-- ### Benefits of Using UDF (Highlighted by This Example)
- **Distributed Processing:** UDFs allow you to perform the convex hull computation in parallel across the cluster, making the process faster and more scalable. In contrast, processing data locally on the driver node can lead to bottlenecks and memory issues.

- **Scalability:** UDFs can handle large datasets efficiently by keeping the computation distributed. Collecting data to the driver, as shown in this example, limits the scalability of the application.

- **Memory Management:** By keeping the data distributed, UDFs avoid the risk of overwhelming the driver's memory, which can happen when large datasets are collected to the driver.

Using a UDF is significantly more efficient and scalable for this type of operation, as it leverages Spark's distributed processing capabilities, avoids unnecessary data movement, and minimizes the risk of driver node bottlenecks. -->

## Conclusion
Using UDFs in this Spark job is crucial for efficient and scalable convex hull computation. UDFs enable parallel processing, minimize data movement, and avoid driver bottlenecks, making them significantly more effective for large-scale operations.
