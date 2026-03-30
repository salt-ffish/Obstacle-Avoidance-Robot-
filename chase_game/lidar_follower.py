#!/usr/bin/env python3
import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
from rclpy.qos import QoSProfile, ReliabilityPolicy

class LidarFollower(Node):
    def __init__(self):
        super().__init__('lidar_follower')
        self.create_subscription(Odometry, '/odom', self.pr2_cb, 10)
        self.create_subscription(Odometry, '/user_odom', self.user_cb, 10)
        qos_best_effort = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)
        self.create_subscription(LaserScan, '/scan', self.scan_cb, qos_best_effort) 
        self.create_subscription(LaserScan, '/scan', self.scan_cb, 10) 
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)

        self.user_x, self.user_y = 3.0, 0.0
        self.pr2_x, self.pr2_y, self.pr2_yaw = 0.0, 0.0, 0.0
        self.repel_x, self.repel_y = 0.0, 0.0
        self.min_front = 10.0
        self.hit_obstacle = False
        self.lidar_connected = False
        self.current_v, self.current_w = 0.0, 0.0
        self.create_timer(0.05, self.control_loop)

    def user_cb(self, msg):
        self.user_x, self.user_y = msg.pose.pose.position.x, msg.pose.pose.position.y

    def pr2_cb(self, msg):
        self.pr2_x, self.pr2_y = msg.pose.pose.position.x, msg.pose.pose.position.y
        q = msg.pose.pose.orientation
        self.pr2_yaw = math.atan2(2*(q.w*q.z + q.x*q.y), 1 - 2*(q.y*q.y + q.z*q.z))

    def scan_cb(self, msg):
        if not self.lidar_connected:
            self.get_logger().info('雷达启动成功(人工势场)')
            self.lidar_connected = True
        rx, ry, valid_rays, min_f = 0.0, 0.0, 0, 10.0
        angle = msg.angle_min
        for r in msg.ranges:
            if 0.1 < r < 10.0 and not math.isinf(r) and not math.isnan(r):
                if r < 2.0: 
                    # 【修改点】大幅增强排斥力场矩阵计算
                    f = 4.0 * ((1.0 / r) - (1.0 / 2.0)) ** 2
                    rx -= f * math.cos(angle)
                    ry -= f * math.sin(angle)
                    valid_rays += 1
                if abs(angle) < 0.8 and r < min_f: min_f = r
            angle += msg.angle_increment
        if valid_rays > 0: self.repel_x, self.repel_y = rx/valid_rays, ry/valid_rays
        else: self.repel_x, self.repel_y = 0.0, 0.0
        self.min_front = min_f
        # 扩大紧急避险检测距离
        self.hit_obstacle = (self.min_front < 1.0)

    def control_loop(self):
        if not self.lidar_connected: return
        dx, dy = self.user_x - self.pr2_x, self.user_y - self.pr2_y
        dist_to_user = math.hypot(dx, dy)
        ang_diff_direct = math.atan2(dy, dx) - self.pr2_yaw
        while ang_diff_direct > math.pi: ang_diff_direct -= 2 * math.pi
        while ang_diff_direct < -math.pi: ang_diff_direct += 2 * math.pi

        target_v, target_w = 0.0, 0.0
        
        if dist_to_user < 1.5:
            target_v, target_w = -0.6, max(min(2.5 * ang_diff_direct, 2.0), -2.0)
        elif 1.5 <= dist_to_user <= 2.8: 
            if self.hit_obstacle and self.min_front < 0.8:
                target_v, target_w = -0.4, (1.5 if ang_diff_direct > 0 else -1.5)
            else:
                target_v = 0.0; self.current_v = 0.0
                target_w = max(min(1.8 * ang_diff_direct, 1.2), -1.2) if abs(ang_diff_direct) > 0.1 else 0.0
        else:
            attract_x, attract_y = (dx / dist_to_user) * 1.5, (dy / dist_to_user) * 1.5
            cos_yaw, sin_yaw = math.cos(self.pr2_yaw), math.sin(self.pr2_yaw)
            g_repel_x = self.repel_x * cos_yaw - self.repel_y * sin_yaw
            g_repel_y = self.repel_x * sin_yaw + self.repel_y * cos_yaw
            
            # 躲避障碍物（红人）的权重系数为 12.0
            ang_diff_net = math.atan2(attract_y + g_repel_y * 12.0, attract_x + g_repel_x * 12.0) - self.pr2_yaw
            while ang_diff_net > math.pi: ang_diff_net -= 2 * math.pi
            while ang_diff_net < -math.pi: ang_diff_net += 2 * math.pi

            if self.hit_obstacle: target_v, target_w = -0.5, (2.8 if ang_diff_net > 0 else -2.8)
            else:
                target_w = max(min(2.5 * ang_diff_net, 2.0), -2.0) if abs(ang_diff_net) > 0.2 else 0.0
                target_v = min(1.8, 0.8 * dist_to_user) if abs(ang_diff_net) < 0.6 else 0.0

        self.current_v += 0.5 * (target_v - self.current_v)
        self.current_w += 0.6 * (target_w - self.current_w)
        if abs(self.current_v) < 0.05: self.current_v = 0.0
        if abs(self.current_w) < 0.08: self.current_w = 0.0

        cmd = Twist()
        cmd.linear.x, cmd.angular.z = self.current_v, self.current_w
        self.pub.publish(cmd)

def main(args=None):
    rclpy.init(args=args)
    node = LidarFollower()
    try: rclpy.spin(node)
    except KeyboardInterrupt: pass
    finally: node.destroy_node(); rclpy.shutdown()

if __name__ == '__main__': main()
