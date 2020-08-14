
regularMsgSchema = {
    "type": "object",
    "properties": {
        "header": {
            "type": "object",
            "properties": {
                "MESSAGE ID": {"type": "string"},
                "DETECTOR NAME": {"type": "string"},
                "SUBJECT": {"type": "string"},
                "MESSAGE SENT TIME": {"type": "string"},
                "NEUTRINO TIME": {"type": "string"},
                "LOCATION": {"type": "string"},
                "P VALUE": {"type": "string"},
                "STATUS": {"type": "string"},
                "MESSAGE TYPE": {"type": "string"},
                "FROM": {"type": "string"}
            }
        },
        "body": {"type": "string"}
    }
}

# heartBeatMsgSchema = {
#     "type": "object",
#     "properties": {
#         "header": {
#             "type": "object",
#             "properties": {
#                 "DETECTOR NAME": {"type": "string"},
#                 "SUBJECT": {"type": "string"},
#                 "MESSAGE SENT TIME": {"type": "string"},
#                 "LOCATION": {"type": "string"},
#                 "STATUS": {"type": "string"},
#                 "MESSAGE TYPE": {"type": "string"},
#                 "FROM": {"type": "string"}
#             }
#         },
#         "body": {"type": "string"}
#     }
# }

# alertMsgSchema = 