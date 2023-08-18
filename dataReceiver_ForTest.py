from pylsl import StreamInlet, resolve_stream
import numpy as np
import time
from new_decoder import cca_match


# 解析流
streams = resolve_stream('type', 'EEG')  # 使用正确的name和type来解析流
inlet = StreamInlet(streams[0])  # 假设只有一个流

# 建立长度为125的空列表，并用0填充
time_window = np.zeros((250, 16))
print(time_window)
# 布尔变量，用于标记是否加入数据
add_data = True

# 记录print次数
print_count = 0

# 开始时间
start_time = time.time()

while True:
    # 从流中获取一个chunk数据
    chunk, _ = inlet.pull_sample()  # 一次获取多少样本取决于你发送时的chunk大小

    if chunk:
        # 判断是否需要加入数据，并进行降采样
        if add_data:
            downsampled_chunk = chunk[0:16]
            time_window[:-1] = time_window[1:]  # 通过移动指针实现降采样
            time_window[-1] = downsampled_chunk

            if time.time() - start_time >= 0.04:
                fs = 250
                segment_length = 0.5
                freq_list = [5,10,9,11,13]
                correlation_threshold = 0.38
                matched_frequencies = cca_match(time_window.T, fs, segment_length, freq_list, correlation_threshold)
                print("Most common frequency:", matched_frequencies)
                #print(time.time() - start_time)
                start_time = time.time()

        # 反转布尔变量的值
        add_data = not add_data

