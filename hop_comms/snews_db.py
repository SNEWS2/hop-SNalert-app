import pymongo
from . import snews_utils
import os


class Storage:
    """This class sets up the SNEWS database using Mongo DB
    :param env: Path to env file, defaults to './auxlilary/test-config.env'
    :type env: str
    :param drop_db: drops all items in the DB every time Storage is initialized, defaults to False
    :drop_db type: bool
    :param use_local: Tells Storage to set up a local DB, defaults to False.
    :use_local type: bool
    """

    def __init__(self, env=None, drop_db=True, use_local=False):
        """Class constructor"""
        snews_utils.set_env(env)
        self.mgs_expiration = int(os.getenv('MSG_EXPIRATION'))
        self.coinc_threshold = int(os.getenv('COINCIDENCE_THRESHOLD'))
        self.mongo_server = os.getenv('DATABASE_SERVER')

        if use_local:
            self.client = pymongo.MongoClient('mongodb://localhost:27017/')
        else:
            self.client = pymongo.MongoClient(self.mongo_server)

        self.db = self.client.snews_db
        self.all_mgs = self.db.all_mgs
        self.false_warnings = self.db.false_warnings
        # self.sig_tier_cache = self.db.sig_tier_cache
        # self.time_tier_cache = self.db.time_tier_cache
        self.coincidence_tier_cache = self.db.coincidence_tier_cache
        self.coincidence_tier_alerts = self.db.coincidence_tier_alerts

        if drop_db:
            # kill all old colls
            self.all_mgs.delete_many({})
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
        self.coincidence_tier_cache.create_index('sent_time', expireAfterSeconds=self.mgs_expiration)
        self.false_warnings.create_index('sent_time')
        self.coincidence_tier_alerts.create_index('sent_time')

        self.coll_list = {
            'CoincidenceTier': self.coincidence_tier_cache,
            'False': self.false_warnings,
            'CoincidenceTierAlert': self.coincidence_tier_alerts,
        }

    def insert_mgs(self, mgs):
        """This method inserts a SNEWS message to its corresponding collection
        :param mgs: SNEWS message
        :mgs type: dict
        """
        mgs_type = mgs['_id'].split('_')[1]
        specific_coll = self.coll_list[mgs_type]
        specific_coll.insert_one(mgs)
        self.all_mgs.insert_one(mgs)

    def get_all_messages(self, sort_order=pymongo.ASCENDING):
        """Returns a list of all messages in the 'all-messages' collection
        :return: A list containing all items inside 'All-Messages'
        :rtype: list"""
        return self.all_mgs.find().sort('sent_time', sort_order)


    def get_coincidence_tier_cache(self, sort_order=pymongo.ASCENDING):
        """Returns a list of all messages in the 'cache' collection
        :return: A list containing all items inside 'Coincidence Tier Cache'
        :rtype: list"""
        return self.coincidence_tier_cache.find().sort('sent_time', sort_order)


    def get_false_warnings(self, sort_order=pymongo.ASCENDING):
        """Returns a list of all messages in the 'cache' collection
          :return: A list containing all items inside 'Coincidence Tier Cahce'
          :rtype: list"""
        return self.false_warnings.find().sort('sent_time', sort_order)

    def empty_false_warnings(self):
        """Returns True of if false warnings is empty
        :return: True if false warnings is empty, False if not"""
        if self.false_warnings.count() == 0:
            return True
        else:
            return False

    def empty_coinc_cache(self):
        """Returns True of if coincidence cache is empty
        :return: True if cache is empty, False if not"""
        if self.coincidence_tier_cache.count() <= 1:
            return True
        else:
            return False

    def purge_cache(self, coll):
        """Erases all items in a collection
        :param coll: name of collection
        :coll type: str"""
        self.coll_list[coll].delete_many({})

