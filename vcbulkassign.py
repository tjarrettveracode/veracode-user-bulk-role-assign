import sys
import requests
import argparse
import logging
import json
import datetime

import anticrlf
from veracode_api_py import VeracodeAPI as vapi

log = logging.getLogger(__name__)

def setup_logger():
    handler = logging.FileHandler('vcbulkassign.log', encoding='utf8')
    handler.setFormatter(anticrlf.LogFormatter('%(asctime)s - %(levelname)s - %(funcName)s - %(message)s'))
    logger = logging.getLogger(__name__)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

def creds_expire_days_warning():
    creds = vapi().get_creds()
    exp = datetime.datetime.strptime(creds['expiration_ts'], "%Y-%m-%dT%H:%M:%S.%f%z")
    delta = exp - datetime.datetime.now().astimezone() #we get a datetime with timezone...
    if (delta.days < 7):
        print('These API credentials expire {}'.format(creds['expiration_ts']))


def update_user(userinfo,role):
    userguid = userinfo["user_id"]

    # API users don't have Security Labs access, and don't try to assign to users who already have the role
    if check_for_api_user(userinfo):
        print("Skipping API user {}".format(userguid))
        return 0
    if check_for_role(userinfo, role):
        print("Skipping user {} as role is already present".format(userguid))
        return 0

    ignoreteamrestrictions = 0

    if check_for_teams(userinfo) == 0:
        #check to see if we have an Ignores Team Restrictions bit
        if ((check_for_role(userinfo, "extseclead") == None) 
            or (check_for_role(userinfo,"extexecutive") == None)
            or (check_for_role(userinfo,"extadmin") == None)):
            ignoreteamrestrictions = 1

        if ignoreteamrestrictions == 0:
            print("Cannot assign role to user {} as user has no assigned teams".format(userguid))
            return 0

    roles = construct_user_roles(userinfo,role)
    vapi().update_user(userguid,roles)
    print("Updated user {}".format(userguid))

    return 1

def construct_user_roles(userdata, role_to_add):
    roles = userdata["roles"]
    newroles = []
    for role in roles:
        newroles.append({"role_name": role.get("role_name")})
    newroles.append({"role_name": role_to_add}) #add roleToAdd to roles

    roles_object = json.dumps({"roles": newroles})
    newroles = json.loads(roles_object)
    return newroles

def check_for_role(userdata, role_to_check):
    roles = userdata["roles"]
    return any(item for item in roles if item["role_name"] == role_to_check)

def check_for_api_user(userdata):
    permissions = userdata.get("permissions")
    apiuser = any(item for item in permissions if item["permission_name"]=="apiUser")
    return apiuser

def check_for_teams(userdata):
    teams = userdata.get("teams")
    if teams == None:
        return 0
    return len(teams) 


def main():
    parser = argparse.ArgumentParser(
        description='This script adds the specified User role for existing users. It can operate on one user '
                    'or all users in the account.')
    parser.add_argument('-u', '--user_id', required=False, help='User ID (GUID) to update. Ignored if --all is specified.')
    parser.add_argument('-l', '--all', action='store_true', required=False, help='Set to TRUE to update all users.', default="true")
    parser.add_argument('-r', '--role', required=False, help='One of SECLAB (default), IDESCAN, ELEARN.', default='SECLAB')
    args = parser.parse_args()

    target_user = args.user_id
    all_users = args.all 
    role = args.role

    if args.role == 'SECLAB':
        role = 'securityLabsUser'
    elif args.role == 'IDESCAN':
        role = 'greenlightideuser'
    elif args.role == 'ELEARN':
        role = 'extelearn'
    else:
        print("Role {} is not supported. Role must be one of SECLAB, IDESCAN, ELEARN.".format(role))
        return 0

    # Check if we're updating only one user.
    if target_user is not None:
        if len(target_user)!=36:
            print("Please make sure User ID is a GUID.")
            return
        else:
            all_users = False

    # CHECK FOR CREDENTIALS EXPIRATION
    creds_expire_days_warning()

    count=0

    if all_users:
        data = vapi().get_users()
        print("Reviewing {} total users...".format(len(data)))
        for user in data:
            userguid = user["user_id"]
            # skip deleted users
            if "deleted" in user.keys() and user["deleted"] == "true":
                print("Skipping deleted user {}".userguid)
                return 0

            data2 = vapi().get_user(userguid)

            count += update_user(data2,role)
    elif target_user is None:
        print("You must specify a --user_id (guid) if --all is not specified.")
        return
    else:
        try:
            user = vapi().get_user(target_user)
        except Exception as e:
            print("Error trying to access that user. Please check the GUID and try again.")
            return
        count += update_user(user,role)

    print("Added role to {} users".format(count))

if __name__ == '__main__':
    setup_logger()
    main()