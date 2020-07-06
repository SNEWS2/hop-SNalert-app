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
        self.size = 0

    def insert(self, time, message):
        # print("--INSERT--")
        time2 = datetime.datetime.strptime(time, self.datetime_format)
        self.de.append(time2)
        self.dic[time2] = message
        self.size += 1
        self.update(time2)
        print("Received time:")
        print(time2)
        print("Deque length:")
        print(len(self.de))
        print("--INSERT--")
        print("")

    def update(self, time):
        """
        Remove messages older than "time_threshold"
        :param time:
        :return:
        """
        # print("--UPDATE--")
        # print(time)
        # print(self.time_threshold)
        while len(self.de) > 0:
            left_time = self.de.popleft()
            threshold = time - datetime.timedelta(0, self.time_threshold)
            # print(threshold)
            # print(left_time)
            # print("==")
            # print(len(self.de))
            # print(self.dic)
            if left_time >= threshold:
                self.de.appendleft(left_time)
                break
            else:
                self.dic.pop(left_time)
                print("POP and old message")
                self.size -= 1
        print("--UPDATE--")
        print("")

    def get_messages(self):
        return self.dic

    def getNumMessages(self):
        return len(self.de)

