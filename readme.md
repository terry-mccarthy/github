# Python Scripts to interact with GitHub

## Requirement
Need to have a github.ini file with contents
```
[DEFAULT]
Token=<your-secret-github-token>
Organisation=<org|user>
```

`pip install -r requirements.txt`

## Scripts
1. vulnerabilities.py - scans all organisation repos for the first 6 vulnerabilities.
1. users.p - lists all users and verified domain emails
1. prs.py - pull requests
1. releases.py - the lastest release of a repo
1. contributions - contributions from users