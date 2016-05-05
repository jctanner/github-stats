#!/opt/anaconda2/bin/python

from GithubStats.githubstats import GithubStats
from pprint import pprint

def main():

    fns = ['/home/jtanner/workspace/.triage/ansible_ansible-modules-core.pickle']
    #fns = ['/home/jtanner/workspace/.triage/imsweb_ezmomi.pickle']
    ghs = GithubStats()
    ghs.load_pickle(fns[0])
    ghs.process_data()
    
    pprint(ghs.stats)

if __name__ == "__main__":
    main()
