#!/usr/bin/env python3
import rclpy
from geometry_msgs.msg import Twist
import sys, termios, tty, select, threading

msg = """
==== 丝滑平移控制 ====
       W
    A  S  D
======================
W/S: 前后 | A/D: 左右 | Q: 退出
（按住移动，松开停止）
"""

def get_key(settings):
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], 0.1) # 0.1秒超时
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ''
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

def main():
    settings = termios.tcgetattr(sys.stdin)
    rclpy.init()
    node = rclpy.create_node('user_teleop')
    pub = node.create_publisher(Twist, '/user_cmd_vel', 10)
    print(msg)

    cmd = Twist()
    
    # 开启单独线程保持持续发送指令（防止模型自动刹车）
    def publish_loop():
        while rclpy.ok():
            pub.publish(cmd)
            import time
            time.sleep(0.05)
            
    threading.Thread(target=publish_loop, daemon=True).start()

    try:
        while rclpy.ok():
            key = get_key(settings)
            if key == 'w': cmd.linear.x, cmd.linear.y = 3.0, 0.0
            elif key == 's': cmd.linear.x, cmd.linear.y = -3.0, 0.0
            elif key == 'a': cmd.linear.x, cmd.linear.y = 0.0, 3.0
            elif key == 'd': cmd.linear.x, cmd.linear.y = 0.0, -3.0
            elif key == 'q' or key == '\x03': break
            else: cmd.linear.x, cmd.linear.y = 0.0, 0.0 # 没按键时自动刹车
    finally:
        cmd.linear.x = cmd.linear.y = 0.0
        pub.publish(cmd)
        node.destroy_node()
        rclpy.shutdown()
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)

if __name__ == '__main__':
    main()
