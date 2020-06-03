#!/usr/bin/env python

import smtplib
import argparse
import json
from hop import stream
from hop.models import GCNCircular
# from hop import cli
from hop import subscribe
import sys
import decider
from pprint import pprint


# https://github.com/scimma/may2020-techthon-demo/blob/master/hop/apps/email/example.py
def _add_parser_args(parser):
    """Parse arguments for broker, configurations and options
    """
    # All args from the subscriber
    # subscribe._add_parser_args(parser)

# https://github.com/scimma/may2020-techthon-demo/blob/master/hop/apps/email/example.py
def prepare_gcn(gcn_dict, json_dump=False):
    """Parse a gcn dictionary and print to stdout.
    Args:
      gcn_dict:  the dictionary object containing a GCN-formatted message
    Returns:
      None
    """
    if json_dump:
        return (json.dumps(gcn_dict))
    else:
        gcn = GCNCircular(**gcn_dict)
        message = ""
        for line in str(gcn).splitlines():
            message += line + "\n"
        return message


def add_gcn(gcn, the_decider):
    """
    Initial alert model upon receiving published information.
    """
    time = gcn['header']['date']
    message = gcn['body']
    the_decider.add_log(time, message)


# ------------------------------------------------
# -- main

def _main(args=None):
    """main function
    """

    if not args:
        parser = argparse.ArgumentParser()
        _add_parser_args(parser)

        # temporary. May switch to subscribe(parser) later
        parser.add_argument('--f', type=str, metavar='N',
                            help='The configuration file.')
        parser.add_argument('--t', type=int, metavar='N',
                            help='The time period where observations of a supernova could occur. unit: seconds')
        parser.add_argument('--time-format', type=str, metavar='N',
                            help='The format of the time string in all messages.')
        # parser.add_argument('--emails-file', type=str, metavar='N',
        #                     help='Send alerts to these emails upon possible SN.')
        args = parser.parse_args()

    # # load config if specified
    # config = cli.load_config(args)
    #
    # # load consumer options
    # start_offset = "earliest" if args.earliest else "latest"

    gcn_format = "json"
    # receivers = [email for email in args.email]

    the_decider = decider.Decider(args.t, args.time_format)

    with stream.open("kafka://dev.hop.scimma.org:9092/snews-testing", "r", config=args.f, format=gcn_format) as s:
        for gcn_dict in s(timeout=0): # set timeout=0 so it doesn't stop listening to the topic
            # print(type(gcn_dict))
            # print(prepare_gcn(gcn_dict))
            # pprint(gcn_dict)
            add_gcn(gcn_dict, the_decider)
            alert = the_decider.deciding()
            if alert == True:
                # publish to TOPIC2 and alert astronomers
            # print("")


# temporary
if __name__ == '__main__':
    _main()