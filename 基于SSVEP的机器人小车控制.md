# 基于SSVEP的机器人小车控制

## 项目概览

本项目实现了基于SSVEP脑电信号对机器人小车的控制。用户佩戴脑电头环,通过注视屏幕上闪烁不同频率的方块来控制小车移动。

系统由以下几部分组成:

- SSVEP刺激程序:屏幕上显示不同频率闪烁的方块,由`ShiningCube.py`实现
- 脑电数据获取:通过蓝牙从脑电设备获取原始数据,由`BluetoothReceive & LslSend.py`实现
- 数据解码:基于CCA算法解码出SSVEP对应的频率,由`new_decoder.py`实现
- 小车控制程序:显示小车视角视频,并根据解码结果发送控制指令,由`CarControl_Client.py`实现
- 数据接收测试程序:`dataReceiver_ForTest.py`,用于在不连接小车的情况下测试解码效果

## 依赖库

本项目需要以下库:

- PyGame
- OpenCV
- pylsl
- scikit-learn
- RoboMaster API

## 使用方法

1. 运行`ShiningCube.py`显示SSVEP刺激界面
2. 运行`BluetoothReceive & LslSend.py`开始通过蓝牙接收脑电数据并通过lsl发送
3. 运行`CarControl_Client.py`显示小车视角视频并接收控制指令
4. 佩戴脑电设备,注视闪烁方块控制小车移动

可以运行`dataReceiver_ForTest.py`在不连接小车的情况下测试解码效果。

## 文件说明

- `ShiningCube.py`: SSVEP刺激界面
- `BluetoothReceive & LslSend.py`: 蓝牙接收和lsl发送
- `new_decoder.py`: 基于CCA的脑电信号解码
- `CarControl_Client.py`: 小车控制程序
- `dataReceiver_ForTest.py`: 测试程序

## 注意事项

- 需要正确配置蓝牙设备地址以及接口
- LSL流配置需与解码程序一致
- 小车连接需要正确的WiFi信息

## 参考资料

- [CCA算法](https://ieeexplore.ieee.org/document/6165309)
- [RoboMaster API](https://lab.dji.com/developers/robomaster-s1)
- [PyGame](https://www.pygame.org/docs/)
- [OpenCV](https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html)

## 联系方式

如果有任何问题,请通过topanxal233@outlook.com与我联系。