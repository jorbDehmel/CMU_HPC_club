'''
A script to install package(s) on an entire cluster at once.

Maintainer(s):
- Jordan Dehmel (jedehmel@mavs.coloradomesa.edu)
'''

import sys
import os
from typing import List
import subprocess as sp
import platform
import rc


def main(args: List[str]) -> int:
    '''
    Install all the given packages.

    :param args: The command-line arguments.
    :returns: Zero upon success, non-zero on failure.
    '''

    os.system('rm -rf ./*_TMP')
    print(f'args: {args}')

    # Check args
    if len(args) < 4:

        # Throw error if insufficient arguments are provided
        print(
            "Please provide at least 3 arguments.\n"
            + "The first should be the node pattern,\n"
            + "the second should be the password,\n"
            + "and the rest should be packages."
        )

        return 1

    # Check OS
    if platform.system() != "Linux":

        # Throw error if not on a Linux system
        print(
            "This script cannot be run on a non-linux\n"
            + "system. Ensure that the master node is\n"
            + "the same platform as the worker nodes."
        )

        return 2

    node_pattern: str = args[1]
    password: str = args[2]
    packages: List[str] = args[3:]

    for i, package in enumerate(packages):
        print(f"Installing package {i} ({package}) on node(s) {node_pattern}")

        rc.remote_install_package(
            package,node_pattern, password)

    print("Done!")

    return 0


# If this is being run as a script, call the main function.
if __name__ == "__main__":
    sys.exit(main(sys.argv))
