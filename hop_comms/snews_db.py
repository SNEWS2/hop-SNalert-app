import pymongo
import snews_utils
import os


#  https://pymongo.readthedocs.io/en/stable/api/pymongo/change_stream.html
class Storage:
    def __init__(self, env=None):
        snews_utils.set_env(env)
        self.mgs_expiration = os.getenv('MSG_EXPIRATION')
        self.coinc_threshold = os.getenv('COINCIDENCE_THRESHOLD')
        self.mongo_server = os.getenv('DATABASE_SERVE')

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

        self.coll_list = {
            'Test': self.test_cache,
            'False': self.false_warnings,

        }

    def insert_mgs(self, coll, mgs):
        coll = self.coll_list[coll]
        self.all_mgs.insert_one(mgs)


class Decider:
    def __init__(self):
        pass

    def check_coincidence(self):
        pass
