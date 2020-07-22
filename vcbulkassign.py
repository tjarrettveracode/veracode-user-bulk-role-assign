import sys
import requests
import argparse
import logging
import json
from veracode_api_signing.plugin_requests import RequestsAuthPluginVeracodeHMAC

from helpers import api

def updateUser(userinfo):
    userguid = userinfo["user_id"]

    # API users don't have Security Labs access, and don't try to assign to users who already have the role
    if checkForAPIUser(userinfo):
        print("Skipping API user",userguid)
        return 0
    if checkForRole(userinfo, "securityLabsUser"):
        print("Skipping user",userguid,"as role is already present")
        return 0

    ignoreteamrestrictions = 0

    if checkForTeams(userinfo) == 0:
        #check to see if we have an Ignores Team Restrictions bit
        if checkForRole(userinfo, "extseclead") == None:
            ignoreteamrestrictions = 1
        elif checkForRole(userinfo, "extexecutive") == None:
            ignoreteamrestrictions = 1
        elif checkForRole(userinfo, "extadmin") == None:
            ignoreteamrestrictions = 1

        if ignoreteamrestrictions == 0:
            print("Cannot assign role to user",userguid,"as user has no assigned teams")
            return 0

    roles = constructUserRoles(userinfo,"securityLabsUser")
    updateduser = api.VeracodeAPI().update_user(userguid,roles)
    print("Updated user",userguid)

    return 1

def constructUserRoles(userdata, roleToAdd):
    roles = userdata["roles"]
    newroles = []
    for role in roles:
        newroles.append({"role_name": role.get("role_name")})
    newroles.append({"role_name": roleToAdd}) #add roleToAdd to roles

    rolesObject = json.dumps({"roles": newroles})
    return rolesObject

def checkForRole(userdata, roleToCheck):
    roles = userdata["roles"]
    return any(item for item in roles if item["role_name"] == roleToCheck)

def checkForAPIUser(userdata):
    permissions = userdata.get("permissions")
    apiuser = any(item for item in permissions if item["permission_name"]=="apiUser")
    return apiuser

def checkForTeams(userdata):
    teams = userdata.get("teams")
    if teams == None:
        return 0
    return len(teams) 


def main():
    parser = argparse.ArgumentParser(
        description='This script adds the Security Labs User role for existing users. It can operate on one user '
                    'or all users in the account.')
    parser.add_argument('-u', '--user_id', required=False, help='User ID (GUID) to update. Ignored if --all is specified.')
    parser.add_argument('-l', '--all', required=False, help='Set to TRUE to update all users.', default=False)
    args = parser.parse_args()

    target_user = args.user_id
    all_users = args.all 

    logging.basicConfig(filename='vcbulkassign.log',
                        format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S%p',
                        level=logging.INFO)

    count=0

    if all_users == "true":
        data = api.VeracodeAPI().get_users()
        print("Reviewing",len(data),"total users...")
        for user in data:
            userguid = user["user_id"]
            # skip deleted users
            if user["deleted"] == "true":
                print("Skipping deleted user",userguid)
                return 0

            data2 = api.VeracodeAPI().get_user(userguid)

            count += updateUser(data2)
            next
    elif target_user is None:
        print("You must specify a --user_id (guid) if --all is not specified.")
        exit
    else:
        user = api.VeracodeAPI().get_user(target_user)
        count += updateUser(user)

    print("Added role to",count,"users")

if __name__ == '__main__':
    main()