import datetime
from . import db_storage
from . import IDecider

class Decider(IDecider.IDecider):
    def __init__(self,
                 coinc_threshold=10,
                 msg_expiration=120,
                 datetime_format="%y/%m/%d %H:%M:%S",
                 mongo_server="mongodb://localhost:27017/",
                 drop_db=True):
        """
        The constructor.
        :param coinc_threshold: maximum time (s) between messages for them to be considered coincident
        :param msg_expiration: maximum time (s) for a message to be stored in the database cache
        :param datetime_format: date format to convert from a string
        :param mongo_server: URL string of the mongodb server address
        :param drop_db: boolean specifying whether to clear previous database storage
        """
        # intialize and use redis storage
        self.db = db_storage.storage(msg_expiration, datetime_format, mongo_server, drop_db)
        self.coinc_threshold = coinc_threshold

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
        :param message: message from a hopskotch kafka stream
        :return:
        """
        # insert message into the deque
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
