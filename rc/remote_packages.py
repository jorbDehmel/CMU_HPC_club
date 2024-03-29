"""
Resources for installing packages remotely over SSH. Relies on
PDSH for the PDCP utility, and assumes a Linux-Mint environment
for both host and nodes. If these assumptions do not hold, this
package **will likely not work.** PDSH is required on the master
and all the worker nodes. PDSH is thus the only package which
cannot be installed with these functions: You will have to
manually install it on all nodes.

Maintainer(s):
- Jordan Dehmel (jedehmel@mavs.coloradomesa.edu)
"""

import subprocess as sp
from typing import Union
import os
import shutil


def download_package(package_name: str, save_to: str) -> None:
    """
    Downloads the given package, along with all its
    dependencies, to the given folder. These will be saved as
    *.deb files which can be installed w/ `dpkg`. Requires an
    internet connection.

    :param package_name: The package to start at for download.
    :param save_to: Where to save the package(s).
    :returns: Nothing.
    """

    # Save cwd
    old_cwd: str = os.getcwd()

    # Make target and cd to it
    os.mkdir(save_to)
    os.chdir(save_to)

    print(f'Now in {os.getcwd()}')

    # Download all packages
    os.system(f"apt-get download $(apt-cache depends -i {package_name} | grep -v \"^ \" | grep -v ^libc-dev$)")

    os.system("ls")

    # Change back to old cwd
    os.chdir(old_cwd)

    print(f'Now in {os.getcwd()}')


def send_folder(folder_to_send: str, destination_path: str, to_nodes: str, password: Union[str, None] = None) -> None:
    """
    Send a folder over SSH using PDSH to all nodes specified.
    Requires this computer to be able to access all specified
    nodes. **Note:** Must not send to a location which requires
    sudo privileges!

    :param folder_to_send: The folder to send.
    :param destination_path: The place to save the sent folder.
    :param to_nodes: The PDCP hosts pattern to send to.
    :returns: Nothing.
    """

    run_command(f"mkdir -p {destination_path}", to_nodes)

    os.system(f"pdcp -r -w {to_nodes} \"{os.getcwd()}/{folder_to_send}\" \"{destination_path}\"")


def run_command(command: str, on_nodes: str, password: Union[str, None] = None) -> None:
    """
    Runs a single command on the given nodes. Uses PDSH under
    the hood.

    :param command: The command to run on each foreign node.
    :param on_nodes: The PDSH pattern to send the command to.
    :param password: If needed, the password for `sudo`. Do not
        feed this any password you care about!
    :returns: Nothing.
    """

    print(command)

    if password:
        sp.run(["pdsh", "-w", on_nodes, f"echo {password} | sudo -S {command}"],
            check=True)

    else:
        sp.run(["pdsh", "-w", on_nodes, f"{command}"],
            check=True)


def remote_install_package(package: str, on_nodes: str, password: str) -> None:
    """
    Install the given package and all its dependencies on all of
    the specified nodes. Uses PDSH and PDCP.

    :param package: The package to begin the install with.
    :param on_nodes: The node pattern to install to. See PDSH.
    :param password: The **trivial** password. Only do this if
        the nodes have a trivial, consistant password (for
        instance, "password").
    :returns: Nothing.
    """

    # Create temporary download folder
    download_location: str = package + "_TMP"

    # Download all the package *.deb files
    download_package(package, download_location)

    # Send all the package *.deb files
    send_folder(download_location, '/home/slurm/' + download_location, on_nodes, password)

    # Send install command to all nodes
    run_command(
        f"echo \"{password}\" | sudo -S dpkg -R --force-depends -i /home/slurm/{download_location}",
        on_nodes)

    # Clean up
    shutil.rmtree(download_location)
