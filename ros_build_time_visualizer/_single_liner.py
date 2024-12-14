import re
import plotly.graph_objects as go
import pandas as pd
import subprocess
import shlex
import os


# Function to parse the events.log file
def parse_build_times(file_path):
    package_times = {}
    job_start_times = {}

    # Regular expressions to match JobStarted and JobEnded
    job_started_pattern = re.compile(r"\[(\d+\.\d+)\] \((.*?)\) JobStarted: {.*}")
    job_ended_pattern = re.compile(r"\[(\d+\.\d+)\] \((.*?)\) JobEnded: {.*}")

    with open(file_path, 'r') as file:
        for line in file:
            # Match JobStarted lines
            started_match = job_started_pattern.match(line)
            if started_match:
                time = float(started_match.group(1))
                package = started_match.group(2)
                job_start_times[package] = time

            # Match JobEnded lines
            ended_match = job_ended_pattern.match(line)
            if ended_match:
                time = float(ended_match.group(1))
                package = ended_match.group(2)

                if package in job_start_times:
                    # Calculate duration and store in dictionary
                    duration = time - job_start_times[package]
                    package_times[package] = duration

    return package_times


def seconds_to_minutes_seconds(seconds):
    from datetime import timedelta
    td = timedelta(seconds=seconds)
    hours, remainder = divmod(td.total_seconds(), 3600)
    minutes, remaining_seconds = divmod(remainder, 60)

    if hours > 0:
        return f"{int(hours)}h {int(minutes)}m {remaining_seconds:.2f}s"
    elif minutes > 0:
        return f"{int(minutes)}m {remaining_seconds:.2f}s"
    else:
        return f"{remaining_seconds:.2f}s"


def get_package_directories(ros_workspace: str):
    base_paths = os.path.join(ros_workspace, "src", "*")
    colcon_command = f"colcon --log-base /dev/null list --base-paths {base_paths}"

    try:
        result = subprocess.run(
            shlex.split(colcon_command),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        print("Error executing colcon command:")
        print(e.stderr)
        return {}

    package_dirs = {}
    for line in result.stdout.strip().split('\n'):
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        package_name = parts[0]
        package_path = parts[1]
        package_dirs[package_name] = package_path

    return package_dirs


def build_hierarchy(package_dirs):
    hierarchy = {}
    for package, path in package_dirs.items():
        folders = path.split(os.sep)
        current_level = hierarchy
        for folder in folders:
            if folder not in current_level:
                current_level[folder] = {}
            current_level = current_level[folder]
        current_level[package] = None  # Leaf node

    return hierarchy


def build_treemap_nodes(hierarchy, build_times, parent_id='', path=[], start_folder='src'):
    """
    Recursively build nodes for the treemap.

    Args:
        hierarchy (dict): Nested dictionary representing the directory hierarchy.
        build_times (dict): Dictionary mapping package names to build times.
        parent_id (str): ID of the parent node.
        path (list): Current path in the hierarchy.
        start_folder (str): The folder from which to start building the treemap.

    Returns:
        tuple: A list of node dictionaries and the total build time.
    """
    nodes = []
    total_build_time = 0.0
    for key, subtree in hierarchy.items():
        current_path = path + [key]

        # Check if the current path includes the start_folder
        if start_folder in current_path:
            # Trim the path to start from start_folder
            start_index = current_path.index(start_folder)
            trimmed_path = current_path[start_index:]
            node_id = '/'.join(trimmed_path)
            label = key

            if subtree is None:
                # Leaf node (package)
                build_time = build_times.get(key, 0.0)
                formatted_time = seconds_to_minutes_seconds(build_time)
                nodes.append({
                    'id': node_id,
                    'parent': '/'.join(trimmed_path[:-1]) if len(trimmed_path) > 1 else '',
                    'label': label,
                    'value': build_time,
                    'Build Time (seconds)': build_time,
                    'Build Time (formatted)': formatted_time
                })
                total_build_time += build_time
            else:
                if key in build_times:
                    # The directory is also a package. Add only as a leaf node to avoid duplication.
                    build_time = build_times.get(key, 0.0)
                    formatted_time = seconds_to_minutes_seconds(build_time)
                    nodes.append({
                        'id': node_id,
                        'parent': '/'.join(trimmed_path[:-1]) if len(trimmed_path) > 1 else '',
                        'label': label,
                        'value': build_time,
                        'Build Time (seconds)': build_time,
                        'Build Time (formatted)': formatted_time
                    })
                    total_build_time += build_time
                else:
                    # Internal node (directory). Recurse into subtree.
                    subtree_nodes, subtree_build_time = build_treemap_nodes(
                        subtree, build_times, '/'.join(trimmed_path), trimmed_path, start_folder)
                    nodes.extend(subtree_nodes)
                    formatted_time = seconds_to_minutes_seconds(subtree_build_time)
                    nodes.append({
                        'id': node_id,
                        'parent': '/'.join(trimmed_path[:-1]) if len(trimmed_path) > 1 else '',
                        'label': label,
                        'value': 0,
                        'Build Time (seconds)': subtree_build_time,
                        'Build Time (formatted)': formatted_time
                    })
                    total_build_time += subtree_build_time
        else:
            # Continue traversing deeper into the hierarchy
            if subtree is not None:
                subtree_nodes, subtree_build_time = build_treemap_nodes(
                    subtree, build_times, parent_id, current_path, start_folder)
                nodes.extend(subtree_nodes)
                total_build_time += subtree_build_time

    return nodes, total_build_time


def plot_treemap_with_plotly_go(nodes):
    df = pd.DataFrame(nodes)
    fig = go.Figure(go.Treemap(
        labels=df['label'],
        parents=df['parent'],
        ids=df['id'],
        values=df['value'],
        customdata=df[['Build Time (formatted)', 'Build Time (seconds)']],
        hovertemplate='<b>%{label}</b><br>Build Time: %{customdata[0]}<br>Total Seconds: %{customdata[1]:.2f}<extra></extra>',
        textinfo='label+value'
    ))
    fig.update_layout(title='Package Build Times Treemap')
    fig.write_html("build_time_treemap.html")
    fig.show()


import argparse


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Process a ROS workspace and generate a build treemap. "
                    "Provide the path to the ROS workspace as an argument.",
        epilog="Example: python script_name.py /home/mfc/projects/autoware"
    )
    parser.add_argument(
        'ros_workspace',
        type=str,
        help="The path to the ROS workspace."
    )
    return parser.parse_args()


def main():
    # Parse the command-line arguments
    args = parse_args()
    ros_workspace = args.ros_workspace

    # Path to the events.log file
    file_path = os.path.join(ros_workspace, "/log/latest_build/events.log")

    # Parse build times from the log file
    build_times = parse_build_times(file_path)

    # Get package directories using colcon
    package_dirs = get_package_directories(ros_workspace)

    if not package_dirs:
        print("No package directories found. Exiting.")
        exit(1)

    # Build the hierarchical directory structure
    hierarchy = build_hierarchy(package_dirs)

    # Build nodes for treemap starting from 'src'
    nodes, total_build_time = build_treemap_nodes(hierarchy, build_times, start_folder='src')

    # Plot treemap using Plotly Graph Objects
    plot_treemap_with_plotly_go(nodes)


if __name__ == "__main__":
    main()
