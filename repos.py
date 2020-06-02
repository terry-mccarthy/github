from github import Github
import configparser
import sys
import re
import datetime

# Expecting a github.ini file with
# [DEFUALT]
# Token=<your github access token>
config = configparser.ConfigParser()
config.read('github.ini')

g = Github(config['DEFAULT']['Token'])

from pprint import pprint
def get_repos():
  """
  Seach all Voda repos
  https://developer.github.com/v3/search/users
  https://pygithub.readthedocs.io/en/latest/github.html?highlight=users#github.MainClass.Github.get_user
  https://pygithub.readthedocs.io/en/latest/github_objects/NamedUser.html?highlight=nameduser#github.NamedUser.NamedUser
  """

  # keyword is added to see if this is a repo imported into other projects
  #myquery = 'git@github.com:VodafoneAustralia/' + '+'.join(keywords) + '+org:VodafoneAustralia'
  
  #def since
  vha_org = g.get_organization("VodafoneAustralia")
  repos = vha_org.get_repos()
  name = ''
  for r in repos:
    #pprint(vars(r._name.value))
    name = r._name.value
    print(name)
    if (name == 'Shop') :
      #h = r.get_hooks()
      #print("Name: {} - count: {}".format(name, h[0]))
      n = r.get_notifications(since=datetime.datetime(2020, 1, 1, 23, 37, 16, 361995))
      pprint(vars(r))
      #pprint(vars(h[0]._active))
      return
    # found = user is None or re.search(user, m.login)
    # if found: 
    #   print(f'{m}  {m.created_at}')

if __name__ == '__main__':
  user = sys.argv[1] if len(sys.argv) > 1 else None
  get_repos()