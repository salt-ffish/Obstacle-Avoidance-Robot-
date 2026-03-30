from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'chase_game'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # 1. 声明打包附带的模型和启动文件夹（非常重要，不然 Gazebo 找不到模型）
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*.urdf')),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'world'), glob('world/*.world')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='salt',
    maintainer_email='salt@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'pedestrian_mover = chase_game.pedestrian_mover:main',
            'teleop = chase_game.user_teleop:main',
            'follower = chase_game.pr2_follower:main',
            'follower_apf = chase_game.follower2:main',
            'follower_lidar = chase_game.lidar_follower:main',
        ],
    },
)