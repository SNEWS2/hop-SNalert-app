from collections import deque
from datetime import datetime
import logging
import os

from dotenv import load_dotenv
import numpy

from hop import Stream


logger = logging.getLogger("snews")


def _add_parser_args(parser):
    """Parse arguments for broker, configurations and options
    """
    parser.add_argument('-v', '--verbose', action='count', default=0, help="Be verbose.")
    parser.add_argument('-f', '--env-file', type=str, help="The path to the .env file.")
    parser.add_argument("--no-auth", action="store_true", help="If set, disable authentication.")
    parser.add_argument("-n", "--num-points", type=int, default=100,
                        help="Number of points to compute mean. default=100")
    parser.add_argument("-m", "--measurement", choices=("alert", "observation"),
                        default="observation", help="Specify the type of measurement to measure "
                                                    "latency. Default = observation.")


def main(args):
    """Measure latency from SNEWS events.
    """
    # set up logging
    verbosity = [logging.WARNING, logging.INFO, logging.DEBUG]
    logging.basicConfig(
        level=verbosity[min(args.verbose, 2)],
        format="%(asctime)s | latency : %(levelname)s : %(message)s",
    )

    # load environment variables
    load_dotenv(dotenv_path=args.env_file)

    # map choices to measurements
    topics = {
        "alert": os.getenv("ALERT_TOPIC"),
        "observation": os.getenv("OBSERVATION_TOPIC"),
    }

    # configure and open stream
    logger.info("starting up")
    stream = Stream(auth=(not args.no_auth), persist=True)
    source = stream.open(topics[args.measurement], "r")

    # track latency measurements
    latencies = deque(maxlen=args.num_points)

    # generate messages
    logger.info(f"listening to messages from {topics[args.measurement]}")
    try:
        for message, metadata in source.read(batch_size=1, metadata=True):
            # calculate current latency
            message_timestamp = metadata.timestamp
            current_timestamp = int((datetime.utcnow() - datetime(1970, 1, 1)).total_seconds() * 1000)
            latency = (current_timestamp - message_timestamp) / 1000

            # calculate mean latency
            latencies.append(latency)
            mean_latency = numpy.around(numpy.mean(list(latencies)), 3)

            logger.info(f"current latency: {latency}s, mean latency: {mean_latency}s")
    except KeyboardInterrupt:
        pass
    finally:
        logger.info("shutting down")
        source.close()
