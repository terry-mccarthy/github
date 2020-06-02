from github import Github
import configparser

# Expecting a github.ini file with
# [DEFUALT]
# Token=<your github access token>
config = configparser.ConfigParser()
config.read('github.ini')

g = Github(config['DEFAULT']['Token'])

from pprint import pprint
def search_code(keywords):
  """
  Seach all Voda repos
  https://developer.github.com/v3/search/#search-code
  """

  # keyword is added to see if this is a repo imported into other projects
  myquery = 'git@github.com:VodafoneAustralia/' + '+'.join(keywords) + '+org:VodafoneAustralia'
  
  result = g.search_code(query=myquery)

  if result.totalCount:
    print(f'Looking for: {myquery}')
    for f in result:
      print(f.repository.html_url + f'/{f.path}')
  else:
    myquery = 'github.com/VodafoneAustralia/' + '+'.join(keywords) + '+org:VodafoneAustralia'
    print(f'Looking for: {myquery}')
    for f in result:
      print(f.repository.html_url + f'/{f.path}')

if __name__ == '__main__':
  keywords = input('Enter keyword(s)[e.g python, flask, postgres]: ')
  keywords = [keyword.strip() for keyword in keywords.split(',')]
  search_code(keywords)