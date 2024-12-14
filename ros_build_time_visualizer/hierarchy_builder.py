import os
import subprocess
import shlex
from ros_build_time_visualizer.utils import seconds_to_minutes_seconds

def get_package_directories(ros_workspace: str):
    base_paths = os.path.join(ros_workspace, "*")
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

    hierarchy = {".": hierarchy}
    return hierarchy


def build_treemap_nodes(hierarchy, build_times, parent_id='', path=[], start_folder='src'):
    nodes = []
    total_build_time = 0.0
    for key, subtree in hierarchy.items():
        current_path = path + [key]

        if start_folder in current_path:
            start_index = current_path.index(start_folder)
            trimmed_path = current_path[start_index:]
            node_id = '/'.join(trimmed_path)
            label = key

            if subtree is None:
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
            if subtree is not None:
                subtree_nodes, subtree_build_time = build_treemap_nodes(
                    subtree, build_times, parent_id, current_path, start_folder)
                nodes.extend(subtree_nodes)
                total_build_time += subtree_build_time

    return nodes, total_build_time
