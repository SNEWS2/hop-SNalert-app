# hop-SNalert-app

An alert application for observing supernovas in SNEWS community.

## Prerequisite
* Python 3.6 or above

## Overview
This is an alert application on top of SCIMMA hop-client that monitors 
the observations published by experiments and optionally send alerts upon
getting a potential supernova. It composes of
* **deque** -
  data structure that stores recent messages and remove old messages.
* **decider** - 
  Behaviors include adding messages and deciding if current messages indicate a supernova.
* **model** - 
  interact with hopscotch and instantiate a decider object. Pass messages in hop.stream to the decider. 
  Publish to TOPIC 2 if the decider decides “True”.

With appropriate authentication, a user can publish and subscribe to topic "**snews-TOPIC**".

See https://github.com/scimma/hop-client for detailed hop-client documentation.


## Quickstart
#### Setting up a virtual environment
* pip:
```
  python3 -m venv demo-venv
  source demo-venv/bin/activate
  ```
* conda:
  ```
  conda create --name demo-venv python=3.7
  conda activate demo-venv
  ```
#### Install hop-client
* pip
  ```
   pip install -U hop-client
  ```
* conda
  ```
  conda install --channel conda-forge --channel scimma hop-client
  ```
Verify your install with `hop`'s help:
  ```
  hop --help
  ```
#### Basic command-lines
* publish
  ```
  hop publish kafka://SERVER/TOPIC -F config.conf example.gcn3
  ```
* subscribe
  ```
  hop subscribe kafka://SERVER/TOPIC -F config.conf -e
  ```
## Tutorial




```
from hop.apps import SNalert

# do cool application stuff here
```
