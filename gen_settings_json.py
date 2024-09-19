#!/usr/bin/env python3
import os
import json
import sys
import argparse

def get_ros_distro():
    """Retrieve ROS_DISTRO from environment variables."""
    ros_distro = os.environ.get('ROS_DISTRO')
    if not ros_distro:
        print("Error: ROS_DISTRO environment variable not set.")
        print("Please source the appropriate setup.bash file, for example:")
        print("  source /opt/ros/noetic/setup.bash")
        sys.exit(1)
    return ros_distro

def is_python_ros_package(package_path):
    """Check if directory has both setup.py and package.xml."""
    setup_py = os.path.join(package_path, "setup.py")
    package_xml = os.path.join(package_path, "package.xml")
    return os.path.isfile(setup_py) and os.path.isfile(package_xml)

def find_package_src_dirs(src_root, excluded_dirs):
    """Recursively find src directories in valid Python ROS packages."""
    src_dirs = []
    for root, dirs, files in os.walk(src_root, topdown=True):
        dirs[:] = [d for d in dirs if d not in excluded_dirs and not d.startswith('.')]
        if is_python_ros_package(root):
            potential_src = os.path.join(root, "src")
            if os.path.isdir(potential_src):
                src_dirs.append(potential_src)
                print(f"Added src directory: '{potential_src}'")
            else:
                print(f"Warning: 'src' not found in package '{os.path.basename(root)}'. Skipping.")
    return src_dirs

def generate_settings_json(ros_distro, ros_extra_path, devel_paths, package_src_dirs):
    """Generate JSON for VSCode settings."""
    # Combine all paths, ensuring no duplicates
    all_extra_paths = [ros_extra_path] + devel_paths + package_src_dirs
    all_extra_paths = list(dict.fromkeys(all_extra_paths))  # Remove duplicates

    settings = {
        "python.autoComplete.extraPaths": all_extra_paths,
        "python.analysis.extraPaths": all_extra_paths,
        "ros.distro": ros_distro
    }
    return settings

def parse_arguments():
    """Parse command-line arguments for multiple workspaces."""
    parser = argparse.ArgumentParser(
        description="Generate VSCode settings.json extraPaths for multiple ROS workspaces."
    )
    parser.add_argument(
        "workspace_paths",
        metavar="WORKSPACE_PATH",
        type=str,
        nargs='+',
        help="Path(s) to ROS workspace(s) (e.g., /home/user/catkin_ws)"
    )
    return parser.parse_args()

def main():
    args = parse_arguments()
    ros_distro = get_ros_distro()
    ros_extra_path = f"/opt/ros/{ros_distro}/lib/python3/dist-packages"
    
    if not os.path.isdir(ros_extra_path):
        print(f"Error: ROS Python dist-packages directory '{ros_extra_path}' does not exist.")
        sys.exit(1)
    
    excluded_dirs = {"__pycache__", "build", "devel", "install", ".git", ".vscode"}
    all_devel_paths = []
    all_package_src_dirs = []
    
    for ws in args.workspace_paths:
        workspace_ws = os.path.abspath(ws)
        workspace_src = os.path.join(workspace_ws, "src")
        workspace_devel = os.path.join(workspace_ws, "devel", "lib", "python3", "dist-packages")
        
        print(f"\nProcessing Workspace: '{workspace_ws}'")
        print(f"Source Directory: '{workspace_src}'")
        print(f"Devel Python dist-packages: '{workspace_devel}'")
        
        if not os.path.isdir(workspace_src):
            print(f"Error: Source directory '{workspace_src}' does not exist. Skipping workspace.")
            continue
        
        if os.path.isdir(workspace_devel):
            all_devel_paths.append(workspace_devel)
            print(f"Added devel dist-packages: '{workspace_devel}'")
        else:
            print(f"Warning: Devel dist-packages directory '{workspace_devel}' does not exist. Skipping devel path.")
        
        package_src_dirs = find_package_src_dirs(workspace_src, excluded_dirs)
        all_package_src_dirs.extend(package_src_dirs)
    
    if not all_devel_paths and not all_package_src_dirs:
        print("\nWarning: No valid Python ROS package src directories or devel dist-packages found.")
    else:
        print(f"\nTotal devel dist-packages added: {len(all_devel_paths)}")
        print(f"Total src directories added: {len(all_package_src_dirs)}")
    
    settings = generate_settings_json(ros_distro, ros_extra_path, all_devel_paths, all_package_src_dirs)
    json_snippet = json.dumps(settings, indent=4)
    
    print("\n# Add the following to your settings.json:\n")
    print(json_snippet)

if __name__ == "__main__":
    main()
