from ibapi.wrapper import EWrapper, ListOfContractDescription
from ibapi.client import EClient
from myserver.ibapiconnection.finishable_queue import FinishableQueue

import queue

from tutorial.ttypes import InvalidOperation

DEFAULT_HISTORIC_DATA_ID = 50
DEFAULT_FUNDAMENTAL_DATA_ID = 8001
DEFAULT_MATCHING_SYMBOLS_ID = 211
DEFAULT_GET_CONTRACT_ID = 43


class IBJTSWrapper(EWrapper):

    def __init__(self):
        super().__init__()
        self._my_contract_details = {}
        self._my_historic_data_dict = {}
        self._my_fundamental_data_dict = {}
        self._my_matching_symbols_data_dict = {}
        self._my_errors = queue.Queue()

    def get_error(self, timeout=5, as_string=True):
        if self.is_error():
            try:
                (id, errorCode, errorString) = self._my_errors.get(timeout=timeout)
                if as_string:
                    return "IB error id %d errorcode %d string %s" % (id, errorCode, errorString)
                else:
                    return id, errorCode, errorString
            except queue.Empty:
                return None

        return None

    def is_error(self):
        an_error_if = not self._my_errors.empty()
        return an_error_if

    def error(self, id, errorCode, errorString):
        self._my_errors.put((id, errorCode, errorString))

    def init_time(self):
        time_queue = queue.Queue()
        self._time_queue = time_queue

        return time_queue

    def currentTime(self, time_from_server):
        self._time_queue.put(time_from_server)

    def init_contract_details(self, reqId):
        contract_details_queue = self._my_contract_details[reqId] = queue.Queue()
        return contract_details_queue

    def contractDetails(self, reqId, contractDetails):
        if reqId not in self._my_contract_details.keys():
            self.init_contract_details(reqId)

        self._my_contract_details[reqId].put(contractDetails)

    def contractDetailsEnd(self, reqId):
        if reqId not in self._my_contract_details.keys():
            self.init_contract_details(reqId)

        self._my_contract_details[reqId].put(FinishableQueue.FINISHED)

    def init_historicprices(self, tickerid):
        historic_data_queue = self._my_historic_data_dict[tickerid] = queue.Queue()

        return historic_data_queue

    def historicalData(self, tickerid, bar):

        # Note I'm choosing to ignore barCount, WAP and hasGaps but you could use them if you like
        bar_data = (bar.date, bar.open, bar.high, bar.low, bar.close, bar.volume)

        historic_data_dict = self._my_historic_data_dict

        # Add on to the current data
        if tickerid not in historic_data_dict.keys():
            self.init_historicprices(tickerid)

        historic_data_dict[tickerid].put(bar_data)

    def historicalDataEnd(self, tickerid, start: str, end: str):

        if tickerid not in self._my_historic_data_dict.keys():
            self.init_historicprices(tickerid)

        self._my_historic_data_dict[tickerid].put(FinishableQueue.FINISHED)

    def init_fundamental_data(self, tickerid):
        fundamental_data_queue = self._my_fundamental_data_dict[tickerid] = queue.Queue()

        return fundamental_data_queue

    def fundamentalData(self, tickerid, data: str):
        super().fundamentalData(tickerid, data)
        fundamental_data_dict = self._my_fundamental_data_dict

        # Add on to the current data
        if tickerid not in fundamental_data_dict.keys():
            self.init_fundamental_data(tickerid)

        fundamental_data_dict[tickerid].put(data)

        self._my_fundamental_data_dict[tickerid].put(FinishableQueue.FINISHED)

    def init_matching_symbols_data(self, tickerid):
        matching_symbols_data_queue = self._my_matching_symbols_data_dict[tickerid] = queue.Queue()

        return matching_symbols_data_queue

    def symbolSamples(self, tickerid, contractDescriptions: ListOfContractDescription):
        query_symbol_lookup_dict = self._my_matching_symbols_data_dict

        # Add on to the current data
        if tickerid not in query_symbol_lookup_dict.keys():
            self.init_matching_symbols_data(tickerid)

        query_symbol_lookup_dict[tickerid].put(contractDescriptions)

        self._my_matching_symbols_data_dict[tickerid].put(FinishableQueue.FINISHED)


class IBJTSClient(EClient):

    MAX_WAIT_SECONDS = 10

    def __init__(self, wrapper):
        EClient.__init__(self, wrapper)

    def speaking_clock(self):

        print("Getting the time from the server... ")

        time_storage = self.wrapper.init_time()
        self.reqCurrentTime()

        try:
            current_time = time_storage.get(timeout=self.MAX_WAIT_SECONDS)
        except queue.Empty:
            print("TestClient.speaking_clock : Exceeded maximum wait for wrapper to respond")
            current_time = None

        while self.wrapper.is_error():
            print(self.get_error())

        return current_time

    def resolve_ib_contract(self, ibcontract, reqId=DEFAULT_GET_CONTRACT_ID):
        print("Getting full contract details from the server... ")
        contract_details_queue = FinishableQueue(self.init_contract_details(reqId))

        self.reqContractDetails(reqId, ibcontract)

        # Run until we get a valid contract(s) or get bored waiting
        new_contract_details = contract_details_queue.get(timeout=self.MAX_WAIT_SECONDS)

        while self.wrapper.is_error():
            print("resolve_ib_contract: " + self.get_error())

        if contract_details_queue.timed_out():
            print("resolve_ib_contract: Exceeded maximum wait for wrapper to confirm finished - seems to be normal behaviour")

        if len(new_contract_details) == 0:
            print("resolve_ib_contract: No new contract details found: returning unresolved contract")
            return ibcontract

        if len(new_contract_details) > 1:
            print("resolve_ib_contract: got multiple contracts using first one")

        new_contract_details = new_contract_details[0]

        if hasattr(new_contract_details, "summary"):
            resolved_ibcontract = new_contract_details.summary
        elif hasattr(new_contract_details, "contract"):
            resolved_ibcontract = new_contract_details.contract
        else:
            raise InvalidOperation(why="resolve_ib_contract unable to resolve response properly")
        print("resolve_ib_contract: returning resolved contract")
        return resolved_ibcontract

    def get_IB_matching_symbols(self, query, tickerid=DEFAULT_MATCHING_SYMBOLS_ID):
        print("get_IB_matching_symbols")

        query_symbol_queue = FinishableQueue(self.init_matching_symbols_data(tickerid))

        self.reqMatchingSymbols(tickerid, query)

        query_result = query_symbol_queue.get(timeout=self.MAX_WAIT_SECONDS)

        while self.wrapper.is_error():
            print(self.get_error())

        if query_symbol_queue.timed_out():
            print("symbol lookup timed out")

        return query_result