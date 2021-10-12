# Quickstart

The module allows you to `publish`, `subscribe`, `retract` and `simulate` observation messages among other things. For these to work an environment file specifying the related kafka and mongo servers is needed. While a default file ('hop_comms/auxiliary/test-config.env') comes with the package, it can also be set from the command line on-flight.  

Below, we present a quick start for the Supernova Early Warning System communication tools [Python API](#Python-Api) using both [Jupyter Notebooks](#snews-on-jupyter-notebooks), and also the [command line interface](#command-line-interface)(CLI).

While can be called from terminal using a CLI, the package also allows jupyter notebook interactions as described in [Python API](#Python-Api)

**Table of Contents**
1. [SNEWS on Jupyter Notebooks](#python-api)
    1. [Subscribe](#subscribing-to-a-topic)
    2. [Publish](#publishing-to-a-topic)
    
2. [Command Line Interface-(CLI)](#command-line-interface)
    1. [Subscribe](#subscribe)
    2. [Publish](#publish)
    3. [Coincidence Decider](#coincidence-decider)
    4. [Simulate Observation](#simulation)


## Python-Api
The hop_comms modules are IPython friendly and can be executed in jupyter notebook environments. However, in order to execute different cells asynchronously, one need to invoke `ipyparallel` first. For this, launch a new linux terminal and eun the following commands;
```bash
conda install ipyparallel
ipcluster nbextension enable -n 2
ipcluster start -n 2
```
This enables the relevant notebook extension to executes multiple cells together. After setting this, go back to jupyter notebook and import `ipyparallel` and `hop_comms`.

```python
from ipyparallel import Client
rc = Client()
```

### Subscribing to a topic
To execute different cells together, a _jupyter magic command_ has to be provided in the beginning of each cell
```python
%%px -a -t 0
from hop_comms.hop_sub import HopSubscribe
sub = HopSubscribe()
sub.subscribe()
```

The `hop_comms.hop_sub.HopSubscribe().subscribe()` command subscribes to the **observation** topic that is set by the environment variable by default. The default environment configuration is provided by the package but can also be provided by the user.<br>

```python
from hop_comms.snews_utils import set_env
set_env(<THE PATH TO YOUR CONFIG FILE>)
```

### Publishing to a topic

```python
%%px -a -t 1
from hop_comms.hop_pub import Publish_Tier_Obs
from hop_comms.snews_utils import data_obs

pub = Publish_Tier_Obs()
data = data_obs() # default values 
pub.publish(<EXPERIMENT NAME>, "CoincidenceTier", data)
```

the `snews_utils.data_obs` provides the message template set by `hop_comms.hop_mgs_schema`, all values are default to `None`. 


## Command Line Interface

### Subscribe

### Publish

### Coincidence Decider

### Simulation

### Decider



Notes
-----

- In general, subscription is only possible for the *Alert* topics
- To publish and subscribe user needs necessary kafka credentials.
- For the moment, the coincidence decider needs to be called externally