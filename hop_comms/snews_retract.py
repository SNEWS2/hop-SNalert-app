from .snews_db import Storage
import time
import logging
import click
from .hop_pub import Publish_Alert
from .snews_utils import TimeStuff
from .snews_utils import get_detector
import numpy as np


# TODO Need implement retract latest
class Retraction:
    """
    This class is incharge of looking for false observations and retracting alerts

    """

    def __init__(self, env_path=None, use_local=False):
        """
        Constructor method
        """
        self.storage = Storage(drop_db=False, use_local=use_local)
        self.false_coll = self.storage.false_warnings
        self.db_coll = self.storage.coll_list
        self.pub = Publish_Alert(env_path=env_path, use_local=use_local)
        self.times = TimeStuff(env_path=env_path)
        self.post_pub_retraction = False

    def update_alert_item(self, alert_item, ind):
        """
        Takes in alert item (must be a list!) and removes the desired entry
        Parameters
        ----------
        alert_item: 'list'
            item from SNEWS alert
        ind: 'int'
            index of false observation
        Returns
        -------
        alert item without the false observation's features

        """
        alert_item.pop(ind)
        return alert_item

    def id_retraction(self, false_id):
        """
        This method checks for a specific false message id, finds it in a mongo OBS collection 
        , deletes it from the collection, and then publishes the new alert 

        Parameters
        __________
        false_id: 'str'
            message id of false OBS

        """

        if false_id != None:
            obs_type = false_id.split('_')[1]
            alert_collection = self.db_coll[f'{obs_type}Alert']
        else:
            return 'No id given'

        if alert_collection.count() == 0:
            click.secho(f'{"-" * 57}', fg='bright_blue')
            print('No alert_collection have been published..\nCould be in cache.')
            pass

        for alert in alert_collection.find().sort('sent_time'):
            ids = alert['ids']
            index = 0
            for mgs_id in ids:
                if mgs_id == false_id:
                    print(f'found it in alert {alert["_id"]}!!')
                    query = {'_id': alert['_id']}
                    updated_alert = self.retract_all_false_items(alert, index)
                    alert_collection.update_one(filter=query, update={"$set": updated_alert})
                    self.publish_retract(alert)
                    self.post_pub_retraction = True

                index += 1

    def latest_retraction(self, N_retract_latest, which_tier, which_detector):
        """
        This methods will retract the latest messages from 
        """

        if which_tier == 'ALL':
            alert_collection = ['CoincidenceTier', 'SigTier', 'TimeTier']
            for alert_type in alert_collection:
                self.latest_retraction(N_retract_latest=N_retract_latest, which_tier=alert_type,
                                       which_detector=which_detector)

        if N_retract_latest == None:
            pass

        if which_tier != 'ALL' and self.db_coll[f'{which_tier}Alert'].count() == 0:
            click.secho(f'No alerts to retract for {which_tier}'.upper(), fg='red')
            pass

        elif which_tier != 'ALL' and self.db_coll[f'{which_tier}Alert'].count() >= 1:
            click.secho(f'Parsing through {which_tier} Alerts'.upper(), fg='red')
            drop_detector_id = get_detector(detector=which_detector).id
            for alert in self.storage.get_alert_collection(which_tier=which_tier):
                ids = alert['ids']
                ind = len(ids) - 1
                n_drop = N_retract_latest
                if n_drop == 'ALL':
                    n_drop = len(ids) - 1
                query = {'_id': alert['_id']}
                for id in reversed(ids):
                    detector_id = id.split('_')[0]
                    if detector_id == drop_detector_id:
                        n_drop -= 1
                        updated_alert = self.retract_all_false_items(alert=alert, ind=ind, n_drop=n_drop)
                        alert_collection.update_one(filter=query, update={"$set": updated_alert})
                    if n_drop == 0:
                        break
                    ind -= 1
                self.publish_retract(alert)
                self.post_pub_retraction = True

    def retract_all_false_items(self, alert, ind, n_drop):
        """
        Parses alert dict,pops the items belonging to the false observation,
        determines if the alert is still valid and updates it.
        valid if 'VALID_ALERT??' = 1, invalid if 'VALID_ALERT??' = 0

        Parameters
        ----------
        alert: 'dict'
            SNEWS alert dictionary
        ind: 'int'
            index of false observation

        """

        alert.update(
            {
                'detector_names': self.update_alert_item(alert['detector_names'], ind),
                'ids': self.update_alert_item(alert['ids'], ind),
                'neutrino_times': self.update_alert_item(alert['neutrino_times'], ind),
                'machine_times': self.update_alert_item(alert['machine_times'], ind),
                # 'locations': self.update_alert_item(alert['locations'], ind),
                'time_of_retraction': self.times.get_snews_time(),

            }
        )
        validity = 0
        if len(np.unique(alert['detector_names'])) > 1:
            validity = 1
        alert.update({'VALID_ALERT??': validity})
        alert.update({'Events_retracted': n_drop})

        return alert

    def publish_retract(self, alert):
        """
        Publishes the retracted alert

        Parameters
        ----------
        alert: 'dict'
            SNEWS alert dictionary

        """
        self.pub.publish_retraction(retracted_mgs=alert)
    def delete_old_false_warning(self, false_mgs):
        """
        Deletes false warning after it's used for retraction.

        Parameters
        ----------
        false_mgs: 'dict'
            false warning message
        """
        if self.post_pub_retraction:
            print('deleting false message')
            query = {'_id': false_mgs['_id']}
            self.false_coll.delete_one(query)
            if self.false_coll.count() == 0:
                self.check_for_false()

    def maintain_stream(self):
        curr_false_message_count = self.storage.false_warnings.count()

        while curr_false_message_count == self.storage.false_warnings.count():
            pass


    def check_for_false(self):
        """
        Main body, this method sets up stream using the fasle message collection.
        For each false message the method will the loop through all alert_collection that have been published.
        For each alert it will then loop through its ids list.
        If a false message is found, all items belonging to that false message will be deleted.
        Afterwards the alert's validity will be evaluated.

        """
        with self.false_coll.watch() as stream:
            if self.storage.empty_false_warnings():
                click.secho(f'{"-" * 57}', fg='bright_blue')
                print('No false warnings')
            for doc in stream:
                false_mgs = doc['fullDocument']
                which_tier = false_mgs['which_tier'] or false_mgs['_id'].split('_')[1]
                click.secho(f'{"-" * 57}', fg='bright_blue')
                click.secho(f'Received a false warning... checking alerts'.upper(), fg='bright_blue')
                self.id_retraction(false_id=false_mgs['false_id'])
                self.latest_retraction(which_detector=false_mgs['detector_name'],
                                       N_retract_latest=false_mgs['N_retract_latest'],
                                       which_tier=which_tier)
                self.delete_old_false_warning(false_mgs)

