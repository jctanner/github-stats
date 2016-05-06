#!/opt/anaconda2/bin/python

import os
from GithubStats.githubstats import GithubStats
from GithubStats.githubstats import GithubStatsAggregator
from pprint import pprint

import pandas as pd

def main():

    #fns = ['/home/jtanner/workspace/.triage/imsweb_ezmomi.pickle']

    cachedir = os.path.expanduser('~/.triage')
    fns = [('ansible_ansible.pickle', 'results/ansible-ansible.csv'),
           ('ansible_ansible-modules-core.pickle', 'results/ansible-modules-core.csv'),
           ('ansible_ansible-modules-extras.pickle', 'results/ansible-modules-extras.csv')]

    reponames = []
    dataframes = []

    ############################################
    # Get stats for each individual repo
    ############################################
    for fn in fns:
        fname = os.path.join(cachedir, fn[0])
        if not os.path.isfile(fname):
            continue

        repo_name = os.path.basename(fn[0]).replace('.pickle', '')
        reponames.append(repo_name)

        ghs = GithubStats()
        ghs.load_pickle(fname)
        df = ghs.process_data()
        dataframes.append(df)
        print df.tail(5)
        df.to_csv(fn[1])

    ############################################
    # Aggregate all data
    ############################################

    gha = GithubStatsAggregator(dataframes, reponames)
    xdf = gha.combine()
    xdf.to_csv('results/ansible_all_repos.csv')
    #import epdb; epdb.st()

if __name__ == "__main__":
    main()
