import pymongo
import snews_utils


#  https://pymongo.readthedocs.io/en/stable/api/pymongo/change_stream.html
class Storage:
    def __init__(self, mongo_client=None):
        self.client = pymongo.MongoClient(
            'mongodb+srv://DB_User:SNEWS2021@cluster0.surxv.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
        self.db = client.database
        self.all_mgs = self.db.all_mgs
        self.test_coll = self.db.test_coll
        self.obs_coll = self.db.obs_coll
        self.sig_tier_coll = self.db.sig_tier_coll
        self.time_tier_coll = self.db.time_tier_coll

    def insert_mgs(self, coll, mgs):
        coll.insert_one(mgs)


class Decider:
    def __init__(self):
        pass

    def check_coincidence(self):
        pass