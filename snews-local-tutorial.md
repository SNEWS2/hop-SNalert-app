# The SuperNova Early Warning System `snews` app

This is a tutorial on how to install and run the SuperNova Early Warning System ("SNEWS") alerting app locally, a Python program that uses the `hop-client` software to help observatories and particle detectors coordinate messages and potentially observe of the next galactic supernova.

This tutorial will show you how to create a local messaging system which will:
1) create messages from mock astrophysics experiments
2) process those messages
3) send out alerts if any two of those messages are significant and coincident

To run this tutorial, you will need:
* Python version >= 3.6
* Docker
* curl
* either `python3-venv` or `conda`

It is recommended that you use virtual environments (with `python3-venv`) or `conda` to manage packages.

Refer to the `Resources` at the end of this tutorial for the documentation and source code of the software used in this tutorial.

## Step 1: Installing `snews`

To install `snews`, you must have either `pip` or `conda`.

### Setting up a virtual environment (recommended)
Running this demo in a virtual environment will help keep your default system packages and the demo's installation dependencies separate.

First, make a folder for this demo and enter it:
```
mkdir snews-tutorial
cd snews-tutorial
```

You can use either pip or conda to create a virtual environment:
* pip:
  ```
  python3 -m venv snews-venv
  source snews-venv/bin/activate
  pip install pip --upgrade
  ```
* conda (you will also need `pip` and `git` to install `snews`)
  ```
  conda create --name snews-venv python=3.7
  conda activate snews-venv
  conda install git pip
  ```

### Installing `snews`

You can then install `snews` directly from Github:
```
pip install git+https://github.com/RiceAstroparticleLab/hop-SNalert-app.git@demo/tutorial
```

Verify your installation by checking `snews --version` and `hop --version`:
```
# snews --version
snews version 0.0.1
# hop --version
hop version 0.2
```

## Step 2: Preparing your environment

To run `snews`, you will need to download two files using `curl`.

### Downloading the environment and container files

To download the required files, run these two `curl` commands while inside the `snews-tutorial` folder:
```
curl https://raw.githubusercontent.com/RiceAstroparticleLab/hop-SNalert-app/demo/tutorial/example.env -o example.env
curl https://raw.githubusercontent.com/RiceAstroparticleLab/hop-SNalert-app/demo/tutorial/run-containers.sh -o run-containers.sh
```

You may alternatively get these files by cloning the source code from Github using:
```
git clone -b demo/tutorial https://github.com/RiceAstroparticleLab/hop-SNalert-app.git
cd hop-SNalert-app
```

### Activating your environment

To set up your environment with the SCIMMA kafka server, the `snews` database, and environment variables, source the two files you downloaded while inside the folder containing them:
```
source example.env
source run-containers.sh
```

## Step 3: Running `snews`

You are now ready to run the `snews` app. This involves running four processes simultaneously:
  1) `snews model`: manages the message parser and database
  2-3) `hop subscribe` x2: read messages sent by the `model` and `generator`
  4) `snews generate`: create and send sample experiment messages

To visualize all processes, you may want to use multiple terminal windows or panes (or create virtual terminals with e.g. emacs, tmux, etc.). You will need to re-activate your virtual environment and variables in each terminal:
```
source snews-venv/bin/activate
source example.env
```

### `snews model`
In one terminal, enter this command to start up the app:
```
snews model --env-file example.env --no-auth
```

### `hop subscribe`

#### Reading alert messages
One subscriber will be used to read alert messages sent by `model`. Enter this command in another terminal:
```
hop subscribe --no-auth $ALERT_TOPIC --persist
```
#### Reading experiment messages
A second subscriber will be used to read sample experiment messages sent by `generate`. Enter this command in another terminal:
```
hop subscribe --no-auth $OBSERVATION_TOPIC --persist
```

### `snews generate`
You are now ready to test `snews` by having mock experiments send detection messages.

#### Generate the messages
In a new terminal, start generating these mock messages by entering:
```
snews generate --env-file example.env --rate 0.5 --alert-probability 0.1 --persist --no-auth
```

#### Test the app
You should now see messages streaming into the terminal reading the experiment messages. Most of these messages (90%) will not be "significant."

But eventually, more than one significant message will be sent within in short time window. When this happens, the `model` will notice a "coincidence" between these significant messages, which trigger the app to send an alert message, which will appear in your first terminal.

These alert messages mean that several different (mock) experiments might have observed the same astrophysical event, hinting at a possible galactic supernova!

## Extra

The app has several customizable options which change its behavior. Trying playing with a few of the options below, and refer to the source code and documentation for more options and help. You can also check out the options for each function from the command line, e.g. `snews generate --help` or `hop subscribe --help`.

* With `generate`, try changing the `--rate` and `--alert-probability` options to see how it affects the rates of message coincidence
* Try editing the `example.env` file with different values of `COINCIDENCE_THRESHOLD` to change the time window (in seconds) that the app searches for message coincidences.
  * note: you'll have to refresh your environment afterwards again using `source example.env`
* Try sending individual alerts with `generate` in different terminals, instead of using `-p` to send endless messages

## Cleanup
When you're finished with the tutorial:
* exit out of each of the `subscribe`, `model`, `generate` processes by pressing `Ctrl-C`
* deactivate your virtual environment if you were using one: `deactivate` for pip or `conda deactivate` for conda

## Resources

### Source code
* `snews` app: https://github.com/RiceAstroparticleLab/hop-SNalert-app
  * Docs: https://hop-snalert-app.readthedocs.io/en/latest/index.html
* `hop-client`: https://github.com/scimma/hop-client
  * Docs: https://hop-client.readthedocs.io/en/latest/index.html
* hop app template: https://github.com/scimma/hop-app-template

### `hop-client` package repositories
* conda: https://anaconda.org/scimma/hop-client
* pypi: https://pypi.org/project/hop-client/
