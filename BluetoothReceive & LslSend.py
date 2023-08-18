import binascii
import datetime
import re
import time
from multiprocessing import Process, Queue
import bluetooth
from pylsl import StreamInfo, StreamOutlet
import bluetooth.btcommon


def fushu(width, data):
    dec_data = int(data, 16)
    if dec_data > 2 ** (width - 1) - 1:
        dec_data = 2 ** width - dec_data
        dec_data = 0 - dec_data
    return dec_data


def cut(obj, sec):
    return [obj[i:i + sec] for i in range(0, len(obj), sec)]


def dt2str(time):
    str1 = time.strftime('%Y-%m-%d %H:%M:%S')
    str2 = time.microsecond
    str2 = str2 / 10 ** 6
    str2 = str(str2)
    str2 = str2[2:]  # 0.去掉
    s = str1 + '.' + str2
    return s


class rtReading(Process):
    def __init__(self, addr):
        Process.__init__(self)
        self.addr = addr
        self.FS = 500
        print("initialize rtReading")

    def startAcquisition(self):
        self.sock.send("W".encode('ascii'))  # start acquisition command, change to "W" or "T"
        print("Acquisition started")

    def parse(self, buffer):
        self.bf += str(binascii.b2a_hex(buffer))[2:-1]
        pattern = re.compile(r'bbaa[0-9A-Za-z]{104}')
        frame_list = pattern.findall(self.bf)
        self.bf = re.sub(pattern, '', self.bf)
        data = []
        for frame in frame_list:
            dd = []
            d = cut(frame[4:-2], 6)
            check_sum_str = hex((~sum([int(i, 16) for i in cut(frame[4:-8], 2)])) & 0xFFFFFFFF)[-2:]
            valid = frame[-8:-6]
            if (valid != check_sum_str):
                print('Checksum did not pass')
                time1 = datetime.datetime.now()
                print(time1)
                continue
            for i in range(16):
                x = fushu(24, d[i])
                dd.append(x)
            dd.append(int(frame[-6:-4], 16))
            dd.append(2)
            data.append(dd)
        return data

    def run(self):
        self.bf = ''
        self.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.sock.connect(self.addr)
        print("bluetooth connected")

        self.startAcquisition()  # Call the startAcquisition method after establishing the connection

        self.info = StreamInfo('EEG', 'EEG', 18, self.FS, 'float32', 'myuid34234')
        self.outlet = StreamOutlet(self.info)
        print("LSL Stream EEG_Stream started.")

        time1 = datetime.datetime.now()
        filename = 'Rawdata' + dt2str(time1).replace(':', '_') + '.txt'
        f1 = open(filename, 'w')
        try:
            while True:
                try:
                    dt = self.sock.recv(4096)
                except bluetooth.btcommon.BluetoothError as error:
                    print(f"Bluetooth error detected: {error}")
                    print("EEG device might be disconnected. Exiting.")
                    break
                # print(f"Received data: {dt}")  #print the received raw data
                data_list = self.parse(dt)
                for data in data_list:
                    print(data)
                    # Push data to LSL
                    if len(data) == 18:  # Make sure the data length matches the channel count
                        # data[5] = 0
                        self.outlet.push_sample(data)
                        f1.write(' '.join(str(x) for x in data))  # Write data as space-separated values
                        f1.write('\n')
                    else:
                        print("Data length does not match channel count.")
                # print(f"Parsed data: {data_list}")  #print the parsed data
                # for data in data_list:
                #     print(data)
                #     # Push data to LSL
                #     self.outlet.push_sample(data)
                #     f1.write(str(data))
                #     f1.write('\n')
        except KeyboardInterrupt:
            print("Acquisition interrupted by user. Exiting.")
        finally:
            f1.close()
            self.sock.close()
            print('file and socket are both closed!')


def main():
    print('Program starts')
    addr = ("88:6B:0F:71:6D:C3",
            5)  # you can change the port value according to the system could by 1 or 2 or 3 or 4 or 5 or 9 etc
    reading = rtReading(addr)
    print('Start eeg reading')
    reading.start()
    print('wait for completion of the eeg reading')
    reading.join()
    print('End of the program')


if __name__ == '__main__':
    main()

