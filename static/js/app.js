document.addEventListener("DOMContentLoaded", function() {
    const initMethodSelect = document.getElementById("init-method");
    const generateBtn = document.getElementById("generate-btn");
    const stepBtn = document.getElementById("step-btn");
    const convergeBtn = document.getElementById("converge-btn");
    const resetBtn = document.getElementById("reset-btn");
    const numClustersInput = document.getElementById("num-clusters");

    let dataset = [];
    let centroids = [];
    let clusters = [];
    let k = 3;
    let stepInitialized = false;
    let isStepping = false; // Flag to indicate if we are in step mode

    // Generate unique colors for clusters
    function generateUniqueColors(k) {
        const colors = [];
        for (let i = 0; i < k; i++) {
            colors.push(`hsl(${Math.floor((i * 360) / k)}, 70%, 50%)`);
        }
        return colors;
    }

    // Initialize centroids based on user-selected method
    function initializeCentroids() {
        k = parseInt(numClustersInput.value, 10);
        const initMethod = initMethodSelect.value;
    
        // Reset step initialization
        stepInitialized = true;
    
        return fetch('/api/kmeans-initialize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                dataset: dataset,
                k: k,
                init_method: initMethod
            })
        })
        .then(response => response.json())
        .then(data => {
            clusters = data.clusters;
            centroids = data.centroids;
            plotClusters(); // Plot the initial clusters and centroids
        })
        .catch(err => console.error('Error initializing centroids:', err));
    }    

    // Function to perform one step of the KMeans algorithm
    function stepKMeans() {
        return fetch('/api/kmeans-step', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                dataset: dataset,
                centroids: centroids,
                k: k
            })
        })
        .then(response => response.json())
        .then(data => {
            const newCentroids = data.centroids;
            const newClusters = data.clusters;

            // Check for convergence
            const isConverged = newCentroids.every((c, index) => {
                return Math.abs(c.x - centroids[index].x) < 1e-4 && Math.abs(c.y - centroids[index].y) < 1e-4;
            });

            centroids = newCentroids;
            clusters = newClusters;

            plotClusters(); // Re-plot with new clusters and centroids

            return isConverged;
        })
        .catch(err => console.error('Error stepping through KMeans:', err));
    }

    // Step through KMeans with a delay
    async function autoStepKMeans() {
        isStepping = true;

        while (true) {
            const converged = await stepKMeans();

            if (converged) {
                alert('KMeans algorithm has converged!');
                isStepping = false;
                break;
            }

            // Wait for 0.5 seconds before the next step
            await new Promise(resolve => setTimeout(resolve, 500));

            // If the user cancels stepping, exit the loop
            if (!isStepping) break;
        }
    }

    // Run KMeans directly to convergence without any delay
    async function runKMeansToConvergence() {
        if (!stepInitialized) await initializeCentroids();

        let converged = false;
        while (!converged) {
            converged = await stepKMeans();
        }

        alert('KMeans algorithm has converged!');
    }

    // Plot dataset (initially with no clusters)
    function plotDataset() {
        const plotData = [{
            x: dataset.map(point => point.x),
            y: dataset.map(point => point.y),
            mode: 'markers',
            type: 'scatter',
            marker: { size: 10, color: '#5e81ac' }
        }];

        const layout = {
            xaxis: { range: [-11, 11] },
            yaxis: { range: [-11, 11] },
            margin: { l: 40, r: 40, t: 40, b: 40 },
            autosize: true,
            plot_bgcolor: '#eaeaea',
            paper_bgcolor: '#eaeaea',
            showlegend: false
        };

        Plotly.newPlot('plot-area', plotData, layout);
    }

    // Plot clusters and centroids
    function plotClusters() {
        const clusterColors = generateUniqueColors(k);

        // Plot points colored by their cluster assignment
        const pointsData = clusters.map((clusterIndex, i) => ({
            x: [dataset[i].x],
            y: [dataset[i].y],
            mode: 'markers',
            type: 'scatter',
            marker: { size: 10, color: clusterColors[clusterIndex % clusterColors.length] }
        }));

        // Plot centroids
        const centroidsData = [{
            x: centroids.map(c => c.x),
            y: centroids.map(c => c.y),
            mode: 'markers',
            type: 'scatter',
            marker: { size: 15, color: '#ff0000', symbol: 'x' }
        }];

        const layout = {
            xaxis: { range: [-11, 11] },
            yaxis: { range: [-11, 11] },
            margin: { l: 40, r: 40, t: 40, b: 40 },
            autosize: true,
            plot_bgcolor: '#eaeaea',
            paper_bgcolor: '#eaeaea',
            showlegend: false
        };

        Plotly.newPlot('plot-area', [...pointsData, ...centroidsData], layout);
    }

    // Fetch dataset from the server
    function fetchDataset() {
        fetch('/api/generate-dataset?num_points=100')
            .then(response => response.json())
            .then(data => {
                dataset = data;
                plotDataset();
            })
            .catch(err => console.error('Error generating dataset:', err));
    }

    // Event listeners
    generateBtn.addEventListener("click", fetchDataset);
    stepBtn.addEventListener("click", () => {
        // Initialize centroids if not done yet, and start stepping through KMeans
        if (!stepInitialized) {
            initializeCentroids().then(() => {
                // Start stepping through only after centroids are initialized
                if (!isStepping) autoStepKMeans();
            });
        } else if (!isStepping) {
            // If already initialized, start stepping through immediately
            autoStepKMeans();
        }
    });    
    convergeBtn.addEventListener("click", runKMeansToConvergence);
    resetBtn.addEventListener("click", () => {
        centroids = [];
        clusters = [];
        stepInitialized = false;
        isStepping = false; // Stop any ongoing stepping
        plotDataset(); // Redraw plot with original dataset only
    });

    // Initialize with a default dataset
    fetchDataset();
});
