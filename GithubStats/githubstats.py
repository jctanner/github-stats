#!/usr/bin/env python

#   https://github.com/digitalemagine/py-statistics/blob/master/statistics/__init__.py

import pickle
import statistics
from datetime import timedelta

import pandas as pd

class GithubStats(object):
    def __init__(self):
        self.filename = None
        self.issues = []
        self.data = None
        self.stats = None

    def load_pickle(self, filename):
        self.filename = filename
        pdata = None
        print "Loading pickle file %s ..." % filename
        with open(filename, 'rb') as f:
            pdata = pickle.load(f)
        self.issues = pdata    
        #import epdb; epdb.st()
        #print "Merging pickle data into issues ..."     
        #for x in pdata:
        #    if x not in self.issues:
        #        self.issues.append(x)    

    def process_data(self):        

        # http://stackoverflow.com/a/18677517

        pr_close_dates = []
        pr_close_ages = []

        pr_merged_dates = []
        pr_merged_count = []

        pr_opened_dates = []
        pr_opened_count = []

        issue_close_dates = []
        issue_close_ages = []

        issue_opened_dates = []
        issue_opened_count = []

        for x in self.issues:

            itype = "issue"
            if x.pull_request:
                itype = "pull"

            # openings
            opened = x.created_at.isoformat()
            if itype == 'issue':
                issue_opened_dates.append(opened)
                issue_opened_count.append(1)
            else:    
                pr_opened_dates.append(opened)
                pr_opened_count.append(1)
                        

            # closures
            if x.state == 'closed':
                timestamp = x.closed_at.isoformat()
                # calc seconds open
                age = (x.closed_at - x.created_at).total_seconds()
                # convert seconds to days
                age, seconds = divmod(age, 24*60*60)

                # issue or pr?
                if itype == 'pull':
                    pr_close_dates.append(timestamp)
                    pr_close_ages.append(age)

                    # merged or not? (need PR data)
                    #import epdb; epdb.st()
                else:
                    issue_close_dates.append(timestamp)
                    issue_close_ages.append(age)

        self.data = {
            'pr_close_dates'        : pr_close_dates,
            'pr_close_ages'         : pr_close_ages,
            'pr_merged_dates'       : pr_merged_dates,
            'pr_merged_count'       : pr_merged_count,
            'pr_opened_dates'       : pr_opened_dates,
            'pr_opened_count'       : pr_opened_count,
            'issue_close_dates'     : issue_close_dates,
            'issue_close_ages'      : issue_close_ages,
            'issue_opened_dates'    : issue_opened_dates,
            'issue_opened_count'    : issue_opened_count
            }

        return self.process_stats(data=self.data)


    def process_stats(self, data=None):

        # easier for unit testing ...
        if not data:
            data = self.data

        # 2015-03-23T05:24:02
        dformat = '%Y-%m-%dT%H:%M:%S'

        #############################################
        # PR closures ...
        #############################################

        ddict = {'date': data['pr_close_dates'],
                 'age': data['pr_close_ages']}
        pull_close_df = pd.DataFrame(ddict, columns=['date', 'age'])
        pull_close_df['date'] = pd.to_datetime(pull_close_df['date'], 
                                               format=dformat)
        pull_close_df = pull_close_df.set_index('date')

        # calculate total closures
        pr_close_totals = pull_close_df.resample('M').count()
        pr_close_totals.columns = ['pr_total_closed']
        pr_close_totals.fillna(0)

        # calculate medians
        pr_close_medians = pull_close_df.resample('M').median()
        pr_close_medians.columns = ['pr_close_median_age_days']

        # calculate means
        pr_close_means = pull_close_df.resample('M').mean()
        pr_close_means.columns = ['pr_close_mean_age_days']


        #############################################
        # PR openings ...
        #############################################

        ddict = {'date': data['pr_opened_dates'],
                 'i': data['pr_opened_count']}
        pr_opened_df = pd.DataFrame(ddict, columns=['date', 'i'])
        pr_opened_df['date'] = pd.to_datetime(pr_opened_df['date'], 
                                               format=dformat)
        pr_opened_df = pr_opened_df.set_index('date')
        pr_opened_totals = pr_opened_df.resample('M').count()
        pr_opened_totals.columns = ['pr_total_opened']
        pr_opened_totals.fillna(0)


        #############################################
        # Issue closures ...
        #############################################

        ddict = {'date': data['issue_close_dates'],
                 'age': data['issue_close_ages']}
        issue_close_df = pd.DataFrame(ddict, columns=['date', 'age'])
        issue_close_df['date'] = pd.to_datetime(issue_close_df['date'], 
                                               format=dformat)
        issue_close_df = issue_close_df.set_index('date')

        # calculate total closures
        issue_close_totals = issue_close_df.resample('M').count()
        issue_close_totals.columns = ['issue_total_closed']
        issue_close_totals.fillna(0)

        # calculate medians
        issue_close_medians = issue_close_df.resample('M').median()
        issue_close_medians.columns = ['issue_close_median_age_days']

        # calculate means
        issue_close_means = issue_close_df.resample('M').mean()
        issue_close_means.columns = ['issue_close_mean_age_days']

        #############################################
        # Issue openings ...
        #############################################

        ddict = {'date': data['issue_opened_dates'],
                 'i': data['issue_opened_count']}
        issue_opened_df = pd.DataFrame(ddict, columns=['date', 'i'])
        issue_opened_df['date'] = pd.to_datetime(issue_opened_df['date'], 
                                               format=dformat)
        issue_opened_df = issue_opened_df.set_index('date')
        issue_opened_totals = issue_opened_df.resample('M').count()
        issue_opened_totals.columns = ['issue_total_opened']
        issue_opened_totals.fillna(0)
        #import epdb; epdb.st()

        #############################################
        # Aggregate result ...
        #############################################

        columns = [pr_opened_totals, 
                   issue_opened_totals,
                   pr_close_totals, 
                   pr_close_medians, 
                   pr_close_means,
                   issue_close_totals, 
                   issue_close_medians, 
                   issue_close_means ]
        result = pd.concat(columns, axis=1)

        # Fill all NaNs with zeros ...
        for col in result.columns:
            result[col] = result[col].fillna(0)

        # Sum the totals ...
        result['opened_total'] = result['issue_total_opened'] + \
                                 result['pr_total_opened']
        result['closed_total'] = result['issue_total_closed'] + \
                                 result['pr_total_closed']

        self.stats = result
        #import epdb; epdb.st()
        return result


class GithubStatsAggregator(object):

    ''' Join totals for projects with submodules / multi-repos '''

    def __init__(self, dataframes, reponames):
        self.dataframes = dataframes
        self.reponames = reponames
        self.stats = None

    def combine(self):

        # Final result
        xdf = pd.DataFrame()

        for repoid,reponame in enumerate(self.reponames):
            if repoid == 0:
                xdf = self.dataframes[repoid].copy()
            else:
                xdf = xdf.add(self.dataframes[repoid], fill_value=0)        

        #import epdb; epdb.st()
        self.stats = xdf
        return xdf
