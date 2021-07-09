# Author: Sebastian Torres-Lara, Univ of Houston

# Imports
from hop import Stream
from datetime import datetime
import time

# get current time year_month_day_hr_min_sec (UTC)
def time_str():
    return datetime.now().utcnow().strftime("%y/%m/%d %H:%M:%S")


# sets up stream source depending on topic
def set_topic(topic_type):
    hop_broker = "kafka.scimma.org"
    observation_topic = f"kafka://{hop_broker}/snews.experiments-test"
    alert_topic = f"kafka://{hop_broker}/snews.alert-test"
    heartbeat_topic = f"kafka://{hop_broker}/snews.alert-test"
    if topic_type == "A":
        return alert_topic
    elif topic_type == "O":
        return observation_topic
    elif topic_type == "H":
        return heartbeat_topic
    else:
        print(
            "INVALID ENTRY:\nUse 'A' for ALERT_TOPIC \nOR\n 'O' for OBSERVATION_TOPIC \nOR\n 'H' for  HEARTBEAT_TOPIC"
        )


# formats topic message, returns it as dict
def format_msg(SN_Trigger_Signal, topic_state):
    # needs to take in trigger data
    # get params from detector data, ideally pass the data as a dict
    detc_name = 18
    sent_time_hr = datetime.now().utcnow().strftime("%H:%M:%S")
    nu_t = datetime.now().utcnow().strftime("%H:%M:%S")
    machine_t = datetime.now().utcnow().strftime("%H:%M:%S")
    loc = "Somewhere"
    p_val = "15 Mev : 0.69...."  # method call
    status = "ON"
    t_series = '"4:12:56":{10.0:2}'  # nested dict: time bin with a dict, with E (MeV) bin containing num of events

    if topic_state == "A":
        return {
            "message_id": 'Alert',
            "detector_id": detc_name,
            "sent_time": sent_time_hr,
            "machine_time": machine_t,
        }
    elif topic_state == "H":
        return {
            "message_id": 'Heartbeat',
            "detector_id": detc_name,
            "machine_time": machine_t,
            "status": status,
        }
    elif topic_state == "TT":
        return {
            "message_id": 'Timing Tier',
            "detector_id": detc_name,
            "neutrino_time": nu_t,
            "machine_time": machine_t,
            "status": status,
            "timing-series": t_series,  # publish as  dict, t_bin:event_num
        }
    elif topic_state == "ST":
        return {
            "message_id": 'Significance Tier',
            "detector_id": detc_name,
            "machine_time": machine_t,
            "neutrino_time": nu_t,
            "status": status,
            "p_value": p_val,  # publish as  dict, E_val:p_val
        }
    elif topic_state == "CT":
        return {
            "message_id": 'Coincidence Tier',
            "detector_id": detc_name,
            "machine_time": machine_t,
            "neutrino_time": nu_t,
            "status": status,
        }


# with hop stream theses method publishes a single message everytime it is called
# must pass it the detector signal

def pub_t_tier(detector_data):
    detector_data = None
    stream = Stream(persist=False)
    msg = format_msg(detector_data, "TT")
    with stream.open(set_topic("O"), "w") as s:
        s.write(msg)
        print(f"Publishing OBS message:\n{msg}")


def pub_sig_tier(detector_data):
    detector_data = None
    stream = Stream(persist=False)
    msg = format_msg(detector_data, "ST")
    with stream.open(set_topic("O"), "w") as s:
        s.write(msg)
        print(f"Publishing OBS message:\n{msg}")


def pub_ccd_tier(detector_data):
    detector_data = None
    stream = Stream(persist=False)
    msg = format_msg(detector_data, "CT")
    with stream.open(set_topic("O"), "w") as s:
        s.write(msg)
        print(f"Publishing OBS message:\n{msg}")


def pub_alert(detector_data):
    detector_data = None
    stream = Stream(persist=False)
    msg = format_msg(detector_data, "A")
    with stream.open(set_topic("A"), "w") as s:
        s.write(msg)
        print(f"Publishing ALERT message:\n{msg}")


def pub_heartbeat(detector_data):
    stream = Stream(persist=True)
    # while True:
    with stream.open(set_topic("H"), "w") as s:
        # detector_data = None  needs to be called every time it's iterated !
        obs_msg = format_msg(detector_data, "H")
        s.write(obs_msg)
        time.sleep(60)


def pub_test(detector_data):
    detector_data = None
    stream = Stream(persist=False)
    msg = {"message_id": 'DS_20k_test_obs', "detector_id": 'DS_20k', "sent_time": "21/06/06 14:21:37", "neutrino_time": datetime.now().strftime("%H:%M:%S"), "machine_time": datetime.now().strftime("%H:%M:%S"), "location": "test", "p_value": 0, "status": "test", "content": "test"}
    with stream.open(set_topic("O"), "w") as s:
        s.write(msg)
        print(f"Publishing OBS message:\n{msg}")