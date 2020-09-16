import datetime
from . import db_storage
from . import IDecider

class Decider(IDecider.IDecider):
    def __init__(self, coinc_threshold, msg_expiration, datetime_format, mongoServer, drop_db):
#    def __init__(self, msg_expiration, datetime_format, mongoServer, drop_db):
        """
        The constructor.
        :param msg_expiration:
        :param datetime_format:
        :param mongoServer:
        :param drop_db:
        """
        # intialize and use redis storage
        self.db = db_storage.storage(msg_expiration, datetime_format, mongoServer, drop_db)
        self.coinc_threshold = coinc_threshold  # also should rename the following:
        #self.coinc_threshold = 10

    def deciding(self):
        """

        :return: True or false indicating the possibility of a supernova
        """
        
        if not self.db.cacheEmpty():
            cacheMsgs = self.db.getCacheMsgs()
            prev = datetime.datetime.min
            prev_location = "FOO LOCATION"
            for msg in cacheMsgs:
                neutrinoTime = msg["neutrino_time"]
                # go through messages to check if any two or more are within the time threshold
                if neutrinoTime - datetime.timedelta(seconds=self.coinc_threshold) <= prev:
                    # verify the locations are different
                    if msg["location"] != prev_location:
                        return True
                prev = neutrinoTime
                prev_location = msg["location"]
        return False

        # return not self.db.cacheEmpty()

    def addMessage(self, message):
        """
        logs should be a gcn or other format of record retrieved from hopskotch stream.
        :param logs:
        :return:
        """
        # insert it the deque
        #print('adding message to db')
        self.db.insert(message.sent_time, message.neutrino_time, message.asdict())

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
