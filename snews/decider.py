from abc import ABC, abstractmethod
import datetime

from . import storage


class IDecider(ABC):
    @abstractmethod
    def get_detector_id(self,num):
        pass

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

    def get_detector_id(self, num):
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
        return detector_id(num)

    def deciding(self):
        """Implements the SNEWS coincidence requirement protocol to check cached messages and determine
        whether an alert message will be sent.

        :return: True or false indicating a coincidence between messages
        """

        if not self.db.cacheEmpty():
            cacheMsgs = self.db.getCacheMsgs()
            # call false_msgs collection from the db
            false_msgs_coll = self.db.false_msg
            cache_mgs_coll = self.db.cache
            prev = datetime.datetime.min
            prev_location = "FOO LOCATION"
            # purge all false alarms before moving forward
            self.purge_false_cache(cache_mgs_coll, false_msgs_coll)
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

    def purge_false_cache(self, cache_coll, false_mgs_coll):
        """
        Deletes any false obs in cache
        """
        all_false_warnings = self.db.get_false_warnings()
        # pass if there are no false warnings
        if self.db.false_warnings.count() == 0:
            pass

        for msg in all_false_warnings:
            # pass if there are no false warnings
            if msg['message_id'].split('_')[1] == 'False':
                false_msg_id = msg['false_id']
                false_id_query = {'message_id': false_msg_id}
                # delete false msg from cache collection
                cache_coll.delete_one(false_id_query)
                # add false msg to false msg collection
                false_mgs_coll.insert_one(msg)
                # delete the warning
                self.db.false_warnings.delete_one(msg)
