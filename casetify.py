import asyncio
import re

READ_SIZE = 1024
DEFAULT_USER = b"lutron"
DEFAULT_PASSWORD = b"integration"
OUTPUT_RE = re.compile(b"~(OUTPUT),([^,]+),([^,]+),([^\r]+)\r\n")

class Casetify:
    """Async class to communicate with Lutron Caseta"""

    loop = asyncio.get_event_loop()
    readbuffer = b""

    @asyncio.coroutine
    def open(self, host, port=23, username=DEFAULT_USER, password=DEFAULT_PASSWORD):
        self.reader, self.writer = yield from asyncio.open_connection(host, port, loop=self.loop)
        yield from self._readuntil(b"login: ")
        self.writer.write(username + b"\r\n")
        yield from self._readuntil(b"password: ")
        self.writer.write(password + b"\r\n")
        yield from self._readuntil(b"GNET> ")

    @asyncio.coroutine
    def _readuntil(self, value):
        while True:
            self.readbuffer += yield from self.reader.read(READ_SIZE)
            if hasattr(value, "search"):
                # assume regular expression
                m = value.search(self.readbuffer)
                if m:
                    self.readbuffer = self.readbuffer[m.end():]
                    return m
            else:
                where = self.readbuffer.find(value)
                if where != -1:
                    self.readbuffer = self.readbuffer[where + len(value):]
                    return True

    @asyncio.coroutine
    def readOutput(self):
        match = yield from self._readuntil(OUTPUT_RE)
        # 2 = integration number, 3 = action number, 4 = value
        return int(match.group(2)), int(match.group(3)), float(match.group(4))

    def writeOutput(self, integration, action, value):
        self.writer.write("#OUTPUT,{},{},{}\r\n".format(integration, action, value).encode())
