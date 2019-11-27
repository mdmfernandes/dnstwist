# -*- coding: utf-8 -*-
# dnstwist - Manage the effective TLD names database
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#   This module was added by Miguel Fernandes @ https://github.com/mdmfernandes
"""Manage the effective TLD names database

Check if the database is updated from https://publicsuffix.org/. If not, updates it!
"""
import re
from datetime import datetime

from requests import exceptions, get

UPDATE_PATTERN = r"<updated>(?P<updated>\S*)</updated>"


def get_last_updated():
    """Check for the last update of the database by fetching the GitHub commits history.

    Returns:
        str or None: a string with the last update date. None in case of error.
    """
    url = 'https://github.com/publicsuffix/list/commits/master.atom'

    try:
        res = get(url)
        res.raise_for_status()  # Raise errors for bad http status
    except (exceptions.ConnectionError, exceptions.MissingSchema, exceptions.HTTPError) as err:
        print("Error while connecting to 'github.com': ", err)
        return None

    atom = res.content.decode()

    last_updated = re.search(UPDATE_PATTERN, atom).group('updated')

    return last_updated


def download_tld_names_db(dest_file):
    """Download the effective TLD names database from https://publicsuffix.org/

    Args:
        dest_file (str): database file path.

    Returns:
        bool: True if success, False otherwise.
    """
    url = 'https://publicsuffix.org/list/public_suffix_list.dat'

    try:
        res = get(url)
        res.raise_for_status()  # Raise errors for bad http status
    except (exceptions.ConnectionError, exceptions.MissingSchema, exceptions.HTTPError) as err:
        print("Error while connecting to 'publicsuffix.org': ", err)
        return False

    # Save list to file
    with open(dest_file, 'w') as fp:
        fp.write(res.content.decode())

    return True


def update_tld_names_db(dest_file, update_file):
    """Update the effective TLD names database.

    Args:
        dest_file (str): database file path.
        update_file (str): path of the file with the last update date.
    """
    with open(update_file) as fp:
        local_file_update = fp.read()

    local_file_update = datetime.strptime(local_file_update, "%Y-%m-%dT%H:%M:%SZ")

    remote_file_update = get_last_updated()

    if remote_file_update:
        remote_file_update = datetime.strptime(remote_file_update, "%Y-%m-%dT%H:%M:%SZ")

        if local_file_update < remote_file_update:
            download_tld_names_db(dest_file)
            # print("[INFO] Updated TLD names database!")
            # Update the file with the last update date
            now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

            with open(update_file, 'w') as fp:
                fp.write(now)
