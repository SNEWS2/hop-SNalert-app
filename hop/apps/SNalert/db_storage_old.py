import redis
# from config import redis_uri
import pymongo
from pymongo import MongoClient
import datetime
from bson.objectid import ObjectId

class storage(object):
    def __init__(self, timeout, datetime_format):
        '''
        Three Redis databases: db=0,1,2
        :param timeout:
        :param datetime_format:
        '''
        # Construct Mongodb first, used to store the json dictionary
        self.client = MongoClient()
        self.db = self.client.test_database
        self.collection = self.db.test_collection
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
        if self.cache.dbsize() < 1:
            return True
        else:
            return False

    def getMsgFromStrID(self, post_id):
        # Convert string ID to ObjectId:
        # print(type(ObjectId(post_id)))
        return self.collection.find_one({'_id': ObjectId(post_id)})
