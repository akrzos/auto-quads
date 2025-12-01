# auto-quads

Self-scheduling QUADS CLI tool to create and manage a self-scheduled cloud

## Usage Workflow

### 1. Clone tool

```console
[user@fedora ~]$ git clone https://github.com/akrzos/auto-quads.git
Cloning into 'auto-quads'...
...
Resolving deltas: 100% (11/11), done.
[user@fedora ~]$ cd auto-quads/
[user@fedora auto-quads]$
```

### 2. Configure and Source Environment Variables

Copy `env.sample.sh` to `env.sh` and fill in variables:

```console
[user@fedora auto-quads]$ cp env.sample.sh env.sh
```

Edit `env.sh` with your QUADS server details:

Fill in
* `QUADS_SERVER` with your quads server
* `QUADS_USERNAME` with either a new or existing quads username (Must be an email address to receive email notifications)
* `QUADS_PASSWORD` with either a new or existing quads password
* `QUADS_OWNER` will automatically be determined to the username portion of your email address
* `QUADS_CLOUD` and `QUADS_ASSIGNMENT_ID` leave blank initally
* `QUADS_DESCRIPTION` set to the description of your work
* `QUADS_QINQ` sets cloud q-in-q setting, 0 is default
* `QUADS_WIPE` determines if machines are wiped before being issued with the cloud, leave as true

> [!TIP]
> You will not have a username/password unless you have previously registered an account. If you have not created an account then, put the values you will use to register your account with.

Example:

```bash
export QUADS_SERVER=quads.example.com
export QUADS_USERNAME=username@example.com
export QUADS_PASSWORD=verysecurepassword
export QUADS_OWNER=username
export QUADS_CLOUD=
export QUADS_ASSIGNMENT_ID=
export QUADS_DESCRIPTION="Quick Scale Test"
export QUADS_QINQ=0
export QUADS_WIPE=true
```

Source `env.sh`:

```console
[user@fedora auto-quads]$ source env.sh
```

### 3. Register a New Account

Register your account with the QUADS server:

```console
[user@fedora auto-quads]$ ./auto-quads.py register
```

> [!TIP]
> Skip if you have already registered an account.

### 4. Create a Cloud

Create a new self-scheduled cloud environment:

```console
[user@fedora auto-quads]$ ./auto-quads.py create-cloud
Logged in successfully
Creating a new self-scheduled cloud

Description: Quick Scale Test
Owner: username
QinQ VLAN ID: 0
Wipe the cloud: true

Cloud created successfully

Cloud name: cloud04
Cloud Assignment ID: 425

Total time: 6 seconds
```

> [!NOTE]
> After creating the cloud, note the `Cloud name` and `Cloud Assignment ID` from the output

Add `Cloud name` and `Cloud Assignment ID` to your `env.sh`

Example:

```bash
export QUADS_SERVER=quads.example.com
export QUADS_USERNAME=username@example.com
export QUADS_PASSWORD=verysecurepassword
export QUADS_OWNER=username
export QUADS_CLOUD=cloud04
export QUADS_ASSIGNMENT_ID=425
export QUADS_DESCRIPTION="Quick Scale Test"
export QUADS_QINQ=0
export QUADS_WIPE=true
```

Source `env.sh` again:

```console
[user@fedora auto-quads]$ source env.sh
```

### 5. Check Available Hosts

List all available hosts that can be added to your cloud:

```console
[user@fedora auto-quads]$ ./auto-quads.py available-hosts
Getting available hosts:

host-001-r660.example.com
host-002-r650.example.com
host-003-r630.example.com
host-004-r630.example.com
host-005-r630.example.com
host-006-r630.example.com
host-007-r630.example.com
host-008-r630.example.com
host-009-r630.example.com

Total available hosts: 9

Total time: 0 seconds
```

### 6. Add Hosts to Cloud

Add one or more hosts to your cloud environment:

```console
[user@fedora auto-quads]$ ./auto-quads.py add-hosts host-003-r630.example.com host-004-r630.example.com host-005-r630.example.com host-006-r630.example.com
Logged in successfully
Adding host: host-003-r630.example.com to cloud: cloud04
Host added to cloud successfully
Adding host: host-004-r630.example.com to cloud: cloud04
Host added to cloud successfully
Adding host: host-005-r630.example.com to cloud: cloud04
Host added to cloud successfully
Adding host: host-006-r630.example.com to cloud: cloud04
Host added to cloud successfully

Total time: 1 seconds
```

### 7. Wait for Cloud Validation

Wait for the cloud to complete its validation process:

```console
[akrzos@fedora auto-quads]$ ./auto-quads.py wait-for-cloud
Waiting for a cloud cloud04 to complete validating
2025-12-01 13:46:56 UTC: cloud04 is not validated yet
2025-12-01 13:47:06 UTC: cloud04 is not validated yet
...
2025-12-01 14:19:51 UTC: cloud04 is validated

Total time: 1975 seconds
```

Optional parameters:
- `-t, --timeout`: Timeout in seconds (default: 900)
- `-p, --poll-interval`: Poll interval in seconds (default: 10)

### 8. Terminate Cloud

When finished, terminate the cloud to release the resources:

```console
[user@fedora auto-quads]$ ./auto-quads.py terminate-cloud
```

## Command Reference

### Global Options

- `-s, --quads-server`: QUADS server hostname (env: `QUADS_SERVER`)
- `-u, --username`: Username for QUADS API (env: `QUADS_USERNAME`)
- `-p, --password`: Password for QUADS API (env: `QUADS_PASSWORD`)
- `-c, --cloud`: Cloud name (env: `QUADS_CLOUD`)
- `-o, --owner`: Cloud owner (env: `QUADS_OWNER`)

### Available Commands

- `register`: Register a new account
- `create-cloud`: Create a new self-scheduled cloud
  - `-d, --description`: Cloud description
  - `-q, --qinq`: QinQ VLAN ID (0 or 1)
  - `-w, --wipe`: Wipe the cloud
- `available-hosts`: List available hosts
- `add-hosts`: Add one or more hosts to a cloud
- `wait-for-cloud`: Wait for a cloud to complete validating
  - `-i, --assignment-id`: Assignment ID
  - `-t, --timeout`: Timeout in seconds
  - `-p, --poll-interval`: Poll interval in seconds
- `terminate-cloud`: Terminate a cloud
  - `-i, --assignment-id`: Assignment ID (required)

## Tips

- Always source `env.sh` after making changes to environment variables
- Keep track of your `QUADS_CLOUD` and `QUADS_ASSIGNMENT_ID` values

## License

Licensed under the Apache License, Version 2.0. See LICENSE file for details.
