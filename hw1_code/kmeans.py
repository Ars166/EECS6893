import operator
import sys
from pyspark import SparkConf, SparkContext
import numpy as np
import matplotlib.pyplot as plt
from scipy import linalg
from sklearn.manifold import TSNE

# Macros.
MAX_ITER = 20
DATA_PATH = "gs://6893_bucket_1/HW1/data.txt"
C1_PATH = "gs://6893_bucket_1/HW1/c1.txt"
C2_PATH = "gs://6893_bucket_1/HW1/c2.txt"
NORM = 2


# Helper functions.
def closest(p, centroids, norm):
    """
    Compute closest centroid for a given point.
    Args:
        p (numpy.ndarray): input point
        centroids (list): A list of centroids points
        norm (int): 1 or 2
    Returns:
        int: The index of closest centroid.
    """
    closest_c = min([(i, linalg.norm(p - c, norm))
                    for i, c in enumerate(centroids)],
                    key=operator.itemgetter(1))[0]
    return closest_c


# K-means clustering
def kmeans(data, centroids, norm=2):
    """
    Conduct k-means clustering given data and centroid.
    This is the basic version of k-means, you might need more
    code to record cluster assignment to plot TSNE, and more
    data structure to record cost.
    Args:
        data (RDD): RDD of points
        centroids (list): A list of centroids points
        norm (int): 1 or 2
    Returns:
        RDD: assignment information of points, a RDD of (centroid, (point, 1))
        list: a list of centroids
        and define yourself...
    """
    # iterative k-means
    costs=[]
    for _ in range(MAX_ITER):
        # Transform each point to a combo of point, closest centroid, count=1
        # point -> (closest_centroid, (point, 1))
        combo = data.map(lambda point: (closest(point, centroids, norm), (point, 1)))

        cost = combo.map(lambda x: linalg.norm(x[1][0] - centroids[x[0]], norm)).sum()
        costs.append(cost)

        # Re-compute cluster center
        # For each cluster center (key), aggregate its values
        # by summing up points and count
        aggregated_combo = combo.reduceByKey(lambda a, b: (a[0] + b[0], a[1] + b[1]))
        
        # Average the points for each centroid: divide sum of points by count
        updated_centroids = aggregated_combo.mapValues(lambda value: value[0] / value[1])
        # Use collect() to turn RDD into list
        centroids = updated_centroids.map(lambda x: x[1]).collect()

    out = combo.map(lambda x: (x[0],x[1][0]))
    print(costs)

    return costs, centroids, out



def main():
    # Spark settings
    conf = SparkConf()
    sc = SparkContext(conf=conf)

    # Load the data, cache this since we're accessing this each iteration
    data = sc.textFile(DATA_PATH).map(
            lambda line: np.array([float(x) for x in line.split()])
            ).cache()

    # Load the initial centroids c1, split into a list of np arrays
    centroids1 = sc.textFile(C1_PATH).map(
            lambda line: np.array([float(x) for x in line.split(' ')])
            ).collect()

    # Load the initial centroids c2, split into a list of np arrays
    centroids2 = sc.textFile(C2_PATH).map(
            lambda line: np.array([float(x) for x in line.split(' ')])
            ).collect()

    cost1, centroid1, out = kmeans(data, centroids1, norm=2)
    points = out.map(lambda x: x[1])
    tsne = TSNE(n_components=2, random_state=42)
    low_dimensional_points = tsne.fit_transform(points)
    clusters = out.map(lambda x: x[0]).collect()

    plt.figure(figsize=(8, 6))
    plt.scatter(low_dimensional_points[:, 0], low_dimensional_points[:, 1], c=clusters, cmap='viridis')
    plt.title('t-SNE Visualization')
    plt.xlabel('t-SNE Dimension 1')
    plt.ylabel('t-SNE Dimension 2')
    plt.colorbar()
    plt.show()



    sc.stop()



    # TODO: Run the kmeans clustering and complete the HW

if __name__ == "__main__":
    main()
