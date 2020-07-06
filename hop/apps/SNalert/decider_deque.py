import deque

class Decider(object):
    def __init__(self, time_threshold, datetime_format):
        # link to a database???
        # self.timestamp = []
        # self.message_dic = {}
        self.de = deque.Deque(time_threshold, datetime_format)

    def deciding(self):
        """

        :return: True or false indicating the possibility of a supernova
        """
        dic = self.de.get_messages()

        # Run analysis code
        # For now:
        if self.de.getNumMessages() > 1:
            return True
        else:
            return False
        # return True

    def add_log(self, time, message):
        """
        logs should be a gcn or other format of record retrieved from hopskotch stream.
        :param logs:
        :return:
        """
        # insert it the deque
        self.de.insert(time, message)

