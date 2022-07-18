from socket import socket, AF_INET, SOCK_STREAM
import struct

class AD5371_comm:
    def __init__(self, host, port=30000):
        self.s_sock = socket(AF_INET, SOCK_STREAM)
        self.s_sock.connect((host, port))

    def send_data(self, data):
        assert type(data)==bytes, "Data is not bytes type"
        data_len = len(data)
        packed_len = struct.pack('I', data_len)
        self.s_sock.send(packed_len)
        self.s_sock.send(data)

    def recv_data(self):
        packed_len = b''
        while len(packed_len) < 4:
            packed_len += self.s_sock.recv(4-len(packed_len))
        data_len = struct.unpack("I", packed_len)[0]

        recv_data = self.s_sock.recv(data_len)
        return recv_data

    def __del__(self):
        self.s_sock.close()

def complex_packer(c_data):
    assert type(c_data)==complex, "This is not Complex Data"

    real_bytes = struct.pack('d', c_data.real)
    imag_bytes = struct.pack('d', c_data.imag)

    return real_bytes+imag_bytes


#Local Test Code
if __name__=="__main__":
    test = AD5371_comm("192.168.1.160")

    tmp_data = 1.123+4.567j
    
    test.send_data(complex_packer(tmp_data))
    print(test.recv_data())

    tmp_data = 0.0+9999.9999j
    test.send_data(complex_packer(tmp_data))
    print(test.recv_data())