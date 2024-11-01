#!/usr/bin/env python

# variables used in Modules
VCS_ROOT = 'https://{ORG_ID}.visualstudio.com/'
NEW_VCS_ROOT = 'https://dev.azure.com/{ORG_ID}/'
PROCESS_URL = NEW_VCS_ROOT + '_apis/work/processes%s'
REPOSITORY_URL = NEW_VCS_ROOT + '%s/_apis/git/repositories/'
PROJECT_REPOSITORY_URL = VCS_ROOT + \
    'DefaultCollection/%s/_apis/git/repositories/%s?api-version=7.1-preview.1'
PROJECT_REPOSITORIES_URL = VCS_ROOT + \
    'DefaultCollection/%s/_apis/git/repositories?api-version=7.1-preview.1'
PROJECT_REPO_URL = VCS_ROOT + \
    'DefaultCollection/%s/_apis/git/%s/?api-version=7.1-preview.1'
HOOKS_URL = NEW_VCS_ROOT + '_apis/hooks/subscriptions/%s'
HOOK_URL = VCS_ROOT + 'DefaultCollection/_apis/hooks/subscriptions/'
PROJECT_URL = NEW_VCS_ROOT + '_apis/projects/'
API_VERSION = 'api-version=6.0'
ORGANIZATION = "{ORG_ID}"
USERNAME = ""