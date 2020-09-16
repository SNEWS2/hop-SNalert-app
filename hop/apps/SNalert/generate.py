import argparse
import datetime
import os
import random
import time
import uuid

from dotenv import load_dotenv

from hop import Stream

from .dataPacket.observationMsg import SNEWSObservation
from .dataPacket.heartbeatMsg import SNEWSHeartbeat


def generate_message(time_string_format, alert_probability=0.1):
    """Generate fake SNEWS alerts/heartbeats.
    """
    test_locations = ["Houston", "Austin", "Seattle", "San Diego"]
    test_detectors = ["DETECTOR 1", "DETECTOR 2"]
    if random.random() > alert_probability:
        return SNEWSHeartbeat(
            message_id=str(uuid.uuid4()),
            detector_id=test_detectors[random.randint(0, 1)],
            sent_time=datetime.datetime.utcnow().strftime(time_string_format),
            machine_time=datetime.datetime.utcnow().strftime(time_string_format),
            location=test_locations[random.randint(0, 3)],
            status="On",
            content="For testing",
        )
    else:
        return SNEWSObservation(
            message_id=str(uuid.uuid4()),
            detector_id=test_detectors[random.randint(0, 1)],
            sent_time=datetime.datetime.utcnow().strftime(time_string_format),
            neutrino_time=datetime.datetime.utcnow().strftime(time_string_format),
            machine_time=datetime.datetime.utcnow().strftime(time_string_format),
            location=test_locations[random.randint(0, 3)],
            p_value=0.5,
            status="On",
            content="For testing",
        )


def _add_parser_args(parser):
    """Parse arguments for broker, configurations and options
    """
    parser.add_argument('-f', '--env-file', type=str, help="The path to the .env file.")
    parser.add_argument('--rate', type=float, default=0.5,
                        help="Rate to send alerts, default=0.5s")
    parser.add_argument('--alert-probability', type=float, default=0.1,
                        help="Probability of generating an alert. Default = 0.1.")
    parser.add_argument('-p',
                        '--persist',
                        action="store_true",
                        help="If set, persist and send messages indefinitely. Otherwise send a single message.")


def main(args):
    """main function
    """
    # load environment variables
    load_dotenv(dotenv_path=args.env_file)

    # configure and open observation stream
    stream = Stream(auth=False)
    source = stream.open(os.getenv("OBSERVATION_TOPIC"), "w")

    # generate messages
    try:
        # send one message, then persist if specified
        message = generate_message(
            os.getenv("TIME_STRING_FORMAT"),
            alert_probability=args.alert_probability,
        )
        source.write(message)
        time.sleep(args.rate)
                        
        while args.persist:
            message = generate_message(
                os.getenv("TIME_STRING_FORMAT"),
                alert_probability=args.alert_probability,
            )
            source.write(message)
            time.sleep(args.rate)
    except KeyboardInterrupt:
        pass
    finally:
        source.close()
