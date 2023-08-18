import pygame
import sys
import math
import threading
from pygame.locals import *
import CarControl_Client
"""
初始化
"""

# 初始化 Pygame
pygame.init()

# 窗体大小
WINDOW_WIDTH = 1480
WINDOW_HEIGHT = 1000

# 创建窗体
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("透明矩形")

# 定义颜色
TRANSPARENT = (0, 0, 0, 0)
WHITE = (255, 255, 255)

# 矩形颜色变化的频率
FREQUENCIES = CarControl_Client.ControlFreq


# 创建透明的 Surface
rect_surfaces = [pygame.Surface((200, 200), pygame.SRCALPHA) for _ in range(4)]


# 在指定位置创建矩形
rect_positions = [
    (WINDOW_WIDTH // 2 - 100, 0),
    (0, WINDOW_HEIGHT // 2 - 100),
    (WINDOW_WIDTH - 100, WINDOW_HEIGHT // 2 - 100),
    (WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT - 100)
]

# 控制线程运行状态
running = True


"""
函数定义
"""

def get_color(time_ms, freq):
    """
    根据时间和频率计算矩形颜色
    Args:
        time_ms (int): 当前时间（毫秒）
        freq (int): 颜色变化频率

    Returns:
        int: 计算得到的颜色值
    """
    max_value = 255
    min_value = 0
    amplitude = (max_value - min_value) / 2
    offset = min_value + amplitude
    return int(offset + amplitude * math.sin(2 * math.pi * time_ms * freq / 1000))


def draw_rect():
    """
    绘制变色的矩形
    """
    while running:
        current_time = pygame.time.get_ticks()
        for i in range(4):
            color_value = get_color(current_time, FREQUENCIES[i])
            rect_color = (color_value, color_value, 255 - color_value)
            rect_surfaces[i].fill(TRANSPARENT)  # Clear the surface
            if i == 0 or i == 3:
                pygame.draw.rect(rect_surfaces[i], rect_color, (0, 0, 200, 100), border_radius=4)
                screen.blit(rect_surfaces[i], rect_positions[i])
            if i == 1 or i == 2:
                pygame.draw.rect(rect_surfaces[i], rect_color, (0, 0, 100, 200), border_radius=4)
                screen.blit(rect_surfaces[i], rect_positions[i])
        pygame.display.update()


# 启动矩形绘制线程
rect_thread = threading.Thread(target=draw_rect, args=())
rect_thread.start()

# 游戏主循环
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            running = False
            break


# 等待绘制线程结束
rect_thread.join()

# 退出 Pygame
pygame.quit()
sys.exit()
