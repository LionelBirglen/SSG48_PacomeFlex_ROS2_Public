import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    description_share = get_package_share_directory("ssg48_gripper_description")

    robot_description_path = os.path.join(
        description_share, 'urdf', 'ssg48.urdf.xacro')

    default_rviz_config_path = os.path.join(
        description_share, 'rviz', 'ssg48.rviz')

    finger_type = LaunchConfiguration('finger_type')
    gui = LaunchConfiguration('gui')
    use_robot_state_pub = LaunchConfiguration('use_robot_state_pub')
    rviz_config = LaunchConfiguration('rviz_config')

    # Process the xacro at node-launch time so launch arguments are resolved.
    robot_description_content = Command(
        ['xacro ', robot_description_path, ' finger_type:=', finger_type])
    robot_description = {
        'robot_description': ParameterValue(robot_description_content,
                                            value_type=str)}

    declare_finger_type_cmd = DeclareLaunchArgument(
        name='finger_type',
        default_value='pacomeflex',
        description='Finger variant: standard, adaptive, or pacomeflex')

    declare_gui_cmd = DeclareLaunchArgument(
        name='gui',
        default_value='True',
        description='Flag to enable joint_state_publisher_gui')

    declare_use_robot_state_pub_cmd = DeclareLaunchArgument(
        name='use_robot_state_pub',
        default_value='True',
        description='Whether to start the robot state publisher')

    declare_rviz_config_cmd = DeclareLaunchArgument(
        name='rviz_config',
        default_value=default_rviz_config_path,
        description='Full path to the RViz configuration file')

    # Joint state publisher (headless variant)
    start_joint_state_publisher_cmd = Node(
        condition=UnlessCondition(gui),
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher')

    # Joint state publisher GUI (sliders)
    start_joint_state_publisher_gui_node = Node(
        condition=IfCondition(gui),
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui')

    # Robot state publisher: URDF -> TF
    start_robot_state_publisher_cmd = Node(
        condition=IfCondition(use_robot_state_pub),
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[robot_description])

    # RViz
    start_rviz_cmd = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config],
        output='screen')

    ld = LaunchDescription()

    ld.add_action(declare_finger_type_cmd)
    ld.add_action(declare_gui_cmd)
    ld.add_action(declare_use_robot_state_pub_cmd)
    ld.add_action(declare_rviz_config_cmd)

    ld.add_action(start_joint_state_publisher_cmd)
    ld.add_action(start_joint_state_publisher_gui_node)
    ld.add_action(start_robot_state_publisher_cmd)
    ld.add_action(start_rviz_cmd)

    return ld
