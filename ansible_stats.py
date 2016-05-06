#!/opt/anaconda2/bin/python

import os
from GithubStats.githubstats import GithubStats
from pprint import pprint

import pandas as pd

def main():

    #fns = ['/home/jtanner/workspace/.triage/imsweb_ezmomi.pickle']

    cachedir = os.path.expanduser('~/.triage')
    fns = [('ansible_ansible.pickle', 'results/ansible-ansible.csv'),
           ('ansible_ansible-modules-core.pickle', 'results/ansible-modules-core.csv'),
           ('ansible_ansible-modules-extras.pickle', 'results/ansible-modules-extras.csv')]

    xcolumns = []
    xreponames = []
    xdf = pd.DataFrame()

    ############################################
    # Get stats for each individual repo
    ############################################
    for fn in fns:
        fname = os.path.join(cachedir, fn[0])
        ghs = GithubStats()
        ghs.load_pickle(fname)
        df = ghs.process_data()
        print df.tail(5)
        df.to_csv(fn[1])

        repo_name = os.path.basename(fn[0]).replace('.pickle', '')
        xreponames.append(repo_name)
        for col in df.columns:
            if not col in xcolumns:
                xcolumns.append(col)
            newcol = col + '__' + repo_name
            xdf[newcol] = df[col]

    ############################################
    # Aggregate all data
    ############################################

    # add totals
    for col in xcolumns:
        cdf = pd.DataFrame(columns=[col])
        for repo_name in xreponames:
            rcol = col + '__' + repo_name
            # create index first
            if len(cdf[col]) == 0:
                cdf[col] = xdf[rcol].copy()
                #import epdb; epdb.st()
            else:
                cdf[col] = xdf[rcol] + cdf[col]

            #import epdb; epdb.st()
        xdf[col] = cdf[col]    
        #import epdb; epdb.st()

    xdf.to_csv('results/ansible_all_repos.csv')
    #import epdb; epdb.st()

if __name__ == "__main__":
    main()
