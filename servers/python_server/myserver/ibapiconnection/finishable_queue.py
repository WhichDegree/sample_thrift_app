import queue


class FinishableQueue(object):

    # marker for when queue is finished
    FINISHED = object()
    STARTED = object()
    TIME_OUT = object()

    def __init__(self, queue_to_finish):

        self._queue = queue_to_finish
        self.status = self.STARTED

    def get(self, timeout):
        """
        Returns a list of queue elements once timeout is finished, or a FINISHED flag is received in the queue
        :param timeout: how long to wait before giving up
        :return: list of queue elements
        """
        contents_of_queue = []
        finished = False

        while not finished:
            try:
                current_element = self._queue.get(timeout=timeout)
                if current_element is self.FINISHED:
                    finished = True
                    self.status = self.FINISHED
                else:
                    contents_of_queue.append(current_element)
                    # keep going and try and get more data

            except queue.Empty:
                # If we hit a time out it's most probable we're not getting a finished element any time soon
                # give up and return what we have
                finished = True
                self.status = self.TIME_OUT

        return contents_of_queue

    def timed_out(self):
        return self.status is self.TIME_OUT

    def set_finished_status(self):
        self.status = self.FINISHED
