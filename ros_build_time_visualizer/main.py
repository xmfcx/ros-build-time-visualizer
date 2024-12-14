import os
from ros_build_time_visualizer.cli import parse_args
from ros_build_time_visualizer.log_parser import parse_build_times
from ros_build_time_visualizer.hierarchy_builder import get_package_directories, build_hierarchy, build_treemap_nodes
from ros_build_time_visualizer.visualizer import plot_treemap_with_plotly_go

def main():
    # Parse the command-line arguments
    args = parse_args()
    ros_workspace = args.ros_workspace

    # Path to the events.log file
    file_path = os.path.join(ros_workspace, args.log_file)
    print(f"Reading build log from: {file_path}")

    # Parse build times from the log file
    build_times = parse_build_times(file_path)

    print("Build times:")
    print(build_times)

    # Get package directories using colcon
    package_dirs = get_package_directories(ros_workspace)

    print("Package directories:")
    print(package_dirs)

    if not package_dirs:
        print("No package directories found. Exiting.")
        exit(1)

    # Filter package_dirs to only include packages with build times
    filtered_package_dirs = {pkg: path for pkg, path in package_dirs.items() if pkg in build_times}

    if not filtered_package_dirs:
        print("No filtered package directories found. Exiting.")
        exit(1)

    print("Filtered Package directories:")
    print(filtered_package_dirs)

    # Build the hierarchical directory structure
    hierarchy = build_hierarchy(filtered_package_dirs)

    # Build nodes for treemap starting from 'src'
    nodes, total_build_time = build_treemap_nodes(hierarchy, build_times, start_folder='src')

    # Plot treemap using Plotly Graph Objects
    fig = plot_treemap_with_plotly_go(nodes)

    # Write the treemap to an output file if the --output flag is present
    if args.output_path:
        fig.write_html(args.output_path)

    # Show the chart if the --show flag is present
    if args.show:
        fig.show()

if __name__ == "__main__":
    main()
