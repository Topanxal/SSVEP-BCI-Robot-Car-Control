import pygame
import cv2
import threading
import numpy as np
import sys
from pygame.locals import *
from pylsl import resolve_stream, StreamInlet
from robomaster import robot
import time
import math
from new_decoder import cca_match

# 初始化Pygame
pygame.init()

# 窗体尺寸和背景颜色
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
BACKGROUND_COLOR = (255, 255, 255)  # 白色

# 方块尺寸和颜色
BLOCK_SIZE = 100
BLOCK_COLOR = (0, 0, 0)  # 黑色
BORDER_COLOR = (255, 255, 255)  # 白色
# 定义颜色
TRANSPARENT = (0, 0, 0, 0)
WHITE = (255, 255, 255)
# 方块闪烁频率（Hz）
ControlFreq = [10, 8, 13, 11]
StopFreq = [6]
FREQUENCIES = ControlFreq + StopFreq
# 方块初始位置
BLOCK_POSITIONS = [
    (WINDOW_WIDTH // 2 - 50, 0),
    (0, WINDOW_HEIGHT // 2 - 50),
    (WINDOW_WIDTH - 100, WINDOW_HEIGHT // 2 - 50),
    (WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT - 100)
]
transparent_surface = pygame.Surface((100, 100), pygame.SRCALPHA)
transparent_surface.fill(TRANSPARENT)

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Video Stream")


def get_color(time_ms, freq):
    """根据时间计算方块颜色"""
    max_value = 255
    min_value = 50
    amplitude = (max_value - min_value) / 2
    offset = min_value + amplitude
    return int(offset + amplitude * math.sin(2 * math.pi * time_ms * freq / 1000))


class RobotController:
    def __init__(self):
        # 机器人初始化
        self.caps_lock_active = None
        self.ep_robot = robot.Robot()

        # 建立连接
        self.ep_robot.initialize(conn_type="sta")

        # 底盘、机械臂、摄像头初始化
        self.ep_chassis = self.ep_robot.chassis
        self.ep_camera = self.ep_robot.camera
        self.ep_arm = self.ep_robot.robotic_arm

        # 摄像头校准
        self.ep_arm.moveto(x=0, y=0).wait_for_completed()
        self.ep_arm.moveto(x=170, y=70).wait_for_completed()

        # 运动参数设置
        self.speed = 20
        self.slp = 0.001

        # 键盘事件的按键队列
        self.key_queue = []

        self.running = True

    def move_chassis(self, w1, w2, w3, w4):
        self.ep_chassis.drive_wheels(w1=w1, w2=w2, w3=w3, w4=w4)
        time.sleep(self.slp)

    def move_forward(self):
        self.move_chassis(self.speed * 1.5, self.speed * 1.5, self.speed * 1.5, self.speed * 1.5)

    def move_backward(self):
        self.move_chassis(-self.speed * 1.5, -self.speed * 1.5, -self.speed * 1.5, -self.speed * 1.5)

    def move_left(self, ):
        self.move_chassis(self.speed * 2, -self.speed * 2, self.speed * 2, -self.speed * 2)

    def move_right(self):
        self.move_chassis(-self.speed * 2, self.speed * 2, -self.speed * 2, self.speed * 2)

    def rotate_anticlockwise(self):
        self.move_chassis(self.speed, -self.speed, -self.speed, self.speed)

    def rotate_clockwise(self):
        self.move_chassis(-self.speed, self.speed, self.speed, -self.speed)

    def move(self, direct):
        if direct in ['w', 'W', 'up']:
            self.move_forward()
        elif direct in ['d', 'D', 'right']:
            self.move_right()
        elif direct in ['a', 'A', 'left']:
            self.move_left()
        elif direct in ['s', 'S', 'down']:
            self.move_backward()
        elif direct in ['q', 'Q']:
            self.rotate_anticlockwise()
        elif direct in ['e', 'E']:
            self.rotate_clockwise()
        elif direct == 'stop':
            self.move_chassis(0, 0, 0, 0)

    def handle_key_event(self, event):
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            self.running = False  # 将退出标志设置为True，以停止主循环
            self.move_chassis(0, 0, 0, 0)
            print("按下Escape键，退出程序")

        if event.type == KEYDOWN:
            if event.key == K_CAPSLOCK:
                self.caps_lock_active = not self.caps_lock_active
                print("Caps Lock状态：", self.caps_lock_active)

            if event.key == K_LEFT or event.key == K_a:
                self.key_queue.append('a')
            if event.key == K_RIGHT or event.key == K_d:
                self.key_queue.append('d')
            if event.key == K_UP or event.key == K_w:
                self.key_queue.append('w')
            if event.key == K_DOWN or event.key == K_s:
                self.key_queue.append('s')
            else:
                if event.key not in self.key_queue:
                    self.key_queue.append(event.key)

        elif event.type == KEYUP:
            if event.key in self.key_queue:
                self.key_queue.remove(event.key)

    def handle_key_queue(self):
        if self.key_queue:
            last_key = self.key_queue[-1]
            # if ord('a') <= ord(last_key) <= ord('z'):
            #     letter = last_key
            #     if self.caps_lock_active ^ (pygame.key.get_mods() & KMOD_SHIFT):
            #         letter = letter.upper()
            self.move(direct=last_key)


        else:
            self.move(direct='stop')

    def get_video_stream(self, screen):
        img = self.ep_camera.read_cv2_image(strategy="newest")
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = np.rot90(img)
        img = img[::-1, :]
        pygame_img = pygame.surfarray.make_surface(img)
        screen.blit(pygame_img, (0, 0))  # 绘制视频流



    def run(self):
        print("run函数运行了")

        # 创建一个新线程来运行 receive_eeg_data 函数
        eeg_thread = threading.Thread(target=self.receive_eeg_data_thread_function, args=())
        eeg_thread.start()


        self.ep_camera.start_video_stream(display=False)
        self.caps_lock_active = pygame.key.get_mods() & KMOD_CAPS

        while self.running:
            for event in pygame.event.get():
                self.handle_key_event(event)
            self.handle_key_queue()

            self.get_video_stream(screen)
            # 绘制方块

            pygame.display.update()

        eeg_thread.join()

        self.ep_camera.stop_video_stream()
        self.ep_robot.close()

    def receive_eeg_data_thread_function(self):

        # 解析流
        streams = resolve_stream('type', 'EEG')  # 使用正确的name和type来解析流
        inlet = StreamInlet(streams[0])  # 假设只有一个流
        print("开始接受数据流")
        # 建立长度为125的空列表，并用0填充
        time_window = np.zeros((250, 16))
        # 布尔变量，用于标记是否加入数据
        add_data = True
        # 开始时间
        start_time = time.time()

        fs = 250
        freq_list = FREQUENCIES
        correlation_threshold = 0.38

        while self.running:

            # 从流中获取一个chunk数据
            chunk, _ = inlet.pull_sample()  # 一次获取多少样本取决于你发送时的chunk大小

            if chunk:
                # 判断是否需要加入数据，并进行降采样
                if add_data:
                    downsampled_chunk = chunk[0:16]
                    time_window[:-1] = time_window[1:]  # 通过移动指针实现降采样
                    time_window[-1] = downsampled_chunk

                    if time.time() - start_time >= 0.04:

                        matched_frequencies = cca_match(time_window.T, fs, freq_list,
                                                        correlation_threshold)
                        print("Most common frequency:", matched_frequencies)

                        if FREQUENCIES[0] == matched_frequencies:
                            self.key_queue.append('w')  # 控制小车前进
                            print("小车前进了")
                        elif FREQUENCIES[1] == matched_frequencies:
                            self.key_queue.append('a')  # 控制小车向左
                            print("小车向左了")
                        elif FREQUENCIES[2] == matched_frequencies:
                            self.key_queue.append('d')  # 控制小车右转
                            print("小车向右了")
                        elif FREQUENCIES[3] == matched_frequencies:
                            self.key_queue.append('s')  # 控制小车后退
                            print("小车后退了")
                        elif FREQUENCIES[4] == matched_frequencies:
                            self.key_queue.clear()
                            self.move(direct='stop')
                            print("小车停止")
                            pass

                        start_time = time.time()
                # 反转布尔变量的值
                add_data = not add_data

            else:
                print("No data received this time.")


if __name__ == '__main__':
    controller = RobotController()
    controller.run()
    pygame.quit()
    sys.exit()
