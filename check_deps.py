import subprocess
import tempfile
import os
import shutil

# Create a temporary directory
with tempfile.TemporaryDirectory() as temp_dir:
    print(f"Installing to: {temp_dir}")
    
    # Install dependencies
    subprocess.run([
        "pip", "install", "-t", temp_dir, "-r", "requirements.txt", "--no-cache-dir"
    ], capture_output=True)
    
    # Calculate sizes
    total_size = 0
    package_sizes = {}
    
    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            file_path = os.path.join(root, file)
            size = os.path.getsize(file_path)
            total_size += size
            
            # Get package name from path
            rel_path = os.path.relpath(file_path, temp_dir)
            package = rel_path.split(os.sep)[0]
            package_sizes[package] = package_sizes.get(package, 0) + size
    
    # Sort by size
    sorted_packages = sorted(package_sizes.items(), key=lambda x: x[1], reverse=True)
    
    print(f"\nTotal size: {total_size / 1024 / 1024:.2f} MB")
    print("\nTop 10 largest packages:")
    for package, size in sorted_packages[:10]:
        print(f"{package}: {size / 1024 / 1024:.2f} MB")