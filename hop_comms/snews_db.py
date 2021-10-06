import pymongo
from . import snews_utils
import os


#  https://pymongo.readthedocs.io/en/stable/api/pymongo/change_stream.html
class Storage:
    def __init__(self, env=None, drop_dbs=True):
        snews_utils.set_env(env)
        self.mgs_expiration = int(os.getenv('MSG_EXPIRATION'))
        self.coinc_threshold = int(os.getenv('COINCIDENCE_THRESHOLD'))
        self.mongo_server = os.getenv('DATABASE_SERVER')

        self.client = pymongo.MongoClient(self.mongo_server) # 
        self.db = self.client.snews_db
        self.all_mgs = self.db.all_mgs
        self.false_warnings = self.db.false_warnings
        self.test_cache = self.db.test_cache
        # self.sig_tier_cache = self.db.sig_tier_cache
        # self.time_tier_cache = self.db.time_tier_cache
        self.coincidence_tier_cache = self.db.coincidence_tier_cache
        self.coincidence_tier_alerts = self.db.coincidence_tier_alerts

        if drop_dbs:
            # kill all old colls
            self.all_mgs.delete_many({})
            self.test_cache.delete_many({})
            self.coincidence_tier_cache.delete_many({})
            self.coincidence_tier_alerts.delete_many({})
            self.false_warnings.delete_many({})
            # drop the old index
            self.all_mgs.drop_indexes()
            self.test_cache.drop_indexes()
            self.coincidence_tier_cache.drop_indexes()
            self.false_warnings.drop_indexes()
            self.coincidence_tier_alerts.drop_indexes()
        # set index
        self.all_mgs.create_index('sent_time')
        self.test_cache.create_index('sent_time', expireAfterSeconds=10)
        self.coincidence_tier_cache.create_index('sent_time', expireAfterSeconds=self.mgs_expiration)
        self.false_warnings.create_index('sent_time')
        self.coincidence_tier_alerts.create_index('sent_time')

        self.coll_list = {
            'Test': self.test_cache,
            'CoincidenceTier': self.coincidence_tier_cache,
            'False': self.false_warnings,
            'CoincidenceTierAlert':self.coincidence_tier_alerts,
        }

    def insert_mgs(self, mgs):
        mgs_type = mgs['_id'].split('_')[1]
        specific_coll = self.coll_list[mgs_type]
        self.all_mgs.insert_one(mgs)
        specific_coll.insert_one(mgs)

    def get_all_messages(self, sort_order=pymongo.ASCENDING):
        return self.all_mgs.find().sort('sent_time', sort_order)

    def get_test_cache(self, sort_order=pymongo.ASCENDING):
        return self.test_cache.find().sort('sent_time', sort_order)

    def get_coincidence_tier_cache(self, sort_order=pymongo.ASCENDING):
        return self.coincidence_tier_cache.find().sort('sent_time', sort_order)

    def is_cache_empty(self):
        if self.test_cache.count() <= 1:
            return True
        else:
            return False

    def get_false_warnings(self, sort_order=pymongo.ASCENDING):
        return self.false_warnings.find().sort('sent_time', sort_order)

    def empty_false_warnings(self):
        if self.false_warnings.count() == 0:
            return True
        else:
            return False

    def empty_coinc_cache(self):
        if self.coincidence_tier_cache.count() <= 1:
            return True
        else:
            return False

    def purge_cache(self,coll):
        self.coll_list[coll].delete_many({})

    def keep_cache_clean(self):
        if self.empty_false_warnings():
            print('No false obs\nMove along\n\n')
            pass
        else:
            for warning_mgs in get_false_warnings():
                # get the id of the false obs from the warning mgs
                get_false_obs_id = warnings['false_id']
                # get the type of the false obs
                false_type = get_false_obs_id.split('_')[1]
                # set up the mongo query
                false_id_query = {'_id': get_false_obs_id}
                # delete false mgs in corresponding cache
                self.coll_list[false_type].delete_one(false_id_query)
                # delete the warning
                self.false_warnings.delete_one(warning_mgs)
