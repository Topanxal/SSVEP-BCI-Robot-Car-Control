# SSVEP BCI Robot Car Control

## Project Overview

This project implements robot car control based on SSVEP brain signals. Users wear a brain-computer interface headset and control the car by gazing at blinking blocks with different frequencies on the screen.

The system consists of the following parts:

- SSVEP Stimulus: Display blinking blocks with different frequencies as visual stimuli, implemented with `ShiningCube.py`
- Brain Signal Acquisition: Acquire raw data from BCI device via Bluetooth, implemented with `BluetoothReceive & LslSend.py`
- Data Decoding: Decode the SSVEP frequency using CCA method, implemented with `new_decoder.py`
- Car Control Program: Display car vision video stream, and send control commands based on decoded frequency, implemented with `CarControl_Client.py`
- Data Receiver Test: `dataReceiver_ForTest.py`, used to test decoding performance without connecting the car

## Dependencies

This project requires the following libraries:

- PyGame
- OpenCV
- pylsl
- scikit-learn
- RoboMaster API

## Usage

1. Run `ShiningCube.py` to display the SSVEP stimulus interface
2. Run `BluetoothReceive & LslSend.py` to start receiving brain signal data via Bluetooth and sending via lsl
3. Run `CarControl_Client.py` to display car vision and receive control commands
4. Wear BCI headset, gaze at flashing blocks to control the car

Run `dataReceiver_ForTest.py` to test decoding performance without connecting the car.

## File Description

- `ShiningCube.py`: SSVEP stimulus UI
- `BluetoothReceive & LslSend.py`: Bluetooth receiving and lsl sending
- `new_decoder.py`: Brain signal decoding based on CCA
- `CarControl_Client.py`: Car control program
- `dataReceiver_ForTest.py`: Test program

## Notes

- Bluetooth device address needs to be configured properly
- lsl stream settings should match decoding program
- Car connection needs correct WiFi settings

## References

- [CCA algorithm](https://ieeexplore.ieee.org/document/6165309)
- [RoboMaster API](https://lab.dji.com/developers/robomaster-s1)
- [PyGame](https://www.pygame.org/docs/)
- [OpenCV](https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html)

## Contact

If you have any questions, please contact me via topanxal233@outlook.com

