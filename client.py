import socket
import argparse
import logging
import multiprocessing

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', force=True)

def tcp_detect(server_addr, timeout, q:multiprocessing.Queue):
    sock = socket.create_connection(server_addr, timeout=3)
    sock.send(f'{{"delay": {timeout}}}'.encode())
    result = None
    try:
        sock.settimeout(timeout+1)
        data = sock.recv(1024).decode()
        if data == 'ok':
            logging.debug(f'connection is ok')
            result = True
        else:
            logging.debug(f'connection is not ok')
            result = False
    except Exception as e:
        logging.debug(f'timeout {timeout}: {e}')
        result = False
    sock.close()
    q.put((result, timeout))

def udp_detect(server_addr, timeout, q:multiprocessing.Queue):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(f'{{"delay": {timeout}}}'.encode(), server_addr)
    result = None
    try:
        sock.settimeout(timeout+1)
        data,_ = sock.recvfrom(1024)
        data = data.decode()
        if data == 'ok':
            logging.debug(f'connection is ok')
            result = True
        else:
            logging.debug(f'connection is not ok')
            result = False
    except Exception as e:
        logging.debug(f'timeout {timeout}: {e}')
        result = False
    sock.close()
    q.put((result, timeout))


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='nat timeout decetor server')
    parser.add_argument('-p', '--port', default=12345, type=int)
    parser.add_argument('-s', '--server', required=True)
    parser.add_argument('--max_timeout', default=1800, type=int, help='max timeout in seconds')
    parser.add_argument('--min_timeout', default=10, type=int, help='min timeout in seconds')
    parser.add_argument('--udp', action='store_true', help='use udp instead of tcp', default=False)
    args = parser.parse_args()

    logging.info(f'connect {args.server}:{args.port}')

    address = (args.server, args.port)

    q = multiprocessing.Queue()

    min = args.min_timeout
    max = args.max_timeout
    while min < max:
        step = (max-min)//20
        step = 1 if step == 0 else step
        logging.debug(f'min: {min}, max: {max}, step: {step}')
        procs = []
        count = 0
        for timeout in range(min,max+1,step):
            count += 1
            logging.debug(f'start process with timeout: {timeout}')
            target = udp_detect if args.udp else tcp_detect
            p = multiprocessing.Process(target=target, args=(address, timeout, q))
            p.start()
            procs.append(p)
        
        logging.debug(f'wait for all process')
        finish = 0
        while finish < count:
            result, timeout = q.get()
            finish += 1
            logging.debug(f'get result: {timeout} {result}')
            if result == True:
                logging.debug(f'after {timeout}s nat is ok')
                min = timeout if timeout > min else min
                min += 1
            else:
                logging.debug(f'after {timeout}s nat is not ok!')
                max = timeout if timeout < max else max
                max -= 1
                # 结束所有进程，进入下一次循环
                for p in procs:
                    p.terminate()
                break

        # 清理进程
        for proc in procs:
            proc.join()
    protocol = 'udp' if args.udp else 'tcp'
    if max == args.max_timeout:
        logging.warning(f'{protocol} nat timeout biger: {max}s, please use --max_timeout to set a bigger value')
    elif min == args.min_timeout:
        logging.warning(f'{protocol} nat timeout smaller: {min}s, please use --min_timeout to set a smaller value')
    else:
        logging.info(f'{protocol} nat timeout: {min-1}s')

