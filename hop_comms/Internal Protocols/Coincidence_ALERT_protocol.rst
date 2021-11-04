Protocols for Publishing SNEWS Coincidence Alerts
====================================================

For SNEWS 2.0 Users

| Version 0.1
| Prepared by
| Sebastian Torres-Lara
|

.. contents:: Table of Contents

Revision History
----------------

+-----------------------+----------+----------------------+-----------+
| Name                  | Date     | Reason For Changes   | Version   |
+=======================+==========+======================+===========+
| Sebastian Torres-Lara | 04/11/21 | Initial Commit       | 0.01      |
+-----------------------+----------+----------------------+-----------+
+-----------------------+----------+----------------------+-----------+
+-----------------------+----------+----------------------+-----------+

1. Introduction
---------------
This page will go through the format the of Coincidence Alerts and when they are published to


2. Security
-----------

For the sake of testing any user with hop-auth credentials can publish an alert. However, for actual deployment only SNEWS will be able to publish alerts


3. Dependencies
---------------

Dependent on ``[unnamed Coincidence system]`` publish method (name of method) and ``snews_coinc.py``



4. Coincidence Alert Message Structure
--------------------

Note: All SNEWS messages (OBS/ALERT) are sent out as Python dictionaries.

4.1 Coincidence Tier Schema
~~~~~~~~~~~~~~~~~~~~~~~~~~~
As of 11/02/21 has agreed to use the following schema.

#. ``_id``

#. ``num_events``

#. ``initial_nu_times``

#. ``avg_p_val``

#. ``ids``


4.1.1 Coincidence Tier Schema
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. ``_id`` is a string (created by built in method) that give each message sent to SNEWS a unique name, format is the following:

    SNEWS_CoincidenceTierALERT_[sent_time in SNEWS format: D/M/Y_H:M:S:mS]

    Example: ``SNEWS_CoincidenceTierALERT_02/11/21_21:57:20:19856``

#. ``num_events``  dictionary object

#. ``initial_nu_times`` dictionary object

#. ``avg_p_val`` dictionary object

#. ``ids`` list object

