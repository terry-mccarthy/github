"""
  List all GitHub Users and their organisation verified domain emails
  - https://docs.github.com/en/graphql/reference/objects?query=#user

"""
import requests
import json
import configparser

from pprint import pprint

# Expecting a github.ini file with
# [DEFUALT]
# Token=<your github access token>
config = configparser.ConfigParser()
config.read('github.ini')
token = config['DEFAULT']['Token']
org = config['DEFAULT']['Organisation']

headers = {"Authorization": "Bearer " + token}

release_query =  """
query ($owner:String! $repo:String!){
  repository(owner: $owner, name: $repo) {
    latestRelease { 
      name
      publishedAt 
    }
  }
}
"""

query_variables = """{{
  "owner": "{owner}",
  "repo": "{repo}"
}}"""

## A simple function to use requests.post to make the API call. Note the json= section.
def run_query(query, query_vars):
  json_input = {'query': query, 'variables': query_vars}
  pprint(json_input)
  request = requests.post('https://api.github.com/graphql', json=json_input, headers=headers)
  if request.status_code == 200:
    return request.json()
  else:
    raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))


#user_vars = query_variables.format(org=org,after='null')


def scan(cursor = 'null'):

    if cursor != 'null':
      cursor = '"' + cursor + '"'

    user_vars = query_variables.format(repo='runner',owner='actions')
    #pprint(user_vars)

    result = run_query(release_query, user_vars)
    pprint(result)


scan()
