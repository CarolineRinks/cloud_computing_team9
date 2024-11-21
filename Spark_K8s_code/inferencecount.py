# Team 9
# Cloud Computing, Fall 2024
# 11/21/2024
# PA4 - Map Reduce with ML Pipeline

import sys
import json
from pyspark.sql import SparkSession

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: wordcount <file>", file=sys.stderr)
        sys.exit(-1)

    # Initialize Spark session
    spark = SparkSession.builder \
        .appName("InferenceErrorCount") \
        .getOrCreate()

    # Our data is saved as JSON file so we are loading it here
    data = spark.read.json(sys.argv[1])

    # Perform MapReduce logic
    # 1. Filter rows where GroundTruth != InferredValue (inference was wrong)
    filtered_data = data.filter(data.GroundTruth != data.InferredValue)

    # 2. Map step: Transform data to (ProducerID, 1) format
    mapped_data = filtered_data.rdd.map(lambda row: (row['ProducerID'], 1))

    # 3. Reduce step: Count occurrences per ProducerID
    reduced_data = mapped_data.reduceByKey(lambda a, b: a + b)

    # Collect and display the results
    results = reduced_data.collect()
    for producer, count in results:
        print(f"ProducerID: {producer}, Inference Errors: {count}")

    spark.stop()
