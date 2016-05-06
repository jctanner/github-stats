#!/opt/anaconda2/bin/python

import os
from GithubStats.githubstats import GithubStats
from pprint import pprint

def main():

    #fns = ['/home/jtanner/workspace/.triage/imsweb_ezmomi.pickle']

    cachedir = os.path.expanduser('~/.triage')
    fns = [('ansible_ansible.pickle', 'ansible-ansible.csv'),
           ('ansible_ansible-modules-core.pickle', 'ansible-modules-core.csv'),
           ('ansible_ansible-modules-extras.pickle', 'ansible-modules-extras.csv')]

    for fn in fns:
        fname = os.path.join(cachedir, fn[0])
        ghs = GithubStats()
        ghs.load_pickle(fname)
        df = ghs.process_data()
        print df.tail(5)
        df.to_csv(fn[1])

if __name__ == "__main__":
    main()
