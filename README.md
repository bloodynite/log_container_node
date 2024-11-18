# Download Kubernetes Logs by Node

This Python script allows you to download `.log` files from containers running on a Kubernetes cluster, organized by node. The logs are saved to a folder on your desktop, with subfolders for each node.

## Features

- Automatically detects nodes in the Kubernetes cluster.
- Selects the first pod running on each node to download logs.
- Downloads all `.log` files from the specified container path.
- Organizes the downloaded log files by node and maintains their original filenames.

## Prerequisites

- Python 3.x
- Kubernetes Python client (`kubernetes` package)
- `kubectl` installed and configured to access your Kubernetes cluster

### Install Dependencies

To install the necessary Python packages, run:

```sh
pip install kubernetes
```

Ensure that `kubectl` is installed and correctly configured to access your Kubernetes cluster.

## Usage

The script can be run as follows:

```python
python log-container-nodos.py
```

### Parameters

- `namespace`: The Kubernetes namespace to query for pods. Defaults to `"default"`.
- `container_path`: The path inside the container where the log files are stored. Defaults to `"/container"`.
- `destination_path`: The path on your local machine where the logs should be saved. If not provided, logs are saved to your desktop in a folder named `K8sLogs_<timestamp>`.

### Example

```python
# Run the script with default settings
python log-container-nodos.py

# Run the script with a custom namespace and container path
python log-container-nodos.py --namespace my-namespace --container-path /var/log
```

## Output

- Logs are saved to a folder named `K8sLogs_<timestamp>` on your desktop.
- Inside the folder, each node has a subfolder containing the log files for that node.
- Each log file retains its original filename, and the successful copy of each log is indicated in the terminal.

### Example Output

```
Detected nodes in the cluster:
  - Node: node1, IP: 10.90.10.154
  - Node: node2, IP: 10.90.10.126
Processing node: node1 (IP: 10.90.10.154), using pod: pod1
    Log files found in pod pod1:
    - /container/log1.log
    - /container/log2.log
    Successfully copied log1.log to 10_90_10_154/log1.log
    Successfully copied log2.log to 10_90_10_154/log2.log
```

## Notes

- Make sure your Kubernetes configuration (`kubeconfig`) is set up correctly, as the script will load this configuration to authenticate with the cluster.
- The script uses `kubectl cp` to copy files, so `kubectl` must be in your system path.

## Disclaimer

This script is intended for use in controlled environments. Always ensure your Kubernetes configuration and log data are secured appropriately before sharing or uploading them to public repositories.

