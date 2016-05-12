#!/usr/bin/env python

#   https://github.com/digitalemagine/py-statistics/blob/master/statistics/__init__.py

import pickle
import statistics
from datetime import timedelta
import pandas as pd

class GithubStats(object):
    def __init__(self):
        self.filename = None
        self.filenames = []
        self.issues = []
        self.data = None
        self.stats = None

        # 2015-03-23T05:24:02
        self.dformat = '%Y-%m-%dT%H:%M:%S'

    def load_pickles(self, filenames):
        self.filenames = filenames
        for fn in self.filenames:
            pdata = None
            print "Loading pickle file %s ..." % fn
            try:
                with open(fn, 'rb') as f:
                    pdata = pickle.load(f)
                self.issues.append(pdata)  
            except Exception as e:
                # EmptyIssue isn't going to be known to pickle ...
                print e

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

        print "----------------------------------"
        print " Processing pickle data" 
        print "----------------------------------"

        # http://stackoverflow.com/a/18677517

        pr_close_dates = []
        pr_close_ages = []

        pr_self_close_dates = []
        pr_self_close_ages = []

        pr_admin_close_dates = []
        pr_admin_close_ages = []

        pr_merged_dates = []
        pr_merged_ages = []

        pr_opened_dates = []
        pr_opened_count = []

        issue_close_dates = []
        issue_close_ages = []

        issue_self_close_dates = []
        issue_self_close_ages = []

        issue_admin_close_dates = []
        issue_admin_close_ages = []

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
                    if not x.pr.merged_at:
                        # Who closed it? Creator or Repo owner?
                        if x.raw_data['closed_by']['id'] == x.raw_data['user']['id']:
                            pr_self_close_dates.append(timestamp)
                            pr_self_close_ages.append(age)
                        else:
                            pr_admin_close_dates.append(timestamp)
                            pr_admin_close_ages.append(age)
                    else:    
                        pr_merged_dates.append(timestamp)
                        pr_merged_ages.append(age)
                        #import epdb; epdb.st()

                else:
                    issue_close_dates.append(timestamp)
                    issue_close_ages.append(age)

                    if not x.raw_data['closed_by']:
                        x.raw_data['closed_by'] = {}

                    if not 'id' in x.raw_data['closed_by']:
                        x.raw_data['closed_by']['id'] = x.raw_data['user']['id']

                    try:
                        x.raw_data['closed_by']['id']
                        x.raw_data['user']['id']
                    except:
                        import epdb; epdb.st()

                    if x.raw_data['closed_by']['id'] == x.raw_data['user']['id']:
                        issue_self_close_dates.append(timestamp)
                        issue_self_close_ages.append(age)
                    else:
                        issue_admin_close_dates.append(timestamp)
                        issue_admin_close_ages.append(age)

        self.data = {
            'pr_close_dates'        : pr_close_dates,
            'pr_close_ages'         : pr_close_ages,
            'pr_self_close_dates'   : pr_self_close_dates,
            'pr_self_close_ages'    : pr_self_close_ages,
            'pr_admin_close_dates'  : pr_admin_close_dates,
            'pr_admin_close_ages'   : pr_admin_close_ages,
            'pr_merged_dates'       : pr_merged_dates,
            'pr_merged_ages'        : pr_merged_ages,
            'pr_opened_dates'       : pr_opened_dates,
            'pr_opened_count'       : pr_opened_count,
            'issue_close_dates'     : issue_close_dates,
            'issue_close_ages'      : issue_close_ages,
            'issue_opened_dates'    : issue_opened_dates,
            'issue_opened_count'    : issue_opened_count
            }

        print "Done."
        return self.process_stats(data=self.data)


    def _summarize_ages(self, dates, ages, sample='M'):

        ddict = {'date': dates, 'age': ages}
        main_df = pd.DataFrame(ddict, columns=['date', 'age'])
        main_df['date'] = pd.to_datetime(main_df['date'], format=self.dformat)
        main_df = main_df.set_index('date')

        # calculate total closures
        totals = main_df.resample(sample).count()
        totals.columns = ['total']
        totals.fillna(0)

        # calculate medians
        medians = main_df.resample(sample).median()
        medians.columns = ['median_age_days']

        # calculate means
        means = main_df.resample(sample).mean()
        means.columns = ['mean_age_days']

        #return {'main': main_df, 'totals': totals, 'medians': medians,'means': means}
        columns = [totals, medians, means]
        result = pd.concat(columns, axis=1)
        return result

    
    def _summarize_counts(self, dates, counts, sample='M'):

        ddict = {'date': dates, 'i': counts}
        main_df = pd.DataFrame(ddict, columns=['date', 'i'])
        main_df['date'] = pd.to_datetime(main_df['date'], format=self.dformat)
        main_df = main_df.set_index('date')
        totals = main_df.resample('M').count()
        totals.columns = ['total']
        totals.fillna(0)
        #return {'main': main_df, 'totals': totals}
        return totals


    def process_stats(self, data=None):

        print "----------------------------------"
        print " Building statistics "
        print "----------------------------------"

        # easier for unit testing ...
        if not data:
            data = self.data

        #############################################
        # PR closures ...
        #############################################

        print "PR closures ..."
        pr_close = self._summarize_ages(data['pr_close_dates'], 
                                data['pr_close_ages'], sample='M')
        pr_close.columns = ['pr_total_closed', 'pr_close_median_age_days', 'pr_close_mean_age_days']

        #############################################
        # PR merges ...
        #############################################

        print "PR merges ..."
        pr_merge = self._summarize_ages(data['pr_merged_dates'], 
                                data['pr_merged_ages'], sample='M')
        pr_merge.columns = ['pr_total_merged', 'pr_merge_median_age_days', 'pr_merge_mean_age_days']

        #############################################
        # PR openings ...
        #############################################

        print "PR openings ..."
        # totals columns: [pr_total_opened]
        pr_open = self._summarize_counts(data['pr_opened_dates'], 
                                data['pr_opened_count'], sample='M')
        pr_open.columns = ['pr_total_opened']

        #############################################
        # Issue closures ...
        #############################################

        print "Issue closures ..."
        i_close = self._summarize_ages(data['issue_close_dates'], 
                                data['issue_close_ages'], sample='M')
        i_close.columns = ['issue_total_closed', 'issue_close_median_age_days', 'issue_close_mean_age_days']

        #############################################
        # Issue openings ...
        #############################################

        print "Issue openings ..."
        i_open = self._summarize_counts(data['issue_opened_dates'], 
                                data['issue_opened_count'], sample='M')
        i_open.columns = ['issue_total_opened']

        #############################################
        # Aggregate result ...
        #############################################

        columns = [pr_open, 
                   pr_close,
                   pr_merge,
                   i_open,
                   i_close]
        result = pd.concat(columns, axis=1)
        #import epdb; epdb.st()

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

        # Add the totals columns
        for repoid,reponame in enumerate(self.reponames):
            if repoid == 0:
                xdf = self.dataframes[repoid].copy()
            else:
                xdf = xdf.add(self.dataframes[repoid], fill_value=0)        

        # Remove non-totals columns (median/mean/etc)
        columns = xdf.columns
        columns = [x for x in columns if not 'total' in x]
        for col in columns:
            del xdf[col]

        # Add all columns from dataframes with repo suffix
        for repoid,reponame in enumerate(self.reponames):
            cols = self.dataframes[repoid].columns
            for col in cols:
                repocol = col + '__' + reponame
                xdf[repocol] = self.dataframes[repoid][col]

        #import epdb; epdb.st()
        self.stats = xdf
        return xdf
