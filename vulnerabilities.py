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
org = config['DEFAULT']['Organisation']

headers = {"Authorization": "Bearer " + token}


## A simple function to use requests.post to make the API call. Note the json= section.
def run_query(query, variables):
    request = requests.post('https://api.github.com/graphql', json={'query': query, 'variables': variables}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))

        
repo_query =  """
query($number_of_repos:Int! $afterCursor:String $org:String!) {
    search(query:$org type:REPOSITORY first:$number_of_repos after:$afterCursor) {
        repositoryCount
        pageInfo {
            startCursor
            hasNextPage
            endCursor
        }
        edges {
            node {
                ... on Repository {
                    name
                    vulnerabilityAlerts(first:100) {
                        edges {
                            node {
                                vulnerableManifestFilename
                                vulnerableManifestPath
                                vulnerableRequirements
                                securityAdvisory {
                                    ghsaId
                                    severity
                                    summary
                                    description
                                }
                                securityVulnerability {
                                    package {
                                        name
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    } 
}
"""

repo_variables = """
{{
   "number_of_repos": 10,
   "afterCursor": {cursor},
   "org": "org:{org}"
}}
"""

  
##
# Execute the repo query that loops through all repos looking for vulnerabilities
# takes pagination
# Limitation - currently only looks for the first 6 vulnerabilities
#
def scanRepos(cursor = "null"):

    # setup the cursor for pagination
    if cursor != "null":
        cursor = '"' + cursor + '"'
    repo_var = repo_variables.format(cursor=cursor, org=org)

    # excute the query
    result = run_query(repo_query, repo_var)

    #pprint(result)
    # output the results
    for e in result['data']['search']['edges'] :
        name = e['node']['name']

        v = {}
        alerts = e['node']['vulnerabilityAlerts']['edges']
        
        for a in alerts:
            package = a['node']['securityVulnerability']['package']['name']
            ghsaId = a['node']['securityAdvisory']['ghsaId']
            severity = a['node']['securityAdvisory']['severity']
            warning = ":".join((severity, ghsaId))
            description = a['node']['securityAdvisory']['description']

            if package in v:
                v[package].append(warning)
            else:
                v[package]=[warning]
            #( {['node']['vulnerableManifestFilename']  a['node']['securityAdvisory']['ghsaId']})
            if severity == 'CRITICAL':
                print("{}: ({}) - {}|{}|{}".format(name, a['node']['vulnerableManifestFilename'], package, a['node']['securityAdvisory']['summary'], warning))
                #print(description)

        for p in v:
            print("{}: {} - {}".format(name, p, ",".join(v[p])))
    
    # recurse the next page
    pageInfo = result['data']['search']['pageInfo']
    if (pageInfo['hasNextPage']) :
        scanRepos(pageInfo['endCursor'])

scanRepos()
