import db_storage
import IDecider
import datetime

class Decider(IDecider.IDecider):
    def __init__(self, time_threshold, datetime_format, mongoServer, drop_db):
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

        # if not self.db.cacheEmpty():
        #     cacheMsgs = self.db.getCacheMsgs()
        #     prev = datetime.datetime.min
        #     prev_location = "FOO LOCATION"
        #     for msg in cacheMsgs:
        #         neutrinoTime = msg["NEUTRINO TIME"]
        #         if neutrinoTime - datetime.timedelta(seconds=self.tightThreshold) <= prev:
        #             # verify location
        #             if msg["header"]["location"] != prev_location:
        #                 return True
        #         prev = neutrinoTime
        #         prev_location = msg["header"]["location"]
        # return False

        return not self.db.cacheEmpty()

    def addMessage(self, sent_time, neutrino_time, message):
        """
        logs should be a gcn or other format of record retrieved from hopskotch stream.
        :param logs:
        :return:
        """
        # insert it the deque
        self.db.insert(sent_time, neutrino_time, message)

    def getCacheMessages(self):
        return self.db.getCacheMsgs()

    def getAllMessages(self):
        """

        :return:
        """
        return self.db.getAllMessages()