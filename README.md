# ros_vscode_settings_generator

A Python script to automatically generate the necessary `extraPaths` configuration for VSCode's `settings.json`.
Tested with ROS Noetic.

# Usage

1. Source ROS: `source /opt/ros/ROS_DISTRO/setup.bash`
2. Run script: `python3 gen_settings_json.py /path/to/workspace1 /path/to/workspace2 ...`
3. Copy the JSON snippet output by the script to VSCode's `settings.json`, and save.