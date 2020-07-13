from pymongo import MongoClient
import datetime
from bson.objectid import ObjectId

class storage(object):
    def __init__(self, timeout, datetime_format, server, drop_db):
        '''

        :param timeout:
        :param datetime_format:
        '''
        # Construct Mongodb first, used to store the json dictionary
        # self.client = MongoClient()
        # self.client = MongoClient('localhost', 27017)
        self.client = MongoClient(server)

        self.db = self.client.test_database
        self.all_messages = self.db.test_collection
        self.cache = self.db.test_cache
        # drop the database and previous records
        # self.all_messages.remove({})
        # self.cache.remove({})
        if drop_db == True:
            self.all_messages.delete_many({})
            self.cache.delete_many({})
        # don't drop
        self.all_messages.create_index("time")
        self.cache.create_index("time", expireAfterSeconds=timeout)

        self.timeout = timeout
        self.datetime_format = datetime_format

    def insert(self, time, message):
        """
        Need to CONVERT STRING TIME to DATETIME OBJECT
        :param time:
        :param message: MUST be a dictionary
        :return:
        """
        time2 = datetime.datetime.strptime(time, self.datetime_format)
        message2 = message
        message2["DATE"] = time2
        # first insert into MongoDB
        msg_id = self.all_messages.insert_one(message2).inserted_id
        # str_msg_id = str(msg_id)
        # insert it into cache with timeout
        self.cache.insert_one(message2)

        # Convert the string time into datetime format
        # time2 = datetime.datetime.strptime(time, self.datetime_format)
        # time2 = time
        # print("All_messages size before: %d" % self.all_messages.dbsize())
        # self.all_messages.set(time2, message)
        # print("All_messages size after: %d" % self.all_messages.dbsize())
        # print("Cache size before: %d" % self.cache.dbsize())
        # self.cache.set('hey', message, ex=self.timeout)
        # print("Cache size after: %d" % self.cache.dbsize())


    # def getMsgWithinTime(self, start, end=None):
    #     if end == None:
    #         return

    def getAllMessages(self):
        """
        sort by 1 gives dates from old to recent
        sort by 2 gives dates from recent to old
        :return:
        """
        return self.all_messages.find().sort("DATE", -1)


    def cacheEmpty(self):
        if self.cache.count() < 1:
            return True
        else:
            return False

    def getMsgFromStrID(self, post_id):
        # Convert string ID to ObjectId:
        # print(type(ObjectId(post_id)))
        return self.all_messages.find_one({'_id': ObjectId(post_id)})
