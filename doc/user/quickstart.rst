==========
Quickstart
==========

.. contents::
   :local:


Run SNEWS 2.0
-------------

After installing the module, the command that does the magic is:

.. code:: bash

    SNalert model

The two required options are:

    * --f: the .env file for required environment variables.
    * --no-auth: True to use the default .toml file. Otherwise, use Hopskotch authentication in the .env file.

So an example command would be

.. code::

     SNalert model --env-file config.env --no-auth

Configuration
^^^^^^^^^^^^^^

The user should create a .env file and pass the file path to the --f
option when running SNEWS 2.0. The .env file should include the following:

.. code:: python

    TIMEOUT=
    TIME_STRING_FORMAT=
    DATABASE_SERVER=
    NEW_DATABASE=
    OBSERVATION_TOPIC=
    TESTING_TOPIC=
    HEARTBEAT_TOPIC=
    ALERT_TOPIC=

The definition of these environmental variables are:

    * TIMEOUT: the loose threshold in the supernova alert protocol.
    * TIME_STRING_FORMAT: the string format of time in all SNEWS messages.
    * DATABASE_SERVER: the database server to that SNEWS 2.0 connects to in order to store messages for processing. In the current version, the app takes in a **MongoDB** server.
    * NEW_DATABASE: "True" to drop all previous messages and "False" to keep them.
    * OBSERVATION_TOPIC: the Hopskotch topic for detectors to publish messages to.
    * TESTING_TOPIC: the optional topic for testing.
    * ALERT_TOPIC: the Hopskotch topic for SNEWS 2.0 to publish alert messages to the detectors.

Access to Hopskotch
^^^^^^^^^^^^^^^^^^^

To configure a .toml file for hop-client module, follow the steps documented
at https://github.com/scimma/hop-client and specify --default-authentiation as False.

Otherwise, in the .env file, include the following:

.. code:: python

    USERNAME=username
    PASSWORD=password

where "username" and "password" are user credentials to Hopsckoth.


Generate Messages
^^^^^^^^^^^^^^^^^^

To simulate real-time experiments that mainly for testing purposes. Run the command

.. code:: bash

    SNalert generate

with the required options

    * --env-file: the .env file for configuration.
    * --rate: the rate of messages sent in seconds (e.g. 2 means roughly one message every 2 seconds).
    * --alert-probability: the discrete probability of an detector making an observation.

So an example command could be

.. code:: bash

    SNalert generate --env-file config.env --rate 0.5 --alert-probability 0.1


Alternative Instances
^^^^^^^^^^^^^^^^^^^^^^

If the user does not have access to the Hopskotch or MongoDB server or both,
running local instances is a alternative choice.

* To run a Kafka instance, run the following in the shell

.. code:: bash

    docker run -p 9092:9092 -it --rm --hostname localhost scimma/server:latest --noSecurity

and pass the following Kafka server to SNEWS 2.0

.. code:: python

    kafka://dev.hop.scimma.org:9092/USER-TOPIC

If the user choose this option, be sure to apply the following patch

.. code:: python

    diff --git a/hop/apps/SNalert/model.py b/hop/apps/SNalert/model.py
    index bac2540..3336106 100644
    --- a/hop/apps/SNalert/model.py
    +++ b/hop/apps/SNalert/model.py
    @@ -123,9 +123,10 @@ class Model(object):
             # print(args.drop_db)
             # print(type(args.default_authentication))
             if self.default_auth == False:
    -            username = os.getenv("USERNAME")
    -            password = os.getenv("PASSWORD")
    -            self.auth = Auth(username, password, method=auth.SASLMethod.PLAIN)
    +            self.auth = False
    +            #username = os.getenv("USERNAME")
    +            #password = os.getenv("PASSWORD")
    +            #self.auth = Auth(username, password, method=auth.SASLMethod.PLAIN)
             self.experiment_topic = os.getenv("OBSERVATION_TOPIC")
             self.testing_topic = os.getenv("TESTING_TOPIC")
             self.heartbeat_topic = os.getenv("HEARTBEAT_TOPIC")
    @@ -153,7 +154,8 @@ class Model(object):
                     # print(type(gcn_dict))
                     # print(prepare_gcn(gcn_dict))
                     print("--THE MODEL")
    -                msg_dict = msg.asdict()['content']
    +                #msg_dict = msg.asdict()['content']
    +                msg_dict = json.loads(msg.content['content'])
                     print(msg_dict)
                     print(type(msg_dict))
                     print(msg_dict['header']['SUBJECT'])

to work around the authentication required in the application.

* To run a MongoDB instance, either run

.. code:: bash

    docker run -p 27017:27017 -it --rm --hostname localhost mongo:latest

or run

.. code:: bash

    pip install -U mongoengine

and pass the following MongoDB server to SNEWS 2.0

.. code::

    mongodb://localhost:27017/
