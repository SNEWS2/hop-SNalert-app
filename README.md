# hop-SNalert-app

An alert application for observing supernovae with the SNEWS detector network.

|              |        |
| ------------ | ------ |
| **Docs:**    | https://hop-snalert-app.readthedocs.io/en/latest/  |


## Prerequisite
* Python 3.6 or above

## Overview
This is an alert application that extends the [SCiMMA hop-client](https://github.com/scimma/hop-client) using the [hop-client cookiecutter template](https://github.com/scimma/hop-app-template). This application monitors 
the observations published by detectors in the SuperNova Early Warning System (SNEWS) network, and can optionally send alerts upon
the detection of a potential supernova.

The application consists of:
* **storage** -
  data structure to store recent messages and remove old messages
* **decider** - 
  applies message parsing logic to decide if incoming messages indicate a supernova
* **model** - 
  instantiates a decider object and connects to SCiMMA HOPSKOTCH message streams; passes messages using hop.stream to the decider; publishes an alert message if the decider indicates a supernova

The application utilizes the `hop-plugin-snews` plugin to provide custom message formats: see the [repository](https://github.com/SNEWS2/hop-plugin-snews) and [documentation] for more details about this format, and see the [hop-client message formats](https://hop-client.readthedocs.io/en/latest/user/models.html) for information on specifying other custom formats.

With appropriate HOPSKOTCH authentication, a user can use the application to publish and subscribe to the online topic "**snews-TOPIC**".


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
#### Install snews
* pip
  ```
  pip install git+https://github.com/RiceAstroparticleLab/hop-SNalert-app.git
  ```
#### Basic command-lines
* running the app:
  ```
  snews model --env-file example.env --no-auth
  ```
* generating test messages:
  ```
  snews generate --env-file example.env --rate 0.5 --alert-probability 0.1 --persist --no-auth
  ```
  
## Tutorial

For a full tutorial on how to set up the application with local message streams, follow the guide here: https://github.com/RiceAstroparticleLab/hop-SNalert-app/blob/demo/tutorial/snews-local-tutorial.md

For a full tutorial on how to set up the application with the SCiMMA HOPSKOTCH network and request HOPSKOTCH credentials, follow the guide here: https://github.com/RiceAstroparticleLab/hop-SNalert-app/blob/demo/tutorial/snews-dev-tutorial.md.
