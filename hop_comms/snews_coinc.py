import snews_utils
from snews_db import Storage
import os


class Decider:

    def __init__(self, env=None):
        snews_utils.set_env()
        self.storage = Storage()
        self.mgs_expiration = int(os.getenv('MSG_EXPIRATION'))

    def check_coincidence(self):
        with self.storage.coincidence_tier_cache.watch() as stream:
            while stream.alive():
                # make sure there are no false mgss
                self.storage.keep_cache_clean()
                # check if cache is empty
                if self.storage.empty_coinc_cache():
                    print('Cache is empty')
                elif self.storage.empty_false_warnings() and not self.storage.empty_coinc_cache():
                    for mgs in self.storage.get_coincidence_tier_cache():
                        pass
