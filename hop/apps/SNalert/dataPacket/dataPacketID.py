
class DataPacketID(object):
    def __init__(self, className):
        # self.key = type(aClass).__name__
        self.key = className
        # self.id = id

    def __eq__(self, other):
        if not isinstance(other, DataPacketID):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.key == other.key

    def __hash__(self):
        return hash(repr(self))