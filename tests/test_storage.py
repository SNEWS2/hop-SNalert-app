from unittest.mock import patch

import mongomock

from snews import storage


@mongomock.patch(servers=(('localhost', 27017),))
def test_cache(mongodb):
    db = storage.MongoStorage(
        msg_expiration=120,
        datetime_format="%y/%m/%d %H:%M:%S",
        server="mongodb://localhost:27017/",
        drop_db=False,
    )
    with patch.object(db, 'cache', mongodb.cache):
        # check that cache is populated
        assert not db.cacheEmpty()

        # check messages in cache
        messages = list(db.getCacheMsgs())
        assert mongodb.cache.count() == len(messages)
