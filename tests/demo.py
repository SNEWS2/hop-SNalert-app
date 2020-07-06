import sys
import subprocess
import argparse
import pickle
import random
import sched, time


result_path = './logs/'

def three_experiments():
    """
    Run the example gcns
    :return:
    """
    # model = subprocess.Popen(['python3',
    #                           './../hop/apps/SNalert/model.py',
    #                           '--f',
    #                           './../utils/config.conf',
    #                           '--t',
    #                           '120',
    #                           '--time-format',
    #                           '%y/%m/%d %H:%M:%S',
    #                           '--temp-gcnfile-path',
    #                           './../utils/messages/unitTest.gcn3'])

    experiment1 = subprocess.call(['hop',
                                    'publish',
                                    'kafka://dev.hop.scimma.org:9092/snews-testing',
                                    '-F',
                                    './../utils/config.conf',
                                    './../utils/messages/experiment1.gcn3'])

    experiment2 = subprocess.call(['hop',
                                    'publish',
                                    'kafka://dev.hop.scimma.org:9092/snews-testing',
                                    '-F',
                                    './../utils/config.conf',
                                    './../utils/messages/experiment2.gcn3'])

    experiment3 = subprocess.call(['hop',
                                    'publish',
                                    'kafka://dev.hop.scimma.org:9092/snews-testing',
                                    '-F',
                                    './../utils/config.conf',
                                    './../utils/messages/experiment3.gcn3'])


# def one_thread(s):
#     """
#     Simulate one experiment, generating observations randomly.
#     :return:
#     """
#     s.enter(10, )



# def test(num):
#     """
#     Create different threads to run experiments. Generate gcn at run time with probabilities.
#     :param num:
#     :return:
#     """
#     s = sched.scheduler(time.time, time.sleep)
#     with open(result_path, 'a') as f:
#         for i in range(num):
#             one_thread(s)
#     return

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--num-experiments', type=int, metavar='N',
                        help='The number of experiments that spit out random observations.')
    args = parser.parse_args()

    three_experiments()
    # test(args.num_experiments)


if __name__ == '__main__':
    main()