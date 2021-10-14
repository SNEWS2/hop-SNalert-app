from .snews_db import Storage
import time
import logging
import click
from .hop_pub import Publish_Alert
from .snews_utils import TimeStuff


#  TODO Still need to test it 13/10/21
class Retraction:
    """
    This class is incharge of looking for false observations and retracting alerts
    """

    def __init__(self, env_path=None):
        """
        Constructor method
        """
        self.storage = Storage(drop_db=False)
        self.false_coll = self.storage.false_warnings
        self.db_coll = self.storage.coll_list
        self.pub = Publish_Alert(env_path=env_path)
        self.times = TimeStuff(env_path=env_path)

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

    def retract_all_false_items(self, alert, ind):
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
        if len(alert['detector_names']) > 1:
            validity = 1
        alert.update({'VALID_ALERT??': validity})

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
                click.secho(f'{"-" * 57}', fg='bright_blue')
                false_mgs = doc['fullDocument']
                false_id = false_mgs['false_id']
                obs_type = false_id.split('_')[1]
                alert_collection = self.db_coll[f'{obs_type}Alert']
                if alert_collection.count() == 0:
                    click.secho(f'{"-" * 57}', fg='bright_blue')
                    print('No alert_collection have been published..\nCould be in cache.')
                for alert in alert_collection.find().sort('sent_time'):
                    ids = alert['ids']
                    counter = 0
                    for mgs_id in ids:
                        if mgs_id == false_id:
                            print(f'found it in alert {alert["_id"]}!!')
                            query = {'_id': alert['_id']}
                            updated_alert = self.retract_all_false_items(alert, counter)
                            alert_collection.update_one(filter=query, update={"$set": updated_alert})
                            self.publish_retract(alert)

                        counter += 1
