from myserver.ibapiconnection.ibgateway_client import IBJTSClient, IBJTSWrapper
from threading import Thread

from tutorial.ttypes import InvalidOperation


class BootstrapIBJTSApp(IBJTSWrapper, IBJTSClient):

    def __init__(self, ip_address, port_id, client_id):
        IBJTSWrapper.__init__(self)
        IBJTSClient.__init__(self, wrapper=self)

        print("Attempting Connection to IB Gateway..." + str(ip_address) + ":" + str(port_id) + "#" + str(client_id))
        self.connect(ip_address, port_id, client_id)

        thread = Thread(target=self.run)
        thread.start()

        setattr(self, "_thread", thread)

        while self.wrapper.is_error():
            (error_id, error_code, error_message) = self.get_error(as_string=False)
            raise InvalidOperation(whatOp=error_code, why=error_message)

    def get_version(self):
        return "Build 976.2l HARDCODED"

    def quit(self):
        print("quitting, disconnecting...")
        self.disconnect()
        print("done disconnecting...")


if __name__ == '__main__':

    print("starting up...")
    app = BootstrapIBJTSApp("192.168.0.20", 4002, 10)

    current_time = app.speaking_clock()

    print("current_time = " + str(current_time))

    print("Now querying matching symbols")

    result = app.get_IB_matching_symbols("AA")

    print("matching symbols returned " + str(result))

    print("disconnecting...")
    app.disconnect()