import random
import time
from pyspark.sql import SparkSession
from pyspark.sql.functions import collect_list, struct
from scipy.spatial import ConvexHull
import pandas as pd

# Initialize Spark session
spark = SparkSession.builder.appName("ConvexHullPerParticleNoUDF").getOrCreate()

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

# Collect the DataFrame to the driver
grouped_data = grouped_df.collect()

# Define a function to compute convex hull (same as before)
def compute_convex_hull(points):
    points = [(p['x'], p['y']) for p in points]
    if len(points) < 3:
        return points  # Convex hull is the same as the points if less than 3 points
    hull = ConvexHull(points)
    hull_points = [points[i] for i in hull.vertices]
    return hull_points
# ------------------------------------------------------------
# Process each particle's points locally on the driver
results = []
for row in grouped_data:
    particle_id = row['particle_id']
    points = row['points']
    convex_hull = compute_convex_hull(points)
    results.append((particle_id, convex_hull))

# Convert the results back to a Spark DataFrame
result_df = spark.createDataFrame(results, ["particle_id", "convex_hull"])

result_df.show(10, truncate=False)

end_time = time.time()
execution_time = end_time - start_time
print(f"Execution time: {execution_time} seconds")

# Stop the Spark session
spark.stop()
