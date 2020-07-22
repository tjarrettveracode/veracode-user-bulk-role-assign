# Veracode User Bulk Role Assign

Uses the Veracode Identity API to add roles to users. Currently allows easy assignment of the Security Labs User role.

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
* --userid, -u : specify a GUID for an individual user to set the role (optional)

## NOTE

1. To be able to use all the endpoints of the Identity REST APIs, you must have either (a) an API service account with the Admin API role, or (b) auser account with the Administrator role, as described in the [Veracode Help Center](https://help.veracode.com/go/c_identity_intro)
2. You cannot assign the Security Lead role to an API user. The script is smart enough to skip these users.
3. The Veracode Platform expects a user with the Security Lead role to either be assigned to a team or to have another role that grants them privileges across teams (e.g. Security Lead). Currently the script will fail to assign the role, with a warning, to a user that does not meet these criteria.
