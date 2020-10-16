# Using the `snews` app with the SCIMMA Hopskotch server
This tutorial will show you how to use the `snews` app to connect to the SCIMMA Hopskotch messaging network.
This can be done using either a local or cloud instance of `snews`; it is recommended that you start with a local instance for testing,
and then move to a cloud provider if needed for your production services.

In either case, you will need to create a Hopskotch account before connecting to the network. If you want to do entirely local testing without a Hopskotch account, refer to the [local snews notes](https://github.com/RiceAstroparticleLab/hop-SNalert-app/blob/demo/tutorial/snews-local-tutorial.md).

## Account Setup
To connect to the Hopskotch server, you will need to create a SNEWS user account and Hopskotch credentials.

### Create User Account
You will need to request access to the SNEWS user group in SCIMMA Hopskotch via CILogon at https://scimma.github.io/IAM/.

Log on through your corresponding institution and click `Begin` to start the account setup process.

Once you complete the setup, the account can then be approved by a SNEWS admin.

### Rwquest Group Access
After your account has been approved, you must add yourself to the Hopskotch user group inside COManage:
* Go to  https://registry.scimma.org/registry/co_groups/index/co:2
* Select "Manage My Group Memberships" in the upper-rigth
* Find the `kafkaUsers` group (it may not be on the first page) and select the "Member" checkbox
* Select `SAVE` in the bottom-right

You will then need to be added to the `SCIMMA Institute Active Members` group by a SCIMMA admin.

### Create Hopskotch Credentials
Once your request to join the `SCIMMA Institute Active Members` group has been approved, you are now able to generate credentials to access the SCIMMA Hopskotch server.

* Request credentials at: https://admin.dev.hop.scimma.org/hopauth/

### Store credentials via `hop-client`
The `hop-client` is a Python package that provides client access to the Hopskotch server, and centralizes the authentication configuration. It will be installed when you install the `snews` app.

#### Installing `snews

When installing `snews`, a virtual environment is recommended to manage packages. You must have either `pip` or `conda`:

* pip (requires `python3-venv`):
  ```
  python3 -m venv snews-venv
  source snews-venv/bin/activate
  pip install pip --upgrade
  ```
* conda (requires `pip`):
  ```
  conda create --name snews-venv python=3.7
  conda activate snews-venv
  conda install git pip
  ```

You can then install `snews` directly from Github:
```
pip install git+https://github.com/RiceAstroparticleLab/hop-SNalert-app.git@demo/tutorial
```

Verify your installation by checking `snews --version` and `hop --version`:
```
snews --version
  SNalert version 0.0.1

hop --version
  hop version 0.2
```

#### Storing your credentials
You are now ready to store the Hopskotch credentials you generated above. Enter the credentials into the prompts when setting up your hop authorization:
```
hop configure setup
```

The configuration file that holds the credentials can be found via:
```
hop configure locate
```

## Connecting to the SNEWS network
Once your Hopskotch credentials are stored, you are ready to connect to the SNEWS network to send and receive messages.

For the development testing network, download the development SNEWS configuration from https://github.com/SNEWS2/snews2-config/blob/master/dev-config.env. Load this configuration before sending/receiving messages via `source dev-config.env`.

### Sending messages
You can use either `snews generate` or `hop publish` to send sample messages to the SNEWS network.

#### `snews generate`
The `snews generate` function is useful for sending default test messages that mimic detections/heartbeats from observatories. The rate and significance of the test messages can be customized; see `snews generate --help` for all options.

For example, to send a signal message that is guaranteed to be a detection, use:
```
snews generate --env-file dev-config.env --alert-probability 1
```

Or, to send a stream of messages that each have a 1% chance to be a detection, use:
```
snews generate --env-file dev-config.env --rate 0.5 --alert-probability 0.01
```

#### `hop publish`
The `hop publish` function can be used to send custom messages to the SNEWS network. The messages should adhere to the [SNEWS plugin message formats](https://hop-plugin-snews.readthedocs.io/en/latest/user/messages.html) to be parsed properly.

For example, to send a message file `detector-observation.txt` that is formatted as a [SNEWSOBSERVATION](https://hop-plugin-snews.readthedocs.io/en/latest/user/messages.html#observation-message) message:
```
source dev-config.env
hop publish --format SNEWSOBSERVATION $OBSERVATION_TOPIC detector-observation.txt
```

### Reading messages
You can use `hop subscribe` to read messages that are being sent to the SNEWS network of topics. These messages are sent to either the OBSERVATION_TOPIC or ALERT_TOPIC, depending on if the message is a detector observation/heartbeat, or a detector alert announcing a coincidence between observation messages. See `hop subscribe --help` for all options.

For example, to continuously read any alert messages that are sent:
```
source dev-config.env
hop subscribe $ALERT_TOPIC -p
```

# Resources

## Source code
* `snews` app: https://github.com/RiceAstroparticleLab/hop-SNalert-app
  * Docs: https://hop-snalert-app.readthedocs.io/en/latest/index.html
* `hop-client`: https://github.com/scimma/hop-client
  * Docs: https://hop-client.readthedocs.io/en/latest/index.html
* `snews` message plugin: https://github.com/SNEWS2/hop-plugin-snews
  * Docs: https://hop-plugin-snews.readthedocs.io/en/latest/
* hop app template: https://github.com/scimma/hop-app-template

## `hop-client` package repositories
* pypi: https://pypi.org/project/hop-client/
* conda: https://anaconda.org/scimma/hop-client
