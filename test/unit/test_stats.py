#!/opt/anaconda/bin/python

import unittest2 as unittest
import sys
sys.path.append('../..')
from GithubStats.githubstats import GithubStats
from GithubStats.githubstats import GithubStatsAggregator

# Timestamp examples ...
"""
 '2016-04-26T13:47:23',
 '2016-04-27T11:32:43',
 '2016-04-27T15:31:04',
 '2016-04-27T14:52:25',
 '2016-04-28T18:20:27',
 '2016-04-29T05:07:09',
 '2016-05-02T00:34:43',
 '2016-05-01T09:02:57',
 '2016-05-02T13:38:29',
 '2016-05-04T17:17:10',
"""

# Fake data example ...
TESTDATA1 = { 
    'pr_close_dates'        : ['2016-04-28T18:20:27', '2016-04-29T05:07:09', '2016-05-01T09:02:57'],
    'pr_close_ages'         : [1,2,1],
    'pr_merged_dates'       : [],
    'pr_merged_ages'        : [],
    'pr_opened_dates'       : ['2016-04-28T18:20:27', '2016-04-29T05:07:09', '2016-05-01T09:02:57'],
    'pr_opened_count'       : [1,1,1],
    'issue_close_dates'     : ['2016-03-28T18:20:27', '2016-04-29T05:07:09', '2016-05-01T09:02:57'],
    'issue_close_ages'      : [1,2,3],
    'issue_opened_dates'    : ['2016-01-28T18:20:27', '2016-03-01T09:02:57'],
    'issue_opened_count'    : [0,0]
}

# 0 prs opened in jan
# 2 prs opened in april
# 1 pr opened in april
# 0 prs closed in jan
# 2 prs closed in april
# 1 pr closed in april


# Fake data example 2 ...
TESTDATA2 = { 
    'pr_close_dates'        : ['2015-04-28T18:20:27', '2015-04-29T05:07:09', '2015-05-01T09:02:57'],
    'pr_close_ages'         : [1,2,1],
    'pr_merged_dates'       : [],
    'pr_merged_ages'        : [],
    'pr_opened_dates'       : ['2015-04-28T18:20:27', '2015-04-29T05:07:09', '2015-05-01T09:02:57'],
    'pr_opened_count'       : [1,1,1],
    'issue_close_dates'     : ['2015-03-28T18:20:27', '2015-04-29T05:07:09', '2015-05-01T09:02:57'],
    'issue_close_ages'      : [1,2,3],
    'issue_opened_dates'    : ['2015-01-28T18:20:27', '2015-03-01T09:02:57', '2016-05-01T09:02:59', 
                               '2016-05-01T09:15:57'],
    'issue_opened_count'    : [0,0,0,0]
}


# Expected aggregates ...

# MONTH    issues_opened issues_closed pr_opened pr_closed
# 2015-01  1                                      
# 2015-02
# 2015-03  1             1
# 2015-04                1             2         2
# 2015-05                1             1         1
# 2016-01  1
# 2016-02
# 2016-03  1             1
# 2016-04                1             2         2
# 2016-05  2             1             1         1
# ----------------------------------------------------------
# TOTAL    6             6             6         6 


class TestStats(unittest.TestCase):

    ghs1 = None
    stats1 = None

    ghs2 = None
    stats2 = None

    gha = None
    gha_stats = None

    def setUp(self):

        # analyze example 1
        self.ghs1 = GithubStats()
        self.stats1 = self.ghs1.process_stats(data=TESTDATA1)

        # analyze example 2
        self.ghs2 = GithubStats()
        self.stats2 = self.ghs2.process_stats(data=TESTDATA2)
   

    def test_total_pr_count(self):
        #import epdb; epdb.st()
        assert self.stats1['pr_total_opened'].sum() == 3.0
        assert self.stats1['pr_total_opened'].count() == 5
        assert self.stats1['pr_total_closed'].sum() == 3.0
        assert self.stats1['pr_total_closed'].count() == 5

    def test_total_issue_count(self):
        assert self.stats1['issue_total_opened'].sum() == 2.0
        assert self.stats1['issue_total_opened'].count() == 5
        assert self.stats1['issue_total_closed'].sum() == 3.0
        assert self.stats1['issue_total_closed'].count() == 5

    def test_aggregator(self):

        # combine stats
        self.gha = GithubStatsAggregator([self.stats1, self.stats2], ['repoA', 'repoB'])
        self.gha_stats = self.gha.combine()
        #import epdb; epdb.st()

        assert self.gha_stats['issue_total_opened'].count() == 17
        assert self.gha_stats['issue_total_opened'].sum() == \
            len(TESTDATA1['issue_opened_dates'] + TESTDATA2['issue_opened_dates'])

        assert self.gha_stats['pr_total_opened'].count() == 17
        assert self.gha_stats['pr_total_opened'].sum() == \
            len(TESTDATA1['pr_opened_dates'] + TESTDATA2['pr_opened_dates'])


