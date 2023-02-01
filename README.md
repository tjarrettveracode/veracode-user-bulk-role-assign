# Veracode User Bulk Role Assign

Uses the Veracode Identity API to add roles to users. Currently allows easy assignment of the Security Labs User, Greenlight IDE User, or eLearning roles.

## Setup

Clone this repository:

    git clone https://github.com/tjarrettveracode/veracode-user-bulk-role-assign

Install dependencies:

    cd veracode-user-bulk-role-assign
    pip install -r requirements.txt

(Optional) Save Veracode API credentials in `~/.veracode/credentials`

    [default]
    veracode_api_key_id = <YOUR_API_KEY_ID>
    veracode_api_key_secret = <YOUR_API_KEY_SECRET>

## Run

If you have saved credentials as above you can run:

    python vcbulkassign.py (arguments)

Otherwise you will need to set environment variables before running `example.py`:

    export VERACODE_API_KEY_ID=<YOUR_API_KEY_ID>
    export VERACODE_API_KEY_SECRET=<YOUR_API_KEY_SECRET>
    python vcbulkassign.py (arguments)

Arguments supported include:

* --all, -l : assigns the role to all users when this is set to TRUE
* --user_id, -u : specify a GUID for an individual user to set the role (optional)
* --role, -r: specify which role to assign, one of SECLAB (Security Labs User, default), IDESCAN (Greenlight IDE User), ELEARN (eLearning) (optional)

## NOTE

1. You should only assign the Security Labs role to the number of users for whom you have purchased seats.
2. To be able to use all the endpoints of the Identity REST APIs, you must have either (a) an API service account with the Admin API role, or (b) a user account with the Administrator role, as described in the [Veracode Docs Center](https://docs.veracode.com/r/c_identity_intro)
3. You cannot assign the Security Labs role to an API user. The script is smart enough to skip these users.
4. The Veracode Platform expects a user with the Security Labs role to either be assigned to a team or to have another role that grants them privileges across teams (e.g. Security Lead). Currently the script will fail to assign the role, with a warning, to a user that does not meet these criteria.
