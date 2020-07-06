import redis
# from config import redis_uri
import datetime

class storage(object):
    def __init__(self, timeout, datetime_format):
        '''
        Three Redis databases: db=0,1,2
        :param timeout:
        :param datetime_format:
        '''
        # r = redis.StrictRedis(url=redis_uri)
        self.all_messages = redis.Redis(host='localhost', port=6379, db=0)
        # print("Initial size of all_messages: %d" % self.all_messages.dbsize())
        self.cache = redis.Redis(host='localhost', port=6379, db=1)
        # print("Initial size of cache: %d" % self.cache.dbsize())
        self.detectors = redis.Redis(host='localhost', port=6379, db=2)

        # flush first in case there're existing keys
        self.all_messages.flushall()
        self.cache.flushall()
        self.detectors.flushall()

        self.timeout = timeout
        self.datetime_format = datetime_format

    def insert(self, time, message):
        # get detector id
        # detector = message['NUMBER']  # ???

        # set pair
        # time2 = datetime.datetime.strptime(time, self.datetime_format)
        time2 = time
        print("All_messages size before: %d" % self.all_messages.dbsize())
        self.all_messages.set(time2, message)
        print("All_messages size after: %d" % self.all_messages.dbsize())
        print("Cache size before: %d" % self.cache.dbsize())
        self.cache.set('hey', message, ex=self.timeout)
        print("Cache size after: %d" % self.cache.dbsize())


    # def getMessagesFromDetector(self, detectorID):


    # def getMessagesWithin(self, ):

    def cacheEmpty(self):
        if self.cache.dbsize() < 1:
            return True
        else:
            return False


def main():
    r = storage(120, '%y/%m/%d %H:%M:%S')
    r.insert('time2', 'message')
    print(r.all_messages.get('time2'))


# temporary
if __name__ == '__main__':
    main()