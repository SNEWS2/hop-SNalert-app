from unittest.mock import patch

import mongomock

from snews import decider


@mongomock.patch(servers=(('localhost', 27017),))
def test_decider(mongodb):
    decide = decider.Decider(
        coinc_threshold=10,
        msg_expiration=120,
        datetime_format="%y/%m/%d %H:%M:%S",
        mongo_server="mongodb://localhost:27017/",
        drop_db=False,
    )
    with patch.object(decide.db, 'cache', mongodb.cache):
        # check messages in cache
        messages = list(decide.getCacheMessages())
        assert mongodb.cache.count() == len(messages)

        # check deciding functionality, should determine coincidence
        assert decide.deciding()
