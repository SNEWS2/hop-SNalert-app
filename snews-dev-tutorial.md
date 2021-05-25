# Using `snews` with the SCIMMA Hopskotch server
This tutorial will show you how to use the `snews` app to connect to the [SCIMMA Hopskotch](https://hop.scimma.org) messaging network. This can be done using either a local or cloud installation of `snews`. It is recommended that you start with a local installation for testing, and then move to a cloud provider if needed for your production services.

In either case, you will need to create a Hopskotch account before connecting to the network. If you want to do entirely local testing without a Hopskotch account, refer to the [local snews notes](https://github.com/RiceAstroparticleLab/hop-SNalert-app/blob/demo/tutorial/snews-local-tutorial.md).

## Account Setup
To connect to the Hopskotch server, you will need to create a SNEWS user account and Hopskotch credentials.

### Create User Account
You will need to request access to the SNEWS user group in SCIMMA Hopskotch via CILogon at https://my.hop.scimma.org/hopauth. Refer to the page if you need to create an account. For more information, see the [SCiMMA IAM docs](https://hop.scimma.org/IAM/Instructions/JoinInstitute) or the [Hopskotch Authenticator docs](https://github.com/scimma/scimma-admin/blob/master/doc/hopauth_guide.md#hopauth-for-users) for account management help.

Log on through your corresponding institution and click `Begin` to start the account setup process.

Once you complete the setup, the account can then be approved by a SNEWS admin.

### Request Group Access (if needed)
After your account has been approved, you will now be a `SCiMMA Active Collaborator`, which should automatically grant you access to Hopskotch as a `kafkaUser`.

If you do not have `kafkaUser` status, you must add yourself to the Hopskotch user group inside COManage:
* Go to https://registry.scimma.org/registry/co_petitions/start/coef:127
* Select "Manage My Group Memberships" in the upper-right
* Find the `kafkaUsers` group (it may not be on the first page) and select the "Member" checkbox
* Select `SAVE` in the bottom-right

### Generating and Storing Credentials
Once you are a part of `SCIMMA Active Collaborators` (or `Active Members`), you will be able to generate credentials to access the SCIMMA Hopskotch server.

However, before you generate credentials, it is recommended that you install `hop-client`. This is a SCIMMA Python package that provides client access to the Hopskotch server; it also centralizes and simplifies the authentication configuration. It will be installed when you install the `snews` app.

#### Installing `hop-client` with `snews`

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
  hop version 0.4
```

The `hop-client` also allows you to interact with the Hopskotch server network including GCN message streams and a Jupyter notebook environment; see [hop.SCiMMA](https://hop.scimma.org) for more information.

### Create and Store Hopskotch Credentials
After `hop-client` is successfully installed, you are ready to generate Hopskotch credentials and store them with `hop-client` (follow the steps from the [Hopskotch Authenticator](https://github.com/scimma/scimma-admin/blob/master/doc/hopauth_guide.md#creating-a-credential) for help):
* Generate credentials at: https://my.hop.scimma.org/hopauth/
* Enter these credentials into the prompts when setting up your hop authorization:
```
hop auth add
Username: <paste-your-username>
Password: <paste-your-password>    # note that this will not show your password; just press enter after you paste it
Hostname (may be empty): kafka.scimma.org
```

The configuration file that holds the credentials can be found via:
```
hop auth locate
```

### Accessing SNEWS Hopskotch data stream topics
Once you have your credentials, a SCiMMA admin can grant you access to the SNEWS data streams ("topics") in Hopskotch. Once you have access, you must then enable access to the data streams used in this tutorial.

This can be done by adding topic permissions to your Hopskotch account. [Online documentation](https://github.com/scimma/scimma-admin/blob/master/doc/hopauth_guide.md#adding-capabilities-to-a-credential) has steps and images of this process, which involves:
* Going to the [Hopskotch auth website](https://my.hop.scimma.org/hopauth/) to `Edit` your `Active Credentials`
* Go to `Add Permission`, select `snews.testing: All` topic from the dropdown, then click `Add permission`. Do this for the `snews.alert-test` and `snews.experiments-test` topics.

These changes may take several minutes to take effect, but afterwards you will now have permission to access the SNEWS topic network.

## Connecting to the SNEWS network
Once your Hopskotch credentials are stored and you have configured your access to SNEWS topics, you are ready to connect to the SNEWS network to send and receive messages.

To do this, download a topic configuration file from the [SNEWS2.0 GitHub repository](https://github.com/SNEWS2/snews2-config). Select the `.env` file depending on your usage:
* for this tutorial, use the [test-config.env](https://github.com/SNEWS2/snews2-config/blob/master/test-config.env) to connect to non-production test topics on a stable instance of Hopskotch.
* the [prod-config.env](https://github.com/SNEWS2/snews2-config/blob/master/prod-config.env) can be used to connect to production topics on a stable instance of Hopskotch.
* the [dev-config.env](https://github.com/SNEWS2/snews2-config/blob/master/dev-config.env) can be used to connect to test topics on the development instance of Hopskotch. You would need separate credentials for the development instance; your credentials for the production Hopskotch instance will not work.

Load your configuration file before sending/receiving messages via `source test-config.env`.

### Sending messages
You can use either `snews generate` or `hop publish` to send sample messages to the SNEWS network.

#### `snews generate`
The `snews generate` function is useful for sending default test messages that mimic detections/heartbeats from observatories. The rate and significance of the test messages can be customized; see `snews generate --help` for all options.

For example, to send a signal message that is guaranteed to be a detection, use:
```
snews generate --env-file test-config.env --alert-probability 1
```

Or, to send a stream of messages that each have a 1% chance to be a detection, use:
```
snews generate --env-file test-config.env --rate 0.5 --alert-probability 0.01
```

#### `hop publish`
The `hop publish` function can be used to send custom messages to the SNEWS network. The messages should adhere to the [SNEWS plugin message formats](https://hop-plugin-snews.readthedocs.io/en/latest/user/messages.html) to be parsed properly.

For example, to send a message file `detector-observation.txt` that is formatted as a [SNEWSOBSERVATION](https://hop-plugin-snews.readthedocs.io/en/latest/user/messages.html#observation-message) message:
```
source test-config.env
hop publish --format SNEWSOBSERVATION $OBSERVATION_TOPIC detector-observation.txt
```

Example messages for the `SNEWSALERT`, `SNEWSOBSERVATION`, and `SNEWSHEARTBEAT` formats can be found as [snews-alert.txt](https://github.com/SNEWS2/hop-SNalert-app/blob/demo/tutorial/snews-alert.txt), [detector-observation.txt](https://github.com/SNEWS2/hop-SNalert-app/blob/demo/tutorial/detector-observation.txt), and [detector-heartbeat.txt](https://github.com/SNEWS2/hop-SNalert-app/blob/demo/tutorial/detector-heartbeat.txt), respectively.

### Reading messages
You can use `hop subscribe` to read messages that are being sent to the SNEWS network of topics. These messages are sent to either the OBSERVATION_TOPIC or ALERT_TOPIC, depending on if the message is a detector observation/heartbeat, or a detector alert announcing a coincidence between observation messages. See `hop subscribe --help` for all options.

For example, to continuously read any alert messages that are sent:
```
source test-config.env
hop subscribe $ALERT_TOPIC --persist
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
