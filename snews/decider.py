from abc import ABC, abstractmethod
import datetime

from . import storage


class IDecider(ABC):
    @abstractmethod
    def deciding(self):
        pass

    @abstractmethod
    def addMessage(self, time, neutrino_time, message):
        pass

    @abstractmethod
    def getAllMessages(self):
        pass


class Decider(IDecider):
    detector_id = {
        1: "Super-K",
        2: "Hyper-K",
        3: "SNO+",
        4: "KamLAND",
        5: "LVD",
        6: "ICE",
        7: "Borexino",
        8: "HALO-1kT",
        9: "HALO",
        10: "NOvA",
        11: "KM3NeT",
        12: "Baksan",
        13: "JUNO",
        14: "LZ",
        15: "DUNE",
        16: "MicroBooNe",
        17: "SBND",
        18: "DS-20K",
        19: "XENONnT",
        20: "PandaX-4T",
    }

    def __init__(self,
                 coinc_threshold=10,
                 msg_expiration=120,
                 datetime_format="%y/%m/%d %H:%M:%S",
                 mongo_server="mongodb://localhost:27017/",
                 drop_db=True):
        """
        The constructor.
        :param coinc_threshold: maximum time (s) between messages for them to be considered coincident
        :param msg_expiration: maximum time (s) that a message will be stored in the database cache before expiring
        :param datetime_format: date format to convert from a string
        :param mongo_server: URL string of the mongodb server address
        :param drop_db: boolean specifying whether to clear previous database storage
        """
        # intialize and use mongo storage
        self.db = storage.MongoStorage(msg_expiration, datetime_format, mongo_server, drop_db)
        self.coinc_threshold = coinc_threshold

    def deciding(self):
        """Implements the SNEWS coincidence requirement protocol to check cached messages and determine
        whether an alert message will be sent.

        :return: True or false indicating a coincidence between messages
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
