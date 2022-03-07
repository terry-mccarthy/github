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

# repo_query =  """
# query {
#   user(login: "terry-mccarthy") {
#     name
#     contributionsCollection {
#       contributionCalendar {
#         totalContributions
#         weeks {
#         contributionDays {
#           color
#           contributionCount
#           date
#           weekday
#         }
#         firstDay
#         }
#       }
#     }
#   }
# }
# """
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



## A simple function to use requests.post to make the API call. Note the json= section.
def run_query(query, vars):
  json_input = {'query': query, 'variables': vars}
  request = requests.post('https://api.github.com/graphql', json=json_input, headers=headers)
  if request.status_code == 200:
    return request.json()
  else:
    raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))


#user_vars = query_variables.format(org=org,after='null')


def scan(cursor = 'null'):

    if cursor != 'null':
      cursor = '"' + cursor + '"'

    user_vars = query_variables.format(org=org,after=cursor)

    result = run_query(repo_query, user_vars)

    for user in result['data']['organization']['membersWithRole']['edges']:
      email = user['node']['organizationVerifiedDomainEmails'][0] \
        if len(user['node']['organizationVerifiedDomainEmails']) else "NA"
      print("login: {login}, name: {name}, email: {email}"
        .format(login=user['node']['login'], name=user['node']['name'], email=email))

    # loop to next page if required
    pageInfo = result['data']['organization']['membersWithRole']['pageInfo']
    if pageInfo['hasNextPage']:
      scan(pageInfo['endCursor'])


#scan()

def get_contributions(user):
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

query_variables = """{{
  "org": "{org}",
  "count": 100,
  "after": {after}
}}"""


def scan(cursor = 'null'):

    if cursor != 'null':
      cursor = '"' + cursor + '"'

    user_vars = query_variables.format(org=org,after=cursor)

    result = run_query(user_query, user_vars)
    #print(result)

    for user in result['data']['organization']['membersWithRole']['edges']:
      login=user['node']['login']
      get_contributions(login)

    # loop to next page if required
    pageInfo = result['data']['organization']['membersWithRole']['pageInfo']
    if pageInfo['hasNextPage']:
      scan(pageInfo['endCursor'])


scan()
