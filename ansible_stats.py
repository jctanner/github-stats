#!/opt/anaconda2/bin/python

import glob
import os
from GithubStats.githubstats import GithubStats
from GithubStats.githubstats import GithubStatsAggregator
from pprint import pprint

import pandas as pd

def main():

    #fns = ['/home/jtanner/workspace/.triage/imsweb_ezmomi.pickle']

    cachedir = os.path.expanduser('~/.triage')
    prefixes = []
    #prefixes.append(('ansible_ansible', 'results/ansible-ansible.csv'))
    prefixes.append(('ansible_ansible-modules-core', 'results/ansible-modules-core.csv'))
    #prefixes.append(('ansible_ansible-modules-extras', 'results/ansible-modules-extras.csv'))

    reponames = []
    dataframes = []

    ############################################
    # Get stats for each individual repo
    ############################################
    for prefix in prefixes:
        globstr = os.path.join(cachedir, prefix[0] + '__*.pickle')
        pickle_files = glob.glob(globstr)
        #import epdb; epdb.st()
        repo_name = os.path.basename(prefix[0])
        reponames.append(repo_name)

        ghs = GithubStats()
        ghs.load_pickles(pickle_files[0:100])
        df = ghs.process_data()
        dataframes.append(df)
        print df.tail(5)
        df.to_csv(prefix[1])

    '''
    ############################################
    # Aggregate all data
    ############################################

    gha = GithubStatsAggregator(dataframes, reponames)
    xdf = gha.combine()
    xdf.to_csv('results/ansible_all_repos.csv')
    #import epdb; epdb.st()
    '''

if __name__ == "__main__":
    main()
