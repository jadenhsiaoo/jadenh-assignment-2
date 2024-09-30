from flask import Flask, request, jsonify, render_template
from kmeans import *
import random

# Use the previously defined helper functions, KMeans, and initialization methods
# Assuming all the Python KMeans code is placed above or imported here

app = Flask(__name__)

# Generate a random dataset within the range (-10, 10)
def generate_dataset(num_points=100):
    return [{'x': random.uniform(-10, 10), 'y': random.uniform(-10, 10)} for _ in range(num_points)]

@app.route('/')
def index():
    return render_template('index.html')

# API to generate dataset
@app.route('/api/generate-dataset', methods=['GET'])
def api_generate_dataset():
    num_points = int(request.args.get('num_points', 100))
    dataset = generate_dataset(num_points)
    return jsonify(dataset)

# API to perform KMeans clustering
@app.route('/api/kmeans', methods=['POST'])
def api_kmeans():
    data = request.json
    dataset = data.get('dataset')
    k = data.get('k')
    init_method = data.get('init_method')
    
    # Choose initialization method
    if init_method == 'random':
        centroids = initialize_random(dataset, k)
    elif init_method == 'farthest-first':
        centroids = initialize_farthest_first(dataset, k)
    elif init_method == 'kmeans++':
        centroids = initialize_kmeans_plus_plus(dataset, k)
    else:
        return jsonify({"error": "Invalid initialization method."}), 400
    
    # Run KMeans to convergence
    clusters, final_centroids = run_kmeans_to_convergence(dataset, centroids, k)
    
    return jsonify({
        'clusters': clusters,
        'centroids': final_centroids
    })

@app.route('/api/kmeans-initialize', methods=['POST'])
def api_kmeans_initialize():
    data = request.json
    dataset = data.get('dataset')
    k = data.get('k')
    init_method = data.get('init_method')
    
    # Choose initialization method
    if init_method == 'random':
        centroids = initialize_random(dataset, k)
    elif init_method == 'farthest-first':
        centroids = initialize_farthest_first(dataset, k)
    elif init_method == 'kmeans++':
        centroids = initialize_kmeans_plus_plus(dataset, k)
    else:
        return jsonify({"error": "Invalid initialization method."}), 400
    
    # Only return initialized centroids without running KMeans
    clusters = assign_clusters(dataset, centroids)
    
    return jsonify({
        'clusters': clusters,
        'centroids': centroids
    })

@app.route('/api/kmeans-step', methods=['POST'])
def api_kmeans_step():
    data = request.json
    dataset = data.get('dataset')
    centroids = data.get('centroids')
    k = data.get('k')
    
    # Perform one step of KMeans algorithm
    clusters = assign_clusters(dataset, centroids)
    new_centroids = update_centroids(dataset, clusters, k)
    
    return jsonify({
        'clusters': clusters,
        'centroids': new_centroids
    })


if __name__ == '__main__':
    app.run(debug=True, port=3000)
