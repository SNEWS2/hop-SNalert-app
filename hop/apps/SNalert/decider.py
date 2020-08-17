import datetime
from . import db_storage
from . import IDecider

class Decider(IDecider.IDecider):
    def __init__(self, time_threshold, datetime_format, mongoServer, drop_db):
        """
        The constructor.
        :param time_threshold:
        :param datetime_format:
        :param mongoServer:
        :param drop_db:
        """
        # intialize and use redis storage
        self.db = db_storage.storage(time_threshold, datetime_format, mongoServer, drop_db)
        self.tightThreshold = 10
        self.looseThreshold = time_threshold

    def deciding(self):
        """

        :return: True or false indicating the possibility of a supernova
        """
        # if not self.db.cacheEmpty():
        #     cacheMsgs = self.db.getCacheMsgs()
        #     # go through messages to check if any two or more are within 10s
        #         # if yes
        #             # verify locations different (as long as at least two are in different locations)
        #             # if so
        #                 return true
        #             # if not
        #                 return false
        #
        #         # if not, no-op or print a message
        #

        if not self.db.cacheEmpty():
            cacheMsgs = self.db.getCacheMsgs()
            prev = datetime.datetime.min
            prev_location = "FOO LOCATION"
            for msg in cacheMsgs:
                neutrinoTime = msg["NEUTRINO TIME"]
                if neutrinoTime - datetime.timedelta(seconds=self.tightThreshold) <= prev:
                    # verify location
                    if msg["header"]["LOCATION"] != prev_location:
                        return True
                prev = neutrinoTime
                prev_location = msg["header"]["LOCATION"]
        return False

        # return not self.db.cacheEmpty()

    def addMessage(self, sent_time, neutrino_time, message):
        """
        logs should be a gcn or other format of record retrieved from hopskotch stream.
        :param logs:
        :return:
        """
        # insert it the deque
        self.db.insert(sent_time, neutrino_time, message)

    def getCacheMessages(self):
        """
        Get messages that have not expired.
        :return:
        """
        return self.db.getCacheMsgs()

    def getAllMessages(self):
        """
        Get all messages in history.
        :return:
        """
        return self.db.getAllMessages()