import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction, SetEnvironmentVariable
from launch_ros.actions import Node

def generate_launch_description():
    pkg_share = get_package_share_directory('chase_game')
    
    # 强制让 Gazebo 优先搜索工作区里的 models 文件夹
    local_model_path = os.path.expanduser('~/ros2_ws/src/chase_game/models')
    set_model_env = SetEnvironmentVariable('GAZEBO_MODEL_PATH', local_model_path)
    
    # 路径配置
    user_urdf = os.path.join(pkg_share, 'urdf', 'user.urdf')
    pr2_sdf = os.path.join(local_model_path, 'pr2', 'model.sdf')
    world_path = os.path.expanduser('~/ros2_ws/src/chase_game/worlds/street.world')
    
    # 启动 Gazebo 服务端与客户端
    gzserver = ExecuteProcess(cmd=['gzserver', '--verbose', '-s', 'libgazebo_ros_init.so', '-s', 'libgazebo_ros_factory.so', world_path], output='screen')
    gzclient = ExecuteProcess(cmd=['gzclient'], output='screen')

    # 生成
    spawn_user = Node(package='gazebo_ros', executable='spawn_entity.py', arguments=['-entity', 'user', '-file', user_urdf, '-x', '3.0', '-y', '0.0', '-z', '0.0'])
    spawn_pr2 = Node(package='gazebo_ros', executable='spawn_entity.py', arguments=['-entity', 'pr2', '-file', pr2_sdf, '-x', '0.0', '-y', '0.0', '-z', '0.0'])
    start_follower = Node(package='chase_game', executable='follower_lidar', output='screen')

    # 模拟行人生成
    ped_urdf = os.path.expanduser('~/ros2_ws/src/chase_game/urdf/pedestrian.urdf')
    spawn_ped1 = Node(package='gazebo_ros', executable='spawn_entity.py', arguments=['-entity', 'ped1', '-file', ped_urdf, '-x', '2.0', '-y', '3.0', '-z', '0.0', '-robot_namespace', 'ped1'])
    spawn_ped2 = Node(package='gazebo_ros', executable='spawn_entity.py', arguments=['-entity', 'ped2', '-file', ped_urdf, '-x', '-2.0', '-y', '2.0', '-z', '0.0', '-robot_namespace', 'ped2'])
    spawn_ped3 = Node(package='gazebo_ros', executable='spawn_entity.py', arguments=['-entity', 'ped3', '-file', ped_urdf, '-x', '1.0', '-y', '-3.0', '-z', '0.0', '-robot_namespace', 'ped3'])
    start_ped_mover = Node(package='chase_game', executable='pedestrian_mover')

    # 时间规划，错峰加载防卡死
    delay_spawn_pr2 = TimerAction(period=3.0, actions=[spawn_pr2])
    delay_peds = TimerAction(period=5.0, actions=[spawn_ped1, spawn_ped2, spawn_ped3, start_ped_mover])
    delay_spawn_user = TimerAction(period=7.0, actions=[spawn_user])
    delay_follower = TimerAction(period=9.0, actions=[start_follower])

    return LaunchDescription([
        set_model_env,
        
        gzserver,
        gzclient,
        delay_spawn_pr2,
        delay_peds,
        delay_spawn_user,
        delay_follower
    ])
