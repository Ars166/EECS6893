from pyspark.sql import SparkSession
from pyspark.ml.feature import StringIndexer, OneHotEncoder, VectorAssembler
from pyspark.ml import Pipeline
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import BinaryClassificationEvaluator, MulticlassClassificationEvaluator

from pyspark.sql.functions import col

# Initialize Spark session
spark = SparkSession.builder \
    .appName("Binary Classification") \
    .getOrCreate()

# Step 1: Data Loading
# Read the CSV file into a DataFrame with specified schema and column names
data = spark.read.csv("path/to/your/adult.csv", header=False, inferSchema=True)
data = data.withColumnRenamed("_c0", "age") \
    .withColumnRenamed("_c1", "workclass") \
    .withColumnRenamed("_c2", "fnlwgt") \
    .withColumnRenamed("_c3", "education") \
    .withColumnRenamed("_c4", "education_num") \
    .withColumnRenamed("_c5", "marital_status") \
    .withColumnRenamed("_c6", "occupation") \
    .withColumnRenamed("_c7", "relationship") \
    .withColumnRenamed("_c8", "race") \
    .withColumnRenamed("_c9", "sex") \
    .withColumnRenamed("_c10", "capital_gain") \
    .withColumnRenamed("_c11", "capital_loss") \
    .withColumnRenamed("_c12", "hours_per_week") \
    .withColumnRenamed("_c13", "native_country") \
    .withColumnRenamed("_c14", "income")

# Step 2: Data Preprocessing
# Convert categorical variables into numeric using StringIndexer and OneHotEncoder
categorical_cols = ["workclass", "education", "marital_status", "occupation", "relationship", "race", "sex", "native_country", "income"]

indexers = [StringIndexer(inputCol=col, outputCol=col + "_index", handleInvalid="keep") for col in categorical_cols]
encoder = OneHotEncoder(inputCols=[indexer.getOutputCol() for indexer in indexers], outputCols=[col + "_encoded" for col in categorical_cols])

# Assemble features into a single vector
feature_cols = ["age", "fnlwgt", "education_num", "capital_gain", "capital_loss", "hours_per_week"] + [col + "_encoded" for col in categorical_cols[:-1]]
assembler = VectorAssembler(inputCols=feature_cols, outputCol="features")

# Create a pipeline for preprocessing
pipeline = Pipeline(stages=indexers + [encoder, assembler])

# Fit and transform the data using the pipeline
preprocessed_data = pipeline.fit(data).transform(data)

# Split
train_data, test_data = preprocessed_data.randomSplit([0.7, 0.3], seed=100)


#Logistic Regression
lr = LogisticRegression(labelCol="income_index", featuresCol="features")

# Train the model
lr_model = lr.fit(train_data)
binary_evaluator = BinaryClassificationEvaluator(labelCol="income_index", rawPredictionCol="prediction", metricName="areaUnderROC")
multiclass_evaluator = MulticlassClassificationEvaluator(labelCol="income_index", predictionCol="prediction", metricName="accuracy")
predictions = lr_model.transform(test_data)

if "prediction" in predictions.schema.names:  # 判断预测结果的列是否存在
    accuracy = multiclass_evaluator.evaluate(predictions)
    print(f"准确率: {accuracy}")
else:
    auc = binary_evaluator.evaluate(predictions)
    print(f"AUC: {auc}")


