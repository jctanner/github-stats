#!/opt/anaconda/bin/python

import unittest2 as unittest
import sys
sys.path.append('../..')
from GithubStats.githubstats import GithubStats

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

TESTDATA1 = { 
    'pr_close_dates'        : ['2016-04-28T18:20:27', '2016-04-29T05:07:09', '2016-05-01T09:02:57'],
    'pr_close_ages'         : [1,2,1],
    'pr_merged_dates'       : [],
    'pr_merged_count'       : [],
    'pr_opened_dates'       : ['2016-04-28T18:20:27', '2016-04-29T05:07:09', '2016-05-01T09:02:57'],
    'pr_opened_count'       : [1,1,1],
    'issue_close_dates'     : ['2016-03-28T18:20:27', '2016-04-29T05:07:09', '2016-05-01T09:02:57'],
    'issue_close_ages'      : [1,2,3],
    'issue_opened_dates'    : ['2016-01-28T18:20:27', '2016-03-01T09:02:57'],
    'issue_opened_count'    : [0,0]
}

class TestStats(unittest.TestCase):

    ghs = None
    stats = None

    def setUp(self):
        self.ghs = GithubStats()
        self.stats = self.ghs.process_stats(data=TESTDATA1)

    #def test_total_count(self):
    #    assert True

    def test_total_pr_count(self):
        assert self.stats['pr_total_opened'][0] == 0.0
        assert self.stats['pr_total_opened'][1] == 2.0
        assert self.stats['pr_total_opened'][2] == 1.0

        assert self.stats['pr_total_closed'][0] == 0.0
        assert self.stats['pr_total_closed'][1] == 2.0
        assert self.stats['pr_total_closed'][2] == 1.0

    def test_total_issue_count(self):
        assert self.stats['issue_total_opened'][0] == 0.0
        assert self.stats['issue_total_opened'][1] == 2.0
        assert self.stats['issue_total_opened'][2] == 1.0

        assert self.stats['issue_total_closed'][0] == 1.0
        assert self.stats['issue_total_closed'][1] == 1.0
        assert self.stats['issue_total_closed'][2] == 1.0


    def test_combined_totals(self):
        assert self.stats['opened_total'][0] == 0.0
        assert self.stats['opened_total'][1] == 4.0
        assert self.stats['opened_total'][2] == 2.0

        assert self.stats['closed_total'][0] == 1.0
        assert self.stats['closed_total'][1] == 3.0
        assert self.stats['closed_total'][2] == 2.0


