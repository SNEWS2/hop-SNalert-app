from .snews_db import Storage
import time
import logging
import click


class RetractionCoincidence:
    """
    This class is incharge of looking for false observations and retracting alerts
    """
    def __init__(self):
        """
        Constructor method
        """
        self.storage = Storage(drop_db=False)
        self.false_coll = self.storage.false_warnings
        self.db_coll = self.storage.coll_list

    def retract_all_false_items(self, alert, counter):
        """
        Parses alert dict,pops the items belonging to the false observation, and updates it.

        Parameters
        ----------
        alert: 'dict'
            SNEWS alert dictionary
        counter: 'int'
            index of false observation
        """
        alert.update(
            {'detector_names': alert['detector_names'].pop(counter)},
            {'ids': alert['ids'].pop(counter)},
            {'neutrino_times': alert['neutrino_times'].pop(counter)},
            {'machine_time': alert['machine_times'].pop(counter)},
            {'locations': alert['locations'.pop(counter)]},
            {'RETRACTED': 1},
        )

    def check_for_false(self):
        with self.false_coll.watch() as stream:
            if self.storage.empty_false_warnings():
                click.secho(f'{"-" * 57}', fg='bright_blue')
                print('No false warnings')
            for doc in stream:
                click.secho(f'{"-" * 57}', fg='bright_blue')
                false_mgs = doc['fullDocument']
                false_id = false_mgs['false_id']
                obs_type = false_id.split('_')[1]
                self.alerts = self.db_coll[f'{obs_type}Alert']
                if self.alerts.count() == 0:
                    click.secho(f'{"-" * 57}', fg='bright_blue')
                    print('No alerts have been published..\nCould be in cache.')
                for alert in self.alerts.find().sort('sent_time'):
                    ids = alert['ids']
                    counter = 0
                    for mgs_id in ids:
                        if mgs_id == false:
                            print('found it !!')
                            self.retract_all_false_item(alert, counter)

                        counter += 1
