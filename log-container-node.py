import subprocess
import os
import pathlib
from datetime import datetime
from kubernetes import client, config

def download_logs_from_pods_by_node_ip(namespace="default", container_path="/container", destination_path=None):
    # Use explicit desktop path for Windows
    if destination_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    destination_path = os.path.join(os.path.expanduser("~"), "Desktop", f"K8sLogs_{timestamp}")
    
    # Ensure absolute path and use forward slashes
    destination_path = pathlib.Path(destination_path).resolve().as_posix()
    
    # Configure cluster access
    try:
        config.load_kube_config()
    except Exception as e:
        print(f"Error loading Kubernetes config: {e}")
        return
    
    # Initialize Kubernetes API clients
    v1 = client.CoreV1Api()
    
    # Get list of nodes
    try:
        nodes = v1.list_node()
    except Exception as e:
        print(f"Error listing nodes: {e}")
        return
    
    if not nodes.items:
        print(f"No nodes found in the cluster")
        return
    
    # Show detected nodes
    print("Detected nodes in the cluster:")
    for node in nodes.items:
        node_ips = [addr.address for addr in node.status.addresses if addr.type in ['InternalIP', 'ExternalIP']]
        node_ip = node_ips[0] if node_ips else "No IP found"
        print(f"  - Node: {node.metadata.name}, IP: {node_ip}")
    
    # Create base destination directory with timestamp if it doesn't exist
    try:
        os.makedirs(destination_path, exist_ok=True)
    except Exception as e:
        print(f"Error creating destination directory: {e}")
        return
    
    # Process each node
    for node in nodes.items:
        # Get node IP address (preferring internal IP)
        node_ips = [addr.address for addr in node.status.addresses if addr.type in ['InternalIP', 'ExternalIP']]
        if not node_ips:
            print(f"No IP found for node {node.metadata.name}")
            continue
        
        # Use the first IP address (preferring internal)
        node_ip = node_ips[0].replace('.', '_')  # Replace dots with underscores for folder name
        node_logs_path = os.path.join(destination_path, node_ip)
        node_logs_path = pathlib.Path(node_logs_path).resolve().as_posix()
        
        # Create node-specific directory
        try:
            os.makedirs(node_logs_path, exist_ok=True)
        except Exception as e:
            print(f"Error creating node log directory {node_logs_path}: {e}")
            continue
        
        # Get list of pods in the namespace
        try:
            pods = v1.list_namespaced_pod(namespace)
        except Exception as e:
            print(f"Error listing pods in namespace {namespace}: {e}")
            continue
        
        # Find the first pod running on this node
        pod = next((pod for pod in pods.items if pod.spec.node_name == node.metadata.name), None)
        
        if not pod:
            print(f"No pods found on node {node.metadata.name}")
            continue
        
        pod_name = pod.metadata.name
        print(f"Processing node: {node.metadata.name} (IP: {node_ips[0]}), using pod: {pod_name}")
        
        # List log files using kubectl directly
        list_command = [
            'kubectl',
            'exec',
            '-n',
            namespace,
            pod_name,
            '--',
            'sh',
            '-c',
            f'find {container_path} -maxdepth 1 -type f -name "*.log"'
        ]
        try:
            ls_output = subprocess.check_output(list_command, stderr=subprocess.STDOUT, universal_newlines=True)
        except subprocess.CalledProcessError as e:
            print(f"Error listing files in pod {pod_name}: {e.output}")
            continue
        
        # Filter log files
        log_files = [line.strip() for line in ls_output.split('\n') if line.strip().endswith('.log')]
        if not log_files:
            print(f"    No .log files found in {container_path} for pod {pod_name}")
            continue
        
        print(f"    Log files found in pod {pod_name}:")
        for log_file in log_files:
            print(f"    - {log_file}")
        
        # Copy each log file
        for log_file in log_files:
            # Use the log_file directly since it already contains the full path
            local_filename = os.path.basename(log_file)
            local_path = os.path.join(node_logs_path, local_filename)
            
            # Convert the local path to a relative path
            local_path_relative = os.path.relpath(local_path)
            
            cp_command = [
                'kubectl',
                'cp',
                f'{namespace}/{pod_name}:{log_file}',
                f'{local_path_relative}'
            ]
            try:
                result = subprocess.run(cp_command, capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"    Error copying {log_file}: {result.stderr}")
                else:
                    print(f"    Successfully copied {log_file} to {node_ip}/{local_filename}")
            except subprocess.CalledProcessError as e:
                print(f"    Error copying {log_file}: {e}")
            except Exception as e:
                print(f"    Unexpected error occurred while copying {log_file}: {e}")

# Usage
download_logs_from_pods_by_node_ip(
    namespace="default",
    container_path="/container",  # Replace with the correct path inside the container
    destination_path=None  # Will default to ~/Desktop/K8sLogs
)

# Note: Ensure you have the following Python packages installed:
# pip install kubernetes
