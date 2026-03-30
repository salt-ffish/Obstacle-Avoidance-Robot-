# ROS 2 机器人动态追踪与避障仿真实验 (Chase Game)

本项目是一个基于 ROS 2 和 Gazebo 物理引擎的机器人追踪仿真实验。项目中，用户可以通过键盘控制一个虚拟目标，而 PR2 机器人将使用激光雷达和改进的人工势场法（APF）对玩家进行实时追踪，并在此过程中动态避开场地内随机游走的行人障碍物。

##  核心功能特性

- **改进型人工势场追踪 (APF)**：结合目标引力与障碍物斥力，斥力函数采用距离平滑衰减模型，实现面对动态障碍物时的无缝绕行。
- **三段式避障**：
  - **追击区 (> 2.8m)**：高速绕行障碍并追击目标。
  - **观察区 (1.5m ~ 2.8m)**：仅做转向微调。
  - **避障区 (< 1.5m 或 极近障碍 < 1.0m)**：瞬间阻断前进惯性，后退规避碰撞。
- **物理缓冲处理**：运用一阶低通滤波模拟机械惯性，消除重型底盘指令突变的打滑。

## 系统要求

- **操作系统**：Ubuntu 20.04 / 22.04 (Linux)
- **ROS 2 版本**：Foxy / Humble / Iron 等 (包含 `rclpy`, `geometry_msgs`, `nav_msgs`, `sensor_msgs`)
- **物理引擎**：Gazebo 11 及 `gazebo_ros_pkgs` 插件

## 安装与编译

将本源码包放入你的 ROS 2 工作区的 `src` 目录下（例如 `~/ros2_ws/src/`）并进行编译：

```bash
cd ~/ros2_ws
colcon build --packages-select chase_game
source install/setup.bash
```

## 运行指南

本仿真需要开启两个终端分别运行游戏场景和玩家控制器。

### 1. 启动 Gazebo 仿真环境与核心节点
在第一个终端中，加载地图、机器人、行人以及追踪大脑节点：
```bash
cd ~/ros2_ws
source install/setup.bash
ros2 launch chase_game play.launch.py
```
*注：环境启动后，你会看到一辆 PR2 机器人、一个青色圆柱体（玩家）和三名移动的红衣行人。*

### 2. 启动键盘遥控器 (玩家控制)
打开**第二个终端**，启动键盘控制脚本：
```bash
cd ~/ros2_ws
source install/setup.bash
python3 src/chase_game/chase_game/user_teleop.py
```
**操作方法：** 
- 在该终端界面保持最前时，使用 `W` (前进), `S` (后退), `A` (左转), `D` (右转) 控制青色玩家移动。
- 此时 PR2 机器人将自动开始通过雷达感知并对你进行追踪。

## 📡 核心话题 (Topics) 架构

- `/user_cmd_vel`：接收键盘下发给玩家的控制指令。
- `/user_odom`：发布玩家的实时全局坐标给机器人。
- `/scan`：PR2 机器人的激光雷达数据，作为人工势场斥力源。
- `/cmd_vel`：最终输出给 PR2 机器人底盘的运动指令。