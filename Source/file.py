import os
import socket
import sys
import json
from json.decoder import JSONDecodeError
import struct

LEN_SIZE = 10
TYPE_SIZE = 1

# In
EXEC_MSG = 0
EVAL_MSG = 1
PING_MSG = 2

# Out
SUCC_MSG = 0
ERR_MSG = 1
EMPTY_RESULT = ''

def print_err(s):
    sys.stderr.write('{}\n'.format(s))
    sys.stderr.flush()

class ConnectionReader:
    def __init__(self, conn):
        self.conn = conn
        self.buff = bytearray()

    def _get_packet(self):
        data = self.conn.recv(1024)
        if not data:
            raise EOFError('Connection closed')
        return data

    def read(self, size):
        while len(self.buff) < size:
            self.buff.extend(self._get_packet())
        result = bytes(self.buff[:size])
        del self.buff[:size]
        return result

    def read_json(self):
        return json.loads(self.read_string())

    def read_int(self):
        return struct.unpack('>i', self.read(4))[0]

    def read_byte(self):
        return struct.unpack('b', self.read(1))[0]

    def read_string(self):
        length = self.read_int()
        return self.read(length).decode('utf-8')


class ConnectionWriter:
    def __init__(self, conn):
        self.conn = conn
        self.buff = bytearray()

    def write(self, data):
        self.buff.extend(data)

    def write_byte(self, b):
        self.write(struct.pack('b', b))

    def write_int(self, i):
        self.write(struct.pack('>i', i))

    def write_string(self, s):
        bs = to_bytes(s)
        self.write_int(len(bs))
        self.write(bs)

    def flush(self):
        self.conn.sendall(self.buff)
        self.clear()

    def clear(self):
        self.buff = bytearray()


def utf8(bs):
    if sys.version_info >= (3, 0):
        return str(bs, 'UTF8')
    return unicode(bs, 'UTF8')


def to_bytes(s):
    if type(s) == bytes:
        return s

    if type(s) != str:
        s = str(s)

    if sys.version_info >= (3, 0):
        return bytes(s, 'UTF8')
    return bytes(s)


def responder():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('localhost', 0))
        sock.listen(0)
        _, port = sock.getsockname()
        sys.stdout.write("{}\n".format(port))
        sys.stdout.flush()
        conn, addr = sock.accept()
        try:
            inp = ConnectionReader(conn)
            out = ConnectionWriter(conn)
            globs = {}
            while True:
                msg_type = int(inp.read_byte())
                try:
                    if msg_type == EXEC_MSG: # 0 (just run)
                        code = inp.read_string()
                        exec(code, globs)
                        out.write_byte(SUCC_MSG)
                        out.write_string(EMPTY_RESULT)
                    elif msg_type == EVAL_MSG: # 1 (run and return)
                        code = inp.read_string()
                        try:
                            result = eval(code, globs)
                        except NameError as n_err: # assume json
                            try:
                                result = json.loads(code)
                            except JSONDecodeError as j_err:
                                raise Exception("The following line failed to parse (as strictly Python or JSON-parsed code):"
                                                + f"\n    `{code}`"
												+  "\nConsider one of the following reasons:"
                                                + f"\n1. Python reason: {n_err}"
                                                + f"\n2. JSON   reason: {j_err}")
                        out.write_byte(SUCC_MSG)
                        out.write_string(result)
                    elif msg_type == PING_MSG: # 2 (testing)
                        out.write_byte(SUCC_MSG)
                        out.write_string(EMPTY_RESULT)
                    else:
                        raise Exception('Unrecognized message type: {}'.format(msg_type))
                except Exception as e:
                    out.write_byte(ERR_MSG)
                    out.write_string(repr(e))
                finally:
                    out.flush()
                    flush()
        finally:
            conn.close()
    finally:
        sock.close()

def flush():
    sys.stdout.flush()
    sys.stderr.flush()

if __name__ == '__main__':
    sys.path.insert(0, os.getcwd())
    responder()
