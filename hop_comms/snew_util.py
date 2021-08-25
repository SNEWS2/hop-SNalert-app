from dotenv import load_dotenv

'''
loads SNEWS env 
'''


def set_env(env_path):
    load_dotenv(env_path)


'''
returns detector name (snews format)
'''


def get_detector_id(num):
    detector_id = {
        1: "Super-K",
        2: "Hyper-K",
        3: "SNO+",
        4: "KamLAND",
        5: "LVD",
        6: "ICE",
        7: "Borexino",
        8: "HALO-1kT",
        9: "HALO",
        10: "NOvA",
        11: "KM3NeT",
        12: "Baksan",
        13: "JUNO",
        14: "LZ",
        15: "DUNE",
        16: "MicroBooNe",
        17: "SBND",
        18: "DS-20K",
        19: "XENONnT",
        20: "PandaX-4T",
    }
    return detector_id(num)
