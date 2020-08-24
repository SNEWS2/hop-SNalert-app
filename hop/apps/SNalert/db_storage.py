from pymongo import MongoClient
import datetime
from bson.objectid import ObjectId
from . import IStorage

class storage(IStorage.IStorage):
    def __init__(self, timeout, datetime_format, server, drop_db):
        '''
        The constructor.
        :param timeout: The concidence
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
        if drop_db == True:
            self.all_messages.delete_many({})
            self.cache.delete_many({})
            self.all_messages.drop_indexes()
            self.cache.drop_indexes()
        # don't drop
        # self.all_messages.create_index("SENT TIME")
        # self.cache.create_index("SENT TIME", expireAfterSeconds=timeout)
        self.all_messages.create_index("sent_time")
        self.cache.create_index("sent_time", expireAfterSeconds=timeout)

        self.timeout = timeout
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
        # message2["SENT TIME"] = time2
        # message2["NEUTRINO TIME"] = time3
        message2["sent_time"] = time2
        message2["neutrino_time"] = time3
        # first insert into MongoDB
        msg_id = self.all_messages.insert_one(message2).inserted_id
        # str_msg_id = str(msg_id)
        # insert it into cache with timeout
        self.cache.insert_one(message2)


    # def getMsgWithinTime(self, start, end=None):
    #     if end == None:
    #         return

    def getAllMessages(self):
        """
        sort by 1 gives dates from old to recent
        sort by 2 gives dates from recent to old
        :return:
        """
        # return self.all_messages.find().sort("SENT TIME", -1)
        return self.all_messages.find().sort("sent_time", -1)

    def getCacheMsgs(self):
        # return self.cache.find().sort("SENT TIME", -1)
        return self.cache.find().sort("sent_time", -1)

    def cacheEmpty(self):
        if self.cache.count() <= 1:
            return True
        else:
            return False

    def getMsgFromStrID(self, post_id):
        # Convert string ID to ObjectId:
        # print(type(ObjectId(post_id)))
        return self.all_messages.find_one({'_id': ObjectId(post_id)})
