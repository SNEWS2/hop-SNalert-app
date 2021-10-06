from snews_db import Storage
import time

class RetractionCoincidence:
    def __init__(self, obs_type):
        self.obs_type = 'CoincidenceTier'
        self.storage = Storage(drop_dbs=False)
        self.coinc_cache = self.storage.coll_list[obs_type]
        self.coinc_alerts = self.storage.coincidence_tier_alerts

    def check_for_false(self):
        if self.storage.empty_false_warnings():
            pass

        for false_mgs in self.storage.get_false_warnings():
            if false_mgs['type'] == self.obs_type:
                pass
