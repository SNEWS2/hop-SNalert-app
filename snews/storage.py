from abc import ABC, abstractmethod
import datetime
from bson.objectid import ObjectId

import pymongo


class IStorage(ABC):
    @abstractmethod
    def insert(self, time, neutrino_time, message):
        pass

    @abstractmethod
    def getAllMessages(self):
        pass

    @abstractmethod
    def cacheEmpty(self):
        pass

    @abstractmethod
    def getMsgFromStrID(self, post_id):
        pass


class MongoStorage(IStorage):
    def __init__(self, msg_expiration, datetime_format, server, drop_db):
        '''
        :param msg_expiration: maximum time for a message to be stored in the database cache
        :param datetime_format: date format to convert from a string
        :param mongo_server: URL string of the mongodb server address
        :param drop_db: boolean specifying whether to clear previous database storage
        '''
        # Construct Mongodb first, used to store the json dictionary
        self.client = pymongo.MongoClient(server)

        self.db = self.client.database
        self.all_messages = self.db.all_messages
        self.cache = self.db.cache
        # drop the database and previous records
        if drop_db:
            self.all_messages.delete_many({})
            self.cache.delete_many({})
            self.all_messages.drop_indexes()
            self.cache.drop_indexes()
        # don't drop
        self.all_messages.create_index("sent_time")
        self.cache.create_index("sent_time", expireAfterSeconds=msg_expiration)

        self.msg_expiration = msg_expiration
        self.datetime_format = datetime_format

    def insert(self, sent_time, neutrino_time, message):
        """
        Need to CONVERT STRING TIME to DATETIME OBJECT
        :param time:
        :param message: MUST be a dictionary
        :return:
        """
        # Convert the string time into datetime format
        time2 = datetime.datetime.strptime(sent_time, self.datetime_format)
        time3 = datetime.datetime.strptime(neutrino_time, self.datetime_format)
        message2 = message
        message2["sent_time"] = time2
        message2["neutrino_time"] = time3
        # first insert into MongoDB
        msg_id = self.all_messages.insert_one(message2).inserted_id
        # insert it into cache with expiration time set
        self.cache.insert_one(message2)

    def getAllMessages(self):
        """
        sort by 1 gives dates from old to recent
        sort by 2 gives dates from recent to old
        :return:
        """
        return self.all_messages.find().sort("sent_time", -1)

    def getCacheMsgs(self):
        return self.cache.find().sort("sent_time", -1)

    def cacheEmpty(self):
        return self.cache.count() <= 1

    def getMsgFromStrID(self, post_id):
        # Convert string ID to ObjectId:
        return self.all_messages.find_one({'_id': ObjectId(post_id)})


class RedisStorage(object):
    def __init__(self, timeout, datetime_format):
        '''
        Three Redis databases: db=0,1,2
        :param timeout:
        :param datetime_format:
        '''
        # allow redis to be optional
        import redis

        # Construct Mongodb first, used to store the json dictionary
        self.client = pymongo.MongoClient()
        self.db = self.client.database
        self.collection = self.db.collection
        self.collection.remove({})

        # Construct Redis as a hot cache with time expiration of messages, the key-value pair being (time, MongoDB ObjectID)
        self.all_messages = redis.Redis(host='localhost', port=6379, db=0)
        self.cache = redis.Redis(host='localhost', port=6379, db=1)
        # self.detectors = redis.Redis(host='localhost', port=6379, db=2)

        # flush first in case there're existing keys
        self.all_messages.flushall()
        self.cache.flushall()
        # self.detectors.flushall()

        self.timeout = timeout
        self.datetime_format = datetime_format

    def insert(self, time, message):
        """

        :param time:
        :param message: MUST be a dictionary
        :return:
        """
        # first insert into MongoDB
        msg_id = self.collection.insert_one(message).inserted_id
        str_msg_id = str(msg_id)
        # insert it into all_messages with the time in the string format
        self.all_messages.set(time, str_msg_id)
        # insert it into cache with timeout
        self.cache.set(time, str_msg_id, ex=self.timeout)

        # Convert the string time into datetime format
        # time2 = datetime.datetime.strptime(time, self.datetime_format)
        # time2 = time
        # print("All_messages size before: %d" % self.all_messages.dbsize())
        # self.all_messages.set(time2, message)
        # print("All_messages size after: %d" % self.all_messages.dbsize())
        # print("Cache size before: %d" % self.cache.dbsize())
        # self.cache.set('hey', message, ex=self.timeout)
        # print("Cache size after: %d" % self.cache.dbsize())


    # def getMsgWithinTimeThreshold(self):


    def cacheEmpty(self):
        return self.cache.dbsize() < 1

    def getMsgFromStrID(self, post_id):
        # Convert string ID to ObjectId:
        # print(type(ObjectId(post_id)))
        return self.collection.find_one({'_id': ObjectId(post_id)})
