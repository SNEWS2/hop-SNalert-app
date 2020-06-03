import argparse
import deque


class Decider(object):
    def __init__(self, time_threshold, datetime_format):
        # link to a database???
        # self.timestamp = []
        # self.message_dic = {}
        self.de = deque.Deque(time_threshold, datetime_format)

    def deciding(self):
        """

        :return: True or false indicating the possibility of a supernova
        """
        dic = self.de.get_messages()

        # Run analysis code
        None

    def add_log(self, time, message):
        """
        log should be a gcn or other format of record retrieved from hopskotch stream.
        :param log:
        :return:
        """
        # insert it the deque
        self.de.insert(time, message)




# def main(args=None):
#     """
#     The main function.
#     :param args:
#     :return:
#     """
#     parser = argparse.ArgumentParser(description='Argument Parser')
#     # parser.add_argument('--subscribe-url', type=int, metavar='N',
#     #                     help='kafka://SERVER/USER-TOPIC')
#     parser.add_argument('--publish-url', type=int, metavar='N',
#                         help='kafka://SERVER/USER-TOPIC')
#     parser.add_argument('--f', type=str, metavar='N',
#                         help='The path to the configuration file.')
#     args = parser.parse_args()
#


