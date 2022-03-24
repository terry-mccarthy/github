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

## A simple function to use requests.post to make the API call. Note the json= section.
def run_query(query, vars):
  json_input = {'query': query, 'variables': vars}
  request = requests.post('https://api.github.com/graphql', json=json_input, headers=headers)
  if request.status_code == 200:
    return request.json()
  else:
    raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))


def with_pagination(func):
  def wrapper(*args, **kwargs):
    hasNext, cursor = func('null')
    while hasNext:
      cursor = '"' + cursor + '"'
      hasNext, cursor = func(cursor)
  return wrapper


contribution_query =  """
query($username:String!) {
  user(login: $username) {
    name
    login
    contributionsCollection {
      contributionCalendar {
        totalContributions
      }
    }
  }
}
"""

def get_zero_contributions(user):
  contribution_variables = """{{
    "username": "{username}"
  }}"""

  contribution_vars = contribution_variables.format(username=user)
  result = run_query(contribution_query, contribution_vars)
  if (result['data']['user']['contributionsCollection']['contributionCalendar']['totalContributions'] == 0):
    #print(result)
    print("{name}, {login}".format(name=result['data']['user']['name'], login=result['data']['user']['login']))

###########

user_query =  """
query ($count:Int! $org:String! $after:String) {
  organization(login: $org) {
    membersWithRole(first: $count after: $after ) {
      totalCount
      edges {
        node {
          login 
          name
          ... on User {
            organizationVerifiedDomainEmails(login: $org)
          }

        }
      }
      pageInfo {
        endCursor
        hasNextPage
      }
    }
  }
}
"""

@with_pagination
def show_contributions(cursor = 'null'):
  query_variables = """{{
    "org": "{org}",
    "count": 100,
    "after": {after}
  }}"""
  user_vars = query_variables.format(org=org,after=cursor)
  result = run_query(user_query, user_vars)

  for user in result['data']['organization']['membersWithRole']['edges']:
    login=user['node']['login']
    get_zero_contributions(login)

  pageInfo = result['data']['organization']['membersWithRole']['pageInfo']
  return pageInfo['hasNextPage'], pageInfo['endCursor']


show_contributions()
