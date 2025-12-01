#!/usr/bin/env python3
#
# Tool to obtain a self-scheduled quads environment
#
#  Copyright 2025 Red Hat
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.


import argparse
import base64
from datetime import datetime, timezone
import os
import urllib3
import requests
import sys
import time


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def add_host_to_cloud(cliargs, token, hostname):
  print("Adding host: {} to cloud: {}".format(hostname, cliargs.cloud))
  endpoint = "https://{}/api/v3/schedules".format(cliargs.quads_server)
  headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer {}".format(token)
  }
  payload = {
    "cloud": cliargs.cloud,
    "hostname": hostname
  }
  response = requests.post(endpoint, verify=False, headers=headers, json=payload)
  if response.status_code != 200:
    print("Failed to add host to cloud: {}".format(response.text))
    sys.exit(1)
  else:
    print("Host added to cloud successfully")


def available_hosts(cliargs):
  total_available = 0
  print("Getting available hosts: \n")
  endpoint = "https://{}/api/v3/available?can_self_schedule=true".format(cliargs.quads_server)
  response = requests.get(endpoint, verify=False)
  for host in response.json():
    print(host)
    total_available += 1
  print("\nTotal available hosts: {}".format(total_available))


def create_cloud(cliargs, token):
  print("Creating a new self-scheduled cloud\n")
  print("Description: {}".format(cliargs.description))
  print("Owner: {}".format(cliargs.owner))
  print("QinQ VLAN ID: {}".format(cliargs.qinq))
  print("Wipe the cloud: {}\n".format(cliargs.wipe))

  endpoint = "https://{}/api/v3/assignments/self".format(cliargs.quads_server)
  headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer {}".format(token)
  }
  payload = {
    "description": cliargs.description,
    "owner": cliargs.owner,
    "qinq": cliargs.qinq,
    "wipe": cliargs.wipe
  }
  response = requests.post(endpoint, verify=False, headers=headers, json=payload)
  if response.status_code != 201:
    print("Failed to create cloud: {}".format(response.text))
    sys.exit(1)
  else:
    print("Cloud created successfully\n")
    print("Cloud name: {}".format(response.json()["cloud"]["name"]))
    print("Cloud Assignment ID: {}".format(response.json()["notification"]["assignment_id"]))


# Only function that returns a value (The token)
def login(cliargs):
  endpoint = "https://{}/api/v3/login".format(cliargs.quads_server)
  headers = {
    "Content-Type": "application/json",
    "Authorization": "Basic {}".format(base64.b64encode(f"{cliargs.username}:{cliargs.password}".encode()).decode())
  }
  response = requests.post(endpoint, verify=False, headers=headers)
  if response.status_code != 200:
    print("Failed to login: {}".format(response.text))
    sys.exit(1)
  else:
    token = response.json()["auth_token"]
    print("Logged in successfully")
  return token


def register(cliargs):
  print("Registering a new account")

  endpoint = "https://{}/api/v3/register".format(cliargs.quads_server)
  headers = {
    "Content-Type": "application/json"
  }
  payload = {
    "username": cliargs.username,
    "password": cliargs.password
  }
  response = requests.post(endpoint, verify=False, headers=headers, json=payload)
  if response.status_code != 200:
    print("Failed to register: {}".format(response.text))
    sys.exit(1)
  else:
    print("Registered successfully")


def terminate_cloud(cliargs, token):
  print("Terminating a cloud")
  print("Cloud name: {}".format(cliargs.cloud))
  endpoint = "https://{}/api/v3/assignments/terminate/{}".format(cliargs.quads_server, cliargs.assignment_id)
  headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer {}".format(token)
  }
  response = requests.post(endpoint, verify=False, headers=headers)
  print("Status code: {}".format(response.status_code))
  if response.status_code != 200:
    print("Failed to terminate cloud: {}".format(response.text))
    sys.exit(1)
  else:
    print("Cloud terminated successfully")


def wait_for_cloud(cliargs):
  print(f"Waiting for a cloud {cliargs.cloud} to complete validating")
  end_time = time.time() + cliargs.timeout
  endpoint = "https://{}/api/v3/assignments/{}".format(cliargs.quads_server, cliargs.assignment_id)
  headers = {
    "Content-Type": "application/json"
  }
  while time.time() < end_time:
    response = requests.get(endpoint, verify=False, headers=headers)
    if str(response.json()["validated"]).lower() == "false":
      print(f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}: {cliargs.cloud} is not validated yet")
    else:
      print(f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}: {cliargs.cloud} is validated")
      break
    time.sleep(cliargs.poll_interval)


def main():
  start_time = time.time()
  parser = argparse.ArgumentParser(
      description="Tool to obtain a self-scheduled quads environment",
      prog="auto-quads.py", formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  parser.add_argument("-s", "--quads-server", default=os.environ.get("QUADS_SERVER"), help="QUADS server hostname (env: QUADS_SERVER)")
  parser.add_argument("-u", "--username", default=os.environ.get("QUADS_USERNAME"), help="Username for QUADS API (env: QUADS_USERNAME)")
  parser.add_argument("-p", "--password", default=os.environ.get("QUADS_PASSWORD"), help="Password for QUADS API (env: QUADS_PASSWORD)")
  parser.add_argument("-c", "--cloud", default=os.environ.get("QUADS_CLOUD"), help="Cloud name (env: QUADS_CLOUD)")
  parser.add_argument("-o", "--owner", default=os.environ.get("QUADS_OWNER"), help="Cloud owner (env: QUADS_OWNER)")

  subparsers = parser.add_subparsers(dest="command")

  parser_register = subparsers.add_parser("register",
      help="Register a new account", formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  parser_create = subparsers.add_parser("create-cloud",
      help="Create a new self-scheduled cloud", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser_create.add_argument("-d", "--description", default=os.environ.get("QUADS_DESCRIPTION"), help="Cloud description (env: QUADS_DESCRIPTION)")
  parser_create.add_argument("-q", "--qinq", type=int, choices=[0, 1], default=os.environ.get("QUADS_QINQ", 0), help="QinQ VLAN ID (env: QUADS_QINQ)")
  parser_create.add_argument("-w", "--wipe", action="store_true", default=os.environ.get("QUADS_WIPE", False), help="Wipe the cloud (env: QUADS_WIPE)")

  parser_available = subparsers.add_parser("available-hosts",
      help="List available hosts", formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  parser_add = subparsers.add_parser("add-hosts",
      help="Add one or more hosts to a cloud", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser_add.add_argument("hostname", nargs='+', help="Hostname(s) to add to the cloud")

  parser_wait = subparsers.add_parser("wait-for-cloud",
      help="Wait for a cloud to complete validating", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser_wait.add_argument("-i", "--assignment-id", default=os.environ.get("QUADS_ASSIGNMENT_ID"), help="Assignment ID (env: QUADS_ASSIGNMENT_ID)")
  parser_wait.add_argument("-t", "--timeout", type=int, default=900, help="Timeout in seconds (env: QUADS_TIMEOUT)")
  parser_wait.add_argument("-p", "--poll-interval", type=int, default=10, help="Poll interval in seconds (env: QUADS_POLL_INTERVAL)")

  parser_terminate = subparsers.add_parser("terminate-cloud",
      help="Terminate a cloud", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser_terminate.add_argument("-i", "--assignment-id", default=os.environ.get("QUADS_ASSIGNMENT_ID"), required=True, help="Assignment ID (env: QUADS_ASSIGNMENT_ID)")
  cliargs = parser.parse_args()
  
  # Validate required arguments
  if not cliargs.quads_server:
    parser.error("--quads-server is required (or set QUADS_SERVER env var)")

  # Auto determine owner value if not provided
  quads_owner = cliargs.username.split("@")[0]
  if not cliargs.owner:
    cliargs.owner = quads_owner

  if cliargs.command == "register":
    register(cliargs)
  elif cliargs.command == "create-cloud":
    token = login(cliargs)
    create_cloud(cliargs, token)
  elif cliargs.command == "available-hosts":
    available_hosts(cliargs)
  elif cliargs.command == "add-hosts":
    token = login(cliargs)
    for hostname in cliargs.hostname:
      add_host_to_cloud(cliargs, token, hostname)
  elif cliargs.command == "wait-for-cloud":
    wait_for_cloud(cliargs)
  elif cliargs.command == "terminate-cloud":
    token = login(cliargs)
    terminate_cloud(cliargs, token)
  else:
    parser.print_help()
    sys.exit(1)

  end_time = time.time()
  total_time = round(end_time - start_time)
  print("\nTotal time: {} seconds".format(total_time))

if __name__ == "__main__":
  sys.exit(main())
