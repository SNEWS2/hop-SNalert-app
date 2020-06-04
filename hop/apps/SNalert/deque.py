import collections
import datetime


class Deque(object):
    def __init__(self, time_threshold, datetime_format):
        """
        The constructor
        :param time_threshold: should be seconds
        :param datetime_format:
        """
        self.dic = {}
        self.de = collections.deque()
        self.time_threshold = time_threshold
        self.datetime_format = datetime_format

    def insert(self, time, message):
        time2 = datetime.datetime.strptime(time, self.datetime_format)
        self.de.append(time2)
        self.dic[time2] = message
        self.update(time2)

    def update(self, time):
        """
        Remove messages older than "time_threshold"
        :param time:
        :return:
        """
        while len(self.de) > 0:
            left_time = self.de.popleft()
            threshold = time - datetime.timedelta(0, self.time_threshold)
            if left_time >= threshold:
                self.de.appendleft(left_time)
                break
            else:
                self.dic.pop(left_time)

    def get_messages(self):
        return self.dic

