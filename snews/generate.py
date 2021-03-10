from collections import namedtuple
import datetime
import logging
import os
import random
import time
import uuid

from dotenv import load_dotenv

from hop import Stream
from hop.plugins.snews import SNEWSHeartbeat, SNEWSObservation


logger = logging.getLogger("snews")


Detector = namedtuple("Detector", "detector_id location")


def generate_message(time_string_format, detectors, alert_probability=0.1):
    """Generate fake SNEWS alerts/heartbeats.
    """
    detector = detectors[random.randint(0, len(detectors) - 1)]
    if random.random() > alert_probability:
        logging.debug(f"generating heartbeat from {detector.location} at {detector.detector_id}")
        return SNEWSHeartbeat(
            message_id=str(uuid.uuid4()),
            detector_id=detector.detector_id,
            sent_time=datetime.datetime.utcnow().strftime(time_string_format),
            machine_time=datetime.datetime.utcnow().strftime(time_string_format),
            location=detector.location,
            status="On",
            content="For testing",
        )
    else:
        logging.debug(f"generating alert from {detector.location} at {detector.detector_id}")
        return SNEWSObservation(
            message_id=str(uuid.uuid4()),
            detector_id=detector.detector_id,
            sent_time=datetime.datetime.utcnow().strftime(time_string_format),
            neutrino_time=datetime.datetime.utcnow().strftime(time_string_format),
            machine_time=datetime.datetime.utcnow().strftime(time_string_format),
            location=detector.location,
            p_value=0.5,
            status="On",
            content="For testing",
        )


def _add_parser_args(parser):
    """Parse arguments for broker, configurations and options
    """
    parser.add_argument('-v', '--verbose', action='count', default=0, help="Be verbose.")
    parser.add_argument('-f', '--env-file', type=str, help="The path to the .env file.")
    parser.add_argument("--no-auth", action="store_true", help="If set, disable authentication.")
    parser.add_argument('-d', '--detector', type=str,
                        help=("Set a specific detector:location pair to simulate messages from. "
                              "If not set, generates messages from multiple random locations."))
    parser.add_argument('--rate', type=float, default=0.5,
                        help="Rate to send alerts, default=0.5s")
    parser.add_argument('--alert-probability', type=float, default=0.1,
                        help="Probability of generating an alert. Default = 0.1.")
    parser.add_argument('-p',
                        '--persist',
                        action="store_true",
                        help="If set, persist and send messages indefinitely. "
                             "Otherwise send a single message.")


def main(args):
    """generate synthetic observation/heartbeat messages
    """
    # set up logging
    verbosity = [logging.WARNING, logging.INFO, logging.DEBUG]
    logging.basicConfig(
        level=verbosity[min(args.verbose, 2)],
        format="%(asctime)s | model : %(levelname)s : %(message)s",
    )

    # load environment variables
    load_dotenv(dotenv_path=args.env_file)

    # choose set of detector/location pairs
    if args.detector:
        detectors = [Detector(*args.detector.split(":"))]
    else:
        detectors = [
            Detector("DETECTOR 1", "Houston"),
            Detector("DETECTOR 2", "Seattle"),
            Detector("DETECTOR 3", "Los Angeles"),
        ]

    # configure and open observation stream
    logger.info("starting up stream")
    stream = Stream(auth=(not args.no_auth))
    source = stream.open(os.getenv("OBSERVATION_TOPIC"), "w")

    # generate messages
    logger.info(f"publishing messages to {os.getenv('OBSERVATION_TOPIC')}")
    try:
        # send one message, then persist if specified
        message = generate_message(
            os.getenv("TIME_STRING_FORMAT"),
            detectors,
            alert_probability=args.alert_probability,
        )
        source.write(message)
        time.sleep(args.rate)

        while args.persist:
            message = generate_message(
                os.getenv("TIME_STRING_FORMAT"),
                detectors,
                alert_probability=args.alert_probability,
            )
            source.write(message)
            time.sleep(args.rate)
    except KeyboardInterrupt:
        pass
    finally:
        logger.info("shutting down")
        source.close()
