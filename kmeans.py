import random
import math

# Function to calculate the Euclidean distance between two points
def euclidean_distance(point1, point2):
    return math.sqrt((point1['x'] - point2['x'])**2 + (point1['y'] - point2['y'])**2)

# Function to assign each point to the nearest centroid
def assign_clusters(dataset, centroids):
    clusters = []
    for point in dataset:
        nearest_centroid_index = 0
        min_distance = euclidean_distance(point, centroids[0])
        
        for i in range(1, len(centroids)):
            distance = euclidean_distance(point, centroids[i])
            if distance < min_distance:
                min_distance = distance
                nearest_centroid_index = i
                
        clusters.append(nearest_centroid_index)
    
    return clusters

# Function to update centroids based on the mean of their assigned points
def update_centroids(dataset, clusters, k):
    new_centroids = []
    for i in range(k):
        assigned_points = [dataset[j] for j in range(len(dataset)) if clusters[j] == i]
        
        if len(assigned_points) == 0:
            new_centroids.append({'x': random.uniform(-10, 10), 'y': random.uniform(-10, 10)})
        else:
            mean_x = sum(point['x'] for point in assigned_points) / len(assigned_points)
            mean_y = sum(point['y'] for point in assigned_points) / len(assigned_points)
            new_centroids.append({'x': mean_x, 'y': mean_y})
    
    return new_centroids

# Random initialization
def initialize_random(dataset, k):
    return random.sample(dataset, k)

# Farthest first initialization
def initialize_farthest_first(dataset, k):
    centroids = [random.choice(dataset)]  # Start with one random centroid
    
    while len(centroids) < k:
        max_distance = -1
        farthest_point = None
        
        # Find the point farthest from any existing centroid
        for point in dataset:
            min_distance_to_centroids = min(euclidean_distance(point, c) for c in centroids)
            if min_distance_to_centroids > max_distance:
                max_distance = min_distance_to_centroids
                farthest_point = point
        
        centroids.append(farthest_point)
    
    return centroids

# KMeans++ initialization
def initialize_kmeans_plus_plus(dataset, k):
    centroids = [random.choice(dataset)]  # Start with one random centroid
    
    while len(centroids) < k:
        # Calculate distances to nearest centroid
        distances = [min(euclidean_distance(point, c)**2 for c in centroids) for point in dataset]
        total_distance = sum(distances)
        
        # Pick a new centroid based on weighted probability
        rand_val = random.uniform(0, total_distance)
        cumulative_sum = 0
        
        for i, point in enumerate(dataset):
            cumulative_sum += distances[i]
            if cumulative_sum >= rand_val:
                centroids.append(point)
                break
    
    return centroids

# Manual initialization
# Here `user_selected_points` would be a list of manually chosen points as {'x': x_val, 'y': y_val}.
def initialize_manual(user_selected_points, k):
    return user_selected_points[:k]

# Function to perform one step of the KMeans algorithm
def kmeans_step(dataset, centroids, k):
    clusters = assign_clusters(dataset, centroids)
    new_centroids = update_centroids(dataset, clusters, k)
    return clusters, new_centroids

# Function to run KMeans until convergence
def run_kmeans_to_convergence(dataset, centroids, k, max_iterations=100):
    iterations = 0
    while iterations < max_iterations:
        clusters = assign_clusters(dataset, centroids)
        new_centroids = update_centroids(dataset, clusters, k)
        
        # Check for convergence (if centroids have not changed)
        if all(euclidean_distance(new, old) < 1e-4 for new, old in zip(new_centroids, centroids)):
            break
        
        centroids = new_centroids
        iterations += 1
        
    return clusters, centroids

