import pymongo
import snews_utils
import os


#  https://pymongo.readthedocs.io/en/stable/api/pymongo/change_stream.html
class Storage:
    def __init__(self, env=None):
        snews_utils.set_env(env)
        self.mgs_expiration = os.getenv('MSG_EXPIRATION')
        self.coinc_threshold = os.getenv('COINCIDENCE_THRESHOLD')
        self.mongo_server = os.getenv('DATABASE_SERVER')

        self.client = pymongo.MongoClient(self.mongo_server)
        self.db = self.client.database
        self.all_mgs = self.db.all_mgs
        self.false_warnings = self.db.false_warnings
        self.test_cache = self.db.test_cache
        # self.obs_cache = self.db.obs_cache
        # self.sig_tier_cache = self.db.sig_tier_cache
        # self.time_tier_cache = self.db.time_tier_cache
        # self.coincidence_tier_cache = self.db.coincidence_tier_cache
        # set index
        self.all_mgs.create_index('sent_time')
        self.test_cache.create_index('sent_time', expireAfterSeconds=self.mgs_expiration)
        self.false_warnings.create_index('sent_time')
        self.coll_list = {
            'Test': self.test_cache,
            'False': self.false_warnings,

        }

    def insert_mgs(self, mgs):
        mgs_type = mgs['messsage_id'].split('_')[1]
        specific_coll = self.coll_list[mgs_type]
        self.all_mgs.insert_one(mgs)
        specific_coll.insert_one(mgs)

    def get_all_messages(self, sort_order=pymongo.ASCENDING):
        return self.all_mgs.find().sort('sent_time', sort_order)

    def get_cache(self, sort_order=pymongo.ASCENDING):
        return self.test_cache.find().sort('sent_time', sort_order)

    def is_cache_empty(self):
        if self.test_cache.count() <= 1:
            return True
        else:
            return False

    def get_false_warnings(self, sort_order=pymongo.ASCENDING):
        return self.false_warnings.find().sort('sent_time', sort_order)

    def empty_false_warnings(self):
        if self.false_warnings.count() <= 1:
            return True
        else:
            return False

    def purge_false_mgs(self):
        pass
