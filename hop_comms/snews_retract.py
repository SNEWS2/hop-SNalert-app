from snews_db import Storage


class Retraction:
    def __init__(self, obs_type):
        self.obs_type = obs_type
        self.storage = Storage(drop_dbs=False)
        self.obs_coll = self.storage.coll_list[obs_type]
