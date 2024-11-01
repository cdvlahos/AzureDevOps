#!/usr/bin/env python

import argparse
import Modules.repos as repoTools
import Modules.project as projectTools
import Modules.hooks as hookTools
import Modules.user_management as userTools
import Modules.processes as processTools

# Setup Parser
parser = argparse.ArgumentParser(prog='ado')
subparsers = parser.add_subparsers(dest='command')

# Project Subparser
project_parser = subparsers.add_parser('project', help='Project commands')
project_subparsers = project_parser.add_subparsers(dest='subcommand')

list_parser = project_subparsers.add_parser('list', help='List projects')

create_parser = project_subparsers.add_parser('create', help='Create project')
create_parser.add_argument('project', help='Name of project')
create_parser.add_argument('-d', '--description', help='Description of project', default='')
create_parser.add_argument('-p', '--process', help='Process name of project', default='PROCESS_NAME')
create_parser.add_argument('--noHook', action='store_true', help='No hooks for project', default=False)
create_parser.add_argument('--externalHardware', help='List of External Teams, EX KTC, Flex...', default="")

delete_parser = project_subparsers.add_parser('delete', help='Delete project')
delete_parser.add_argument('name', help='Name of project')

update_parser = project_subparsers.add_parser('update', help='Update project')
update_parser.add_argument('project', help='Name of project')
update_parser.add_argument('-d', '--description', help='Description of project', default='')
update_parser.add_argument('-p', '--process', help='Process name of project', default='')
update_parser.add_argument('--crn', action='store_true', help='Update CRN hooks', default=False)

# Repo Subparser
repo_parser = subparsers.add_parser('repo', help='Repo commands')
repo_subparsers = repo_parser.add_subparsers(dest='subcommand')

list_parser = repo_subparsers.add_parser('list', help='List repos')
list_parser.add_argument('project', help='Name of project')

get_parser = repo_subparsers.add_parser('get', help='Get repo')
get_parser.add_argument('project', help='Name of project')
get_parser.add_argument('repo', help='Name of repo')

delete_repo_parser = repo_subparsers.add_parser('delete', help='Delete repository')
delete_repo_parser.add_argument('project', help='Name of project')
delete_repo_parser.add_argument('repo', help='Name of repo')

create_repo_parser = repo_subparsers.add_parser('create', help="Create new Repo")
create_repo_parser.add_argument('project', help='Name of project')
create_repo_parser.add_argument('repo', help='Name of repo')

list_deleted_parser = repo_subparsers.add_parser('listDeleted', help='List repos in recycle bin')
list_deleted_parser.add_argument('project', help='Name of project')

restore_repo_parser = repo_subparsers.add_parser('restore', help='Restore deleted repository')
restore_repo_parser.add_argument('project', help='Name of project')
restore_repo_parser.add_argument('repo', help='Name of repo')


# Hooks Subparser
hooks_parser = subparsers.add_parser('hooks', help='Hooks commands')
hooks_subparsers = hooks_parser.add_subparsers(dest='subcommand')

list_hooks_parser = hooks_subparsers.add_parser('list', help='List hooks')
list_hooks_parser.add_argument('project', help='Name of project' )

create_all_parser = hooks_subparsers.add_parser('create_all', help='Create all hooks')

delete_old_parser = hooks_subparsers.add_parser('delete_old', help='Delete old hooks')

create_hooks_parser = hooks_subparsers.add_parser('create_git', help='Create hook')
create_hooks_parser.add_argument('project', help='Name of project')

takeown_parser = hooks_subparsers.add_parser('takeown', help='Take ownership of hooks')
takeown_parser.add_argument('owner', help='Email address of user to take ownership from')

create_crn_parser = hooks_subparsers.add_parser('create_crn', help='Create CRN hook')
create_crn_parser.add_argument('project', help='Name of project')

# User Subparser
user_parser = subparsers.add_parser('user', help='user commands')
user_subparsers = user_parser.add_subparsers(dest='subcommand')

find_user_parser = user_subparsers.add_parser('find_user', help='Search for a user from given email')
find_user_parser.add_argument('email', help='Users Email')

delete_user_parser = user_subparsers.add_parser('delete', help='Search for a user from given email')
delete_user_parser.add_argument('email', help='Users Email')

# Process Subparser
process_parser = subparsers.add_parser('process', help='Process commands')
process_subparsers = process_parser.add_subparsers(dest='subcommand')

update_process_parser = process_subparsers.add_parser('update', help='Update a given process')
update_process_parser.add_argument('-p', '--process', help='Name of Process', required=True)
update_process_parser.add_argument('-e', '--element', help='Name of element to update', required=True)
update_process_parser.add_argument('-l', '--list', help='List of elements to add', required=True)

find_process_parser = process_subparsers.add_parser('find', help='Find a given process')
find_process_parser.add_argument('-p', '--process', help='Name of Process', default=None)
find_process_parser.add_argument('-w', '--workItem', help='Name of work item type', default=None)


if __name__ == "__main__":
    # Ensure that the user specifies a valid command
    valid_commands = ['project', 'hooks', 'repo', 'user', 'process']
    args = parser.parse_args()
    if not args.command or args.command not in valid_commands:
        print("Please select a valid command")
        parser.print_help()
        exit(1)
    # Handle commands
    elif args.command == 'project':
        valid_subcommands = ['list', 'create', 'delete', 'update']
        if not args.subcommand or args.subcommand not in valid_subcommands:
            print("Please select a valid command for project")
            project_parser.print_help()
            exit(1)
        if args.subcommand == 'list':
            print('Listing projects')
            projectTools.list_project()
        elif args.subcommand == 'create':
            print(f'Creating project {args.project}')
            if args.description:
                print(f'Creating description {args.description}')
            elif args.process:
                print(f'Adding to process {args.process}')
            elif args.crn:
                print(f'Creating Hooks {args.crn}')

            # create the project
            subscriptions = hookTools.get_subscriptions()
            projectTools.create_project(args.project, subscriptions, desc=args.description, process=args.process, nohook=args.noHook)

            # If this is an external hardware project create teams
            if len(args.externalHardware) > 0:
                print(f'Creating External Hardware project teams')
                externalTeams = ""
                for externalTeam in args.externalHardware.split(","):
                    externalTeams = externalTeams + externalTeam + " "
                    # create the external users Team
                    projectTools.create_team(externalTeam + " External Team", args.project)

                # create the external team and Internal developers team
                projectTools.create_team(externalTeams + " and Internal Development", args.project)

                # create the external team and Internal operations team
                projectTools.create_team(externalTeams + " and Internal Operations", args.project)

        elif args.subcommand == 'delete':
            print(f'Deleting project {args.project}')
            projectTools.delete_project(args.project)
        elif args.subcommand == 'update':
            print(f'Updating project {args.project}')
            if args.description:
                print(f'Updating description {args.description}')
            elif args.process:
                print(f'Updating process name {args.process}')
            elif args.crn:
                print(f'Updating CRN {args.crn}')
            projectTools.update_project(args.project, args.description, args.process, args.crn)
    elif args.command == 'repo':
        valid_subcommands = ['list', 'get', 'create', 'delete', 'listDeleted', 'restore']
        if not args.subcommand or args.subcommand not in valid_subcommands:
            print("Please select a valid command for repo")
            repo_parser.print_help()
            exit(1)
        if args.subcommand == 'list':
            print(f'Listing repos for project {args.project}')
            repoTools.list_repositories(args.project)
        elif args.subcommand == 'get':
            print(f'Getting repo {args.repo} for project {args.project}')
            repoTools.get_repository(args.project, args.repo)
        elif args.subcommand == 'create':
            print(f'Create repo {args.repo} in project {args.project}')
            repoTools.create_repository(args.project, args.repo)
        elif args.subcommand == 'delete':
            print(f'Delete repo {args.repo} for project {args.project}')
            repoTools.delete_repository(args.project, args.repo)
        elif args.subcommand == 'listDelete':
            print(f'List all deleted repos in recycle bin for project {args.project}')
            repoTools.list_deleted(args.project)
        elif args.subcommand == 'restore':
            print(f'Restore repo {args.repo} for project {args.project} from recycle bin')
            repoTools.restore_deleted(args.project, args.repo)
    elif args.command == 'hooks':
        valid_subcommands = ['list', 'create_all', 'create_git', 'takeown', 'create_crn', 'delete_old']
        if not args.subcommand or args.subcommand not in valid_subcommands:
            print("Please select a valid command for hooks")
            hooks_parser.print_help()
            exit(1)
        if args.subcommand == 'list':
            print(f'Listing hooks for project {args.project}')
            hookTools.list_hooks(args.project)
        elif args.subcommand == 'create_all':
            subscriptions = hookTools.get_subscriptions()
            projects = projectTools.get_projects()
            for project in projects:
                hookTools.create_git(project, subscriptions)
        elif args.subcommand == 'create_git':
            subscriptions = hookTools.get_subscriptions()
            hookTools.create_git(args.project, subscriptions)
        elif args.subcommand == 'create_crn':
            hookTools.create_crn(args.project)
            print(f'Creating CRN hook for project {args.project}')
        elif args.subcommand == 'takeown':
            print(f'Taking ownership of hooks in all projects from {args.owner}')
            hookTools.takeown_hook(args.owner)
        elif args.subcommand == 'delete_old':
            print(f'Deleting old hooks')
            hookTools.delete_old_hooks()
    elif args.command == 'user':
        valid_subcommands = ['find_user', 'delete']
        if not args.subcommand or args.subcommand not in valid_subcommands:
            print("Please select a valid command for user")
            user_parser.print_help()
            exit(1)
        if args.subcommand == 'find_user':
            print(f'Searching for user {args.email}')
            userTools.find_user(args.email)
        elif args.subcommand == 'delete':
            print(f'Removing {args.email} from the organization if they exist')
            userTools.remove_user(args.email)
            hookTools.takeown_hook(args.email)
    elif args.command == 'process':
        valid_subcommands = ['update', 'find']
        if not args.subcommand or args.subcommand not in valid_subcommands:
            print("Please select a valid command for process")
            process_parser.print_help()
            exit(1)
        if args.subcommand == 'update':
            print(f'Updating process {args.process}')
            processTools.update_process(args.process, args.field, args.list)
        elif args.subcommand == 'find':
            if args.workItem:
                print(f'Finding Work item type details for {args.workItem} in process {args.process}')
                processTools.list_work_item_type_details(args.process, args.workItem)
            else:
                print(f'Finding process {args.process}')
                processTools.list_work_item_types(args.process)

