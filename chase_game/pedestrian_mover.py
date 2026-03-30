#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import random
import math

class PedestrianMover(Node):
    def __init__(self):
        super().__init__('pedestrian_mover')
        
        self.pubs = {
            'ped1': self.create_publisher(Twist, '/ped1/cmd_vel', 10),
            'ped2': self.create_publisher(Twist, '/ped2/cmd_vel', 10),
            'ped3': self.create_publisher(Twist, '/ped3/cmd_vel', 10)
        }
        
        self.positions = {
            'ped1': (2.0, 3.0),
            'ped2': (-2.0, 2.0),
            'ped3': (1.0, -3.0)
        }
        
        self.create_subscription(Odometry, '/ped1/odom', lambda msg: self.odom_cb(msg, 'ped1'), 10)
        self.create_subscription(Odometry, '/ped2/odom', lambda msg: self.odom_cb(msg, 'ped2'), 10)
        self.create_subscription(Odometry, '/ped3/odom', lambda msg: self.odom_cb(msg, 'ped3'), 10)
        
        self.create_timer(3.0, self.timer_cb)

    def odom_cb(self, msg, pd_id):
        self.positions[pd_id] = (msg.pose.pose.position.x, msg.pose.pose.position.y)

    def timer_cb(self):
        for pd_id, pub in self.pubs.items():
            x, y = self.positions[pd_id]
            t = Twist()
            
            if abs(x) > 4.5 or abs(y) > 4.5:
                angle_to_center = math.atan2(-y, -x)
                # 【修改点1】：将超出围栏被拉回中心的速度从 0.4 提高到 0.8 m/s
                speed = 0.8 
                
                t.linear.x = speed * math.cos(angle_to_center)
                t.linear.y = speed * math.sin(angle_to_center)
                t.angular.z = random.uniform(-0.4, 0.4)
            else:
                # 【修改点2】：将圈内日常乱晃的速度上限从 0.4 提高到 0.9 m/s（相当于快步走）
                t.linear.x = random.uniform(-0.9, 0.9)
                t.linear.y = random.uniform(-0.9, 0.9)
                t.angular.z = random.uniform(-0.6, 0.6)
                
            pub.publish(t)

def main(args=None):
    rclpy.init(args=args)
    rclpy.spin(PedestrianMover())
    rclpy.shutdown()

if __name__ == '__main__': 
    main()
