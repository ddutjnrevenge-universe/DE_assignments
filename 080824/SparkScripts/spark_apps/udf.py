import random
import time
from pyspark.sql import SparkSession
from pyspark.sql.functions import collect_list, struct, col
# from scipy.spatial import ConvexHull
from pyspark.sql.types import ArrayType, StructType, StructField, IntegerType

class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

# Utility function to find orientation of ordered triplet (p, q, r).
# 0 --> p, q, r are collinear
# 1 --> Clockwise
# 2 --> Counterclockwise
def orientation(p, q, r):
    val = (q.y - p.y) * (r.x - q.x) - (q.x - p.x) * (r.y - q.y)
    if val == 0:
        return 0  # collinear
    elif val > 0:
        return 1  # clockwise
    else:
        return 2  # counterclockwise

# Function to compute convex hull using the algorithm provided
def compute_convex_hull(points):
    points = [Point(p['x'], p['y']) for p in points]

    n = len(points)
    if n < 3:
        return [(p.x, p.y) for p in points]  # Convex hull is the same as the points if less than 3 points

    hull = []

    # Find the leftmost point
    l = 0
    for i in range(1, n):
        if points[i].x < points[l].x:
            l = i

    p = l
    while True:
        hull.append(points[p])

        q = (p + 1) % n
        for i in range(n):
            if orientation(points[p], points[i], points[q]) == 2:
                q = i

        p = q

        if p == l:
            break

    return [(p.x, p.y) for p in hull]

# Initialize Spark session
spark = SparkSession.builder.appName("ConvexHullPerParticle").getOrCreate()

# Generate sample data with 1,000,000 data points
num_points = 1000000
num_particles = 4
# set seed for reproducibility
random.seed(0)
data = [(random.randint(1, num_particles), random.randint(0, 1000), random.randint(0, 1000)) for _ in range(num_points)]

# Measure the execution time
start_time = time.time()

# Create DataFrame
columns = ["particle_id", "x", "y"]
df = spark.createDataFrame(data, columns)

# Group by particle_id and collect points
grouped_df = df.groupBy("particle_id").agg(
    collect_list(struct("x", "y")).alias("points")
)
# Print default partitions
print(f"Default partitions: {grouped_df.rdd.getNumPartitions()}")
# Repartition the DataFrame for parallel processing
# grouped_df = grouped_df.repartition(36)

# # Define a function to compute convex hull
# def compute_convex_hull(points):
#     points = [(p['x'], p['y']) for p in points]
#     if len(points) < 3:
#         return points  # Convex hull is the same as the points if less than 3 points
#     hull = ConvexHull(points)
#     hull_points = [points[i] for i in hull.vertices]
#     return hull_points
# ------------------------------------------------------------
# Register the UDF
hull_schema = ArrayType(StructType([StructField("x", IntegerType()), StructField("y", IntegerType())]))
compute_convex_hull_udf = spark.udf.register("compute_convex_hull", compute_convex_hull, hull_schema)

# Apply the UDF
result_df = grouped_df.withColumn("convex_hull", compute_convex_hull_udf(col("points")))

result_df.select("particle_id", "convex_hull").show(10, truncate=False)

end_time = time.time()
execution_time = end_time - start_time
print(f"Execution time: {execution_time} seconds")

# Stop the Spark session
spark.stop()
