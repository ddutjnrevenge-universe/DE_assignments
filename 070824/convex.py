import random
import time
from pyspark.sql import SparkSession
from pyspark.sql.functions import collect_list, struct, col
from scipy.spatial import ConvexHull
from pyspark.sql.types import ArrayType, StructType, StructField, IntegerType

# Initialize Spark session
spark = SparkSession.builder.appName("ConvexHullPerParticle").getOrCreate()

# Generate sample data with 1,000,000 data points
num_points = 1000000
num_particles = 10000  
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

# Define a function to compute convex hull
def compute_convex_hull(points):
    points = [(p['x'], p['y']) for p in points]
    if len(points) < 3:
        return points  # Convex hull is the same as the points if less than 3 points
    hull = ConvexHull(points)
    hull_points = [points[i] for i in hull.vertices]
    return hull_points
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
