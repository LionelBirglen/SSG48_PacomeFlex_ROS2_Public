import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
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

    # ---------------- launch arguments ----------------

    declare_finger_type_cmd = DeclareLaunchArgument(
        name='finger_type',
        default_value='pacomeflex',
        description='Finger variant: standard, adaptive, or pacomeflex')

    declare_use_robot_state_pub_cmd = DeclareLaunchArgument(
        name='use_robot_state_pub',
        default_value='True',
        description='Whether to start the robot state publisher')

    declare_use_rviz_cmd = DeclareLaunchArgument(
        name='use_rviz',
        default_value='True',
        description='Whether to start RViz')

    declare_rviz_config_cmd = DeclareLaunchArgument(
        name='rviz_config',
        default_value=default_rviz_config_path,
        description='Full path to the RViz configuration file')

    declare_bustype_cmd = DeclareLaunchArgument(
        name='bustype',
        default_value='socketcan',
        description='can bustype, typical socketcan or slcan')

    declare_channel_cmd = DeclareLaunchArgument(
        name='channel',
        default_value='can0',
        description='can channel, typical can0 or /dev/ttyACM0')

    declare_bitrate_cmd = DeclareLaunchArgument(
        name='bitrate',
        default_value='1000000',
        description='can bitrate, typical 1000000 or 500000')

    declare_default_speed_cmd = DeclareLaunchArgument(
        name='default_speed',
        default_value='100',
        description='GripperCommand action default speed, between 0 - 255')

    finger_type = LaunchConfiguration('finger_type')
    use_robot_state_pub = LaunchConfiguration('use_robot_state_pub')
    use_rviz = LaunchConfiguration('use_rviz')
    rviz_config = LaunchConfiguration('rviz_config')
    bustype = LaunchConfiguration('bustype')
    channel = LaunchConfiguration('channel')
    bitrate = LaunchConfiguration('bitrate')
    default_speed = LaunchConfiguration('default_speed')

    # ---------------- robot description ----------------
    # Process the xacro at node-launch time so launch arguments are resolved.

    robot_description_content = ParameterValue(
        Command(['xacro ', robot_description_path,
                 ' finger_type:=', finger_type]),
        value_type=str)

    robot_description = {'robot_description': robot_description_content}

    # ---------------- nodes ----------------

    # Merge the gripper driver's joint states into /joint_states.
    start_joint_state_publisher_cmd = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        parameters=[robot_description,
                    {'source_list': ['gripper_joint_states']}])

    # URDF -> TF
    start_robot_state_publisher_cmd = Node(
        condition=IfCondition(use_robot_state_pub),
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[robot_description])

    # SSG48 gripper driver
    ssg48 = Node(
        package='ssg48_gripper',
        executable='ssg48_gripper',
        name='ssg48_gripper',
        parameters=[{
            'robot_description': robot_description_content,
            'bustype': bustype,
            'bitrate': bitrate,
            'channel': channel,
            'default_speed': default_speed,
            'joint_state_topic': 'gripper_joint_states'
        }],
        output='screen')

    # RViz
    start_rviz_cmd = Node(
        condition=IfCondition(use_rviz),
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config],
        output='screen')

    # ---------------- assemble ----------------

    ld = LaunchDescription()

    ld.add_action(declare_finger_type_cmd)
    ld.add_action(declare_use_robot_state_pub_cmd)
    ld.add_action(declare_use_rviz_cmd)
    ld.add_action(declare_rviz_config_cmd)
    ld.add_action(declare_channel_cmd)
    ld.add_action(declare_bitrate_cmd)
    ld.add_action(declare_bustype_cmd)
    ld.add_action(declare_default_speed_cmd)

    ld.add_action(start_joint_state_publisher_cmd)
    ld.add_action(start_robot_state_publisher_cmd)
    ld.add_action(ssg48)
    ld.add_action(start_rviz_cmd)

    return ld
