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
        self.data = {}
        self.stats = {}

    def load_pickle(self, filename):
        self.filename = filename
        pdata = None
        print "Loading pickle file %s ..." % filename
        with open(filename, 'rb') as f:
            pdata = pickle.load(f)
        self.issues = pdata    
        #print "Merging pickle data into issues ..."     
        #for x in pdata:
        #    if x not in self.issues:
        #        self.issues.append(x)    

    def process_data(self):                
        print "Processing data and running stats ..."
        #self.get_pr_close_ages()        
        self.get_close_ages_by_month(itype='pull')        
        self.get_close_ages_by_month(itype='issue')        
        #self.get_issue_close_ages()        
        #import epdb; epdb.st()

    def get_pr_close_ages(self, start=None, end=None):        
        ages = []
        for x in self.issues:
            if not x.state == 'closed' or not x.pull_request:
                continue
            ages.append( x.closed_at - x.created_at )
        ages = [x.total_seconds() for x in ages]    
        self.data['pr_ages'] = ages
        self.stats['pr_close_age_median'] = statistics.median(ages)
        self.stats['pr_close_age_mean'] = statistics.mean(ages)
        try:
            self.stats['pr_close_age_mode'] = statistics.mode(ages)
        except statistics.StatisticsError:
            self.stats['pr_close_age_mode'] = None
        return ages

    def get_issue_close_ages(self, start=None, end=None):        
        ages = []
        for x in self.issues:
            if not x.state == 'closed' or x.pull_request:
                continue
            ages.append( x.closed_at - x.created_at )
        ages = [x.total_seconds() for x in ages]    
        self.data['issue_ages'] = ages
        self.stats['issue_close_age_median'] = statistics.median(ages)
        self.stats['issue_close_age_mean'] = statistics.mean(ages)
        try:
            self.stats['issue_close_age_mode'] = statistics.mode(ages)
        except statistics.StatisticsError:
            self.stats['issue_close_age_mode'] = None
        return ages


    def get_close_ages_by_month(self, itype='pull'):        

        # http://stackoverflow.com/a/18677517

        dates = []
        ages = []

        for x in self.issues:
            if itype == 'pull':
                if not x.state == 'closed' or not x.pull_request:
                    continue
            else:        
                if not x.state == 'closed' or x.pull_request:
                    continue
            #print x
            timestamp = x.closed_at.isoformat()
            # calc seconds open
            age = (x.closed_at - x.created_at).total_seconds()
            # convert seconds to days
            age, seconds = divmod(age, 24*60*60)
            dates.append(timestamp)
            ages.append(age)
            #import epdb; epdb.st()

        ddict = {'date': dates,
                 'age': ages}
        df = pd.DataFrame(ddict, columns=['date', 'age'])

        # 2015-03-23T05:24:02
        dformat = '%Y-%m-%dT%H:%M:%S'
        df['date'] = pd.to_datetime(df['date'], format=dformat)

        df = df.set_index('date')

        # calculate total closures
        bymonth_totals = df.resample('M').count()
        bymonth_totals.columns = ['total_closed']

        # calculate medians
        bymonth_medians = df.resample('M').median()
        bymonth_medians.columns = ['median_age_days']

        # calcuate means
        bymonth_means = df.resample('M').mean()
        bymonth_means.columns = ['mean_age_days']

        # join the columns (axis sets the date as the key)
        result = pd.concat([bymonth_totals, bymonth_means, bymonth_medians], axis=1)

        # clear NaNs
        result = result[pd.notnull(result['mean_age_days'])]
        print result
        #import epdb; epdb.st()











