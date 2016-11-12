from casetify import Casetify
import asyncio

@asyncio.coroutine
def printCaseta(caseta):
    mode, integration, action, value = yield from caseta.read()
    print(mode, integration, action, value)

def main():
    loop = asyncio.get_event_loop()

    caseta = Casetify()
    loop.run_until_complete(caseta.open("192.168.1.124"))
    loop.run_until_complete(printCaseta(caseta))
    loop.close()

main()
