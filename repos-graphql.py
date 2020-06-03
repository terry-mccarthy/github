# An example to get the remaining rate limit using the Github GraphQL API.

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

headers = {"Authorization": "Bearer " + token}


## A simple function to use requests.post to make the API call. Note the json= section.
def run_query(query, variables):
    request = requests.post('https://api.github.com/graphql', json={'query': query, 'variables': variables}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))

        
# The GraphQL query (with a few aditional bits included) itself defined as a multi-line string.       
query1 = """
query($repo:String!){
    repository(owner:"VodafoneAustralia", name:$repo) {
        vulnerabilityAlerts(first:5) {
            edges {
                node {
                    vulnerableManifestFilename
                    securityAdvisory {
                        severity
                        summary
                    }
                }
            }
        }
    }
}
"""

repo_query =  """
query($number_of_repos:Int! $afterCursor:String) {
    search(query:"org:VodafoneAustralia" type:REPOSITORY first:$number_of_repos after:$afterCursor) {
        repositoryCount
        pageInfo {
            startCursor
            hasNextPage
            endCursor
        }
        edges {
            node {
                ... on Repository {
                nameWithOwner
                name
                }
            }
        }
    } 
}
"""

repo_variables = """
{{
   "number_of_repos": 10,
   "afterCursor": {cursor}
}}
"""

# repo_var = variables.format(cursor="null")
# repo_var = variables.format(cursor='"Y3Vyc29yOjEw"')
# print(repo_var)

def scanRepos(cursor = "null"):

    if cursor != "null":
        cursor = '"' + cursor + '"'
    repo_var = repo_variables.format(cursor=cursor)

    #pprint(repo_var)
    result = run_query(repo_query, repo_var) # Execute the query
    #repos = json.loads(result)
    #pprint(result)

    for e in result['data']['search']['edges'] :
        name = e['node']['name']
        getVulnerabilities(name)
    
    pageInfo = result['data']['search']['pageInfo']
    if (pageInfo['hasNextPage']) :
        scanRepos(pageInfo['endCursor'])

def getVulnerabilities(name):
    var_repo = """
    {{
       "repo": "{name}"
    }}
    """.format(name=name)

    #print(var_repo)
    #print(name)
    sec = run_query(query1, var_repo)
    #pprint(sec)
    alerts = sec['data']['repository']['vulnerabilityAlerts']['edges']
    for a in alerts :
        print("Repo {}: {}".format(name, a['node']['securityAdvisory']['summary']))

scanRepos()
