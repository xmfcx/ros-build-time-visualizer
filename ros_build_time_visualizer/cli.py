import argparse

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Process a ROS workspace and generate a build treemap. "
                    "Provide the path to the ROS workspace as an argument.",
        epilog="Example: python -m ros_build_time_visualizer /home/mfc/projects/autoware --output_path build_time_treemap.html --show"
    )
    parser.add_argument(
        'ros_workspace',
        type=str,
        help="The path to the ROS workspace."
    )
    parser.add_argument(
        '--show',
        action='store_true',
        help="Whether to show the final chart. If this flag is present, the chart will be displayed."
    )
    parser.add_argument(
        '--output_path',
        type=str,
        nargs='?',
        const="build_time_treemap.html",
        default="build_time_treemap.html",
        help="File path to save the output HTML file. If this flag is present, the chart will be saved to the specified path."
    )
    parser.add_argument(
        '--log_file',
        type=str,
        nargs='?',
        const="log/latest_build/events.log",
        default="log/latest_build/events.log",
        help="Path to the events.log file. If this flag is present, the log file will be read from the specified path."
    )
    return parser.parse_args()
