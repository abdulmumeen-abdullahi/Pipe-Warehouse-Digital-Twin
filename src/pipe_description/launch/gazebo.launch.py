import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro

def generate_launch_description():
    pkg_name = 'pipe_description'
    file_subpath = 'urdf/warehouse.urdf.xacro'

    # Get paths
    pkg_share = get_package_share_directory(pkg_name)
    pkg_share_path = os.path.dirname(pkg_share)

    # Set Ignition Gazebo resource path
    set_env = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH', 
        value=pkg_share_path
    )

    # Process the URDF file
    xacro_file = os.path.join(pkg_share, file_subpath)
    robot_description_raw = xacro.process_file(xacro_file).toxml()

    # Launch Ignition Gazebo
    ign_gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': '-r empty.sdf'}.items(),
    )

    # Spawn
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-string', robot_description_raw,
            '-name', 'pipe_warehouse',
            '-allow_renaming', 'true'
        ],
        output='screen'
    )

    # robot_state_publisher
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description_raw}]
    )

    return LaunchDescription([
        set_env,      
        ign_gazebo,
        node_robot_state_publisher,
        spawn_entity,
    ])