import socketserver
import multiprocessing
import argparse
import logging
import json
import time

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', force=True)

class tcpServerHandle(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(1024).decode()
        logging.debug(f'recv: {data}')
        json_data = json.loads(data)
        # 收到消息后，等待指定时间，然后回复ok
        time.sleep(json_data['delay'])
        self.request.send('ok'.encode())

class udpServerHandle(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        logging.debug(f'from {self.client_address} recv: {data.decode()}')
        json_data = json.loads(data.decode())
        # 收到消息后，等待指定时间，然后回复ok
        time.sleep(json_data['delay'])
        socket.sendto('ok'.encode(), self.client_address)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='nat timeout decetor server')
    parser.add_argument('-p', '--port', default=12345, type=int, help='detect server port')
    args = parser.parse_args()

    logging.info(f'Server is running on 0.0.0.0:{args.port}')

    address = ('0.0.0.0', args.port)

    tcp_server = socketserver.ThreadingTCPServer(address, tcpServerHandle)
    udp_server = socketserver.ThreadingUDPServer(address, udpServerHandle)

    multiprocessing.Process(target=udp_server.serve_forever).start()

    tcp_server.serve_forever()
    tcp_server.shutdown()
    udp_server.shutdown()

