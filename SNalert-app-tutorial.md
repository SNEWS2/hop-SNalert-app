TODO:
* reduce the scimma-server image size?
* update any repos/installs to reflect name/plugin changes
* update the message content in SNalert-generate for the user

# SNEWS SNalert app Tutorial

This is a tutorial on how to install and run the SNEWS SuperNova alert app, a Python program that uses the `hop-client` software to send messages for multi-messenger astrophysics.

This tutorial will show you how to create a local messaging system which will:
1) create messages from mock astrophysics experiments
2) process those messages
3) send out alerts if any two of those messages are significant and coincident

To run the SuperNova Alert ("SNalert") app, you will need:
* Python version >= 3.6
* Docker

To download files in this tutorial, you will need:
* curl

It is recommended that you use virtual environments (with `python3-venv`) or `conda` to manage packages.

Refer to the `Resources` at the end of this tutorial for the documentation and source code of the software used in this tutorial.


## Step 1: Installing SNEWS SNalert

To install `SNAlert`, you must have either `pip` or `conda`.


<> This tutorial also uses `curl`. If you're not using `conda`, here are some hints on how to install these on some common Linux systems:
<> * Debian (including Ubuntu):
<>   ```
<>    sudo apt-get update && sudo apt-get install python3-pip curl
<>    ```
<> * Centos:
<>   ```
<>   yum install python36 python36-devel python36-setuptools curl
<>   easy_install-3.6 pip
<>   ```

### Setting up a virtual environment (recommended)
Running this demo in a virtual environment will help keep your default system packages and the demo's installation dependencies separate.

You can then use either pip or conda to create a virtual environment:
* pip:
  ```
  python3 -m venv snews-venv
  source snews-venv/bin/activate
  ```
* conda (you will also need `pip` and `git` to install the `SNalert` app)
  ```
  conda create --name snews-venv python=3.7
  conda activate snews-venv
  conda install git pip
  ```

### Installing SNalert

You can install `SNalert` directly from Github:
```
pip install git+https://github.com/RiceAstroparticleLab/hop-SNalert-app.git
```

Verify your `hop-client` install by checking `hop version`:
```
# hop version
hop version 0.2
```

Verify your `SNalert` install by checking `SNalert --version`:
```
# SNalert --version
SNalert version 0.0.1
```

## Step 2: Preparing your environment

To run the SNalert app, you will need to download two files using `curl`.

### Downloading the environment and container files

To download the required files, run these two `curl` commands (note: you may want to create a separate directory for these files with, e.g., `mkdir snalert-files; cd snalert-files`):
```
curl https://raw.githubusercontent.com/RiceAstroparticleLab/hop-SNalert-app/demo/tutorial/example.env -o example.env
curl https://raw.githubusercontent.com/RiceAstroparticleLab/hop-SNalert-app/master/run-containers.sh -o run-containers.sh
```

You may alternatively get these files by cloning the source code from Github using:
```
git clone -b demo/tutorial https://github.com/RiceAstroparticleLab/hop-SNalert-app.git
cd hop-SNalert-app
```

### Activating your environment

To set up your environment with the SCIMMA kafka server, the SNalert's database, and environment variables, source the two files you downloaded while inside the folder containing them:
```
source run-containers.sh
source example.env
```

## Step 3: Running SNalert

You are now ready to run the SNalert app. This involves running four processes simultaneously:
  1) `SNalert model`: manages the message parser and database
  2-3) `hop subscribe` x2: read messages sent by the `model` and `generator`
  4) `SNalert generate`: create and send sample experiment messages


To visualize all processes, you may want to use multiple terminal windows or panes (or create virtual terminals with e.g. emacs, tmux, etc.).

### `SNalert model`
In one terminal, enter this command to start up the app:
```
SNalert model --env-file example.env --no-auth
```

### `hop subscribe`

#### Reading alert messages
One subscriber will be used to read alert messages sent by `model`. Enter this command in another terminal:
```
hop subscribe --no-auth $ALERT_TOPIC -p
```
#### Reading experiment messages
A second subscriber will be used to read sample experiment messages sent by `generate`. Enter this command in another terminal:
```
hop subscribe --no-auth $OBSERVATION_TOPIC -p
```

### `SNalert generate`
You are now ready to test the SNalert app by having mock experiments send detection messages.

#### Generate the messages
In a new terminal, start generating these mock messages by entering:
```
SNalert generate --env-file example.env --rate 0.5 --alert-probability 0.1 -p
```

#### Test the app
You should now see messages streaming into the terminal reading the experiment messages. Most of these messages (90%) will not be "significant."

But eventually, more than one significant message will be sent within in short time window. When this happens, the `model` app will notice a "coincidence" between these significant messages, which trigger the app to send an alert message, which will appear in your first terminal.

These alert messages mean that several different (mock) experiments might have observed the same astrophysical event, hinting at a possible Galactic Supernova!

## Extra

The app has several customizable options which change its behavior. Trying playing with a few of the options below, and refer to the source code and documentation for more options and help.

* With `generate`, try changing the `--rate` and `--alert-probability` options to see how it affects the rates of message coincidence
* Try editing the `example.env` file with different values of `COINCIDENCE_THRESHOLD` to change the time window (in seconds) that the app searches for message coincidences
* Try sending individual alerts with `generate` in different terminals, instead of using `-p` to send endless messages

## Cleanup
When you're finished with the tutorial:
* exit out of each of the `subscribe`, `model`, `generate` processes by pressing `Ctrl-C`
* deactivate your virtual environment if you were using one: `deactivate` for pip or `conda deactivate` for conda

## Resources

### Source code
* `SNalert` app: https://github.com/RiceAstroparticleLab/hop-SNalert-app
  * Docs: https://hop-snalert-app.readthedocs.io/en/latest/index.html
* `hop-client`: https://github.com/scimma/hop-client
  * Docs: https://hop-client.readthedocs.io/en/latest/index.html
* hop app template: https://github.com/scimma/hop-app-template

### `hop-client` package repositories
* conda: https://anaconda.org/scimma/hop-client
* pypi: https://pypi.org/project/hop-client/
