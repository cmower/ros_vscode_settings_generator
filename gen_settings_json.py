#!/usr/bin/env python3
import os
import json
import sys
import argparse


def get_ros_distro():
    """Retrieve ROS_DISTRO from environment variables."""
    ros_distro = os.environ.get("ROS_DISTRO")
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
        dirs[:] = [d for d in dirs if d not in excluded_dirs and not d.startswith(".")]
        if is_python_ros_package(root):
            potential_src = os.path.join(root, "src")
            if os.path.isdir(potential_src):
                src_dirs.append(potential_src)
                print(f"Added src directory: '{potential_src}'")
            else:
                print(
                    f"Warning: 'src' not found in package '{os.path.basename(root)}'. Skipping."
                )
    return src_dirs


def generate_settings_json(ros_distro, package_src_dirs, ros_extra_path):
    """Generate JSON for VSCode settings."""
    settings = {
        "python.autoComplete.extraPaths": [ros_extra_path] + package_src_dirs,
        "python.analysis.extraPaths": [ros_extra_path] + package_src_dirs,
        "ros.distro": ros_distro,
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
        nargs="+",
        help="Path(s) to ROS workspace(s) (e.g., /home/user/catkin_ws)",
    )
    return parser.parse_args()


def main():
    args = parse_arguments()
    ros_distro = get_ros_distro()
    ros_extra_path = f"/opt/ros/{ros_distro}/lib/python3/dist-packages"

    if not os.path.isdir(ros_extra_path):
        print(
            f"Error: ROS Python dist-packages directory '{ros_extra_path}' does not exist."
        )
        sys.exit(1)

    excluded_dirs = {"__pycache__", "build", "devel", "install", ".git", ".vscode"}
    all_src_dirs = []

    for ws in args.workspace_paths:
        workspace_ws = os.path.abspath(ws)
        workspace_src = os.path.join(workspace_ws, "src")
        print(f"\nProcessing Workspace: '{workspace_ws}'")
        print(f"Source Directory: '{workspace_src}'")

        if not os.path.isdir(workspace_src):
            print(
                f"Error: Source directory '{workspace_src}' does not exist. Skipping workspace."
            )
            continue

        package_src_dirs = find_package_src_dirs(workspace_src, excluded_dirs)
        all_src_dirs.extend(package_src_dirs)

    if not all_src_dirs:
        print("\nWarning: No valid Python ROS package src directories found.")
    else:
        print(f"\nTotal src directories added: {len(all_src_dirs)}")

    settings = generate_settings_json(ros_distro, all_src_dirs, ros_extra_path)
    json_snippet = json.dumps(settings, indent=4)

    print("\n# Add the following to your settings.json:\n")
    print(json_snippet)


if __name__ == "__main__":
    main()
