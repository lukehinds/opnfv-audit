#!/usr/bin/python
#
# Copyright (c) 2016 Red Hat
# Luke Hinds (lhinds@redhat.com)
# This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# 0.1: This script provides an audit of all files in opnfv repos

import os
import re
import sys
import subprocess

# terminal colors
START = "\x1b["
GREEN = "32m"
RED = "31m"
YELLOW = "33m"
BLUE = "34m"
PURPLE = "35m"
BOLD = "01;"
UNDERLINE = "04;"
RESET = "\x1b[00m"

BOLDGRN = START+BOLD+GREEN
BOLDRED = START+BOLD+RED
UNKNOWN = START+BOLD+YELLOW
TITLE = START+BOLD+PURPLE
MESSAGE = START+BOLD+BLUE

projects = ['Compliance','apex','armband','availability','bottlenecks','compass4nfv','conductor','copper','cperf','doctor','domino','dovetail','dpacc','enfv','escalator','fastpathmetrics','fds','fuel','functest','genesis','genesisreq','inspector','ipv6','joid','kvmfornfv','lsoapi','models','moon','movie','multisite','netready','octopus','onosfw','oscar','ovno','ovsnfv','parser','pharos','pinpoint','policytest','prediction','promise','qtip','releng','rs','sandbox','sdnvpn','securedlab','sfc','storperf','vnf_forwarding_graph','vswitchperf','yardstick']
script_dir = os.path.dirname(os.path.abspath(__file__))
dirlist = os.walk('.').next()[1]

def update():
    for project in  dirlist:
        sys.stdout.write("%sPulling updates from %s%s" % (MESSAGE, project, RESET))
        sys.stdout.write("\n\n")
        os.chdir(os.path.join(script_dir.rstrip(), project))
        subprocess.call(["git", "pull"])
        sys.stdout.write("\n")



def clone():
    for project in projects:
        if os.path.isdir(project):
            sys.stdout.write("%sA Clone of %s already exists in this folder (try update instead)%s" % (BOLDRED, project, RESET))
            sys.stdout.write("\n\n")
        else:
            proj = "git clone https://gerrit.opnfv.org/gerrit/{0}".format(project)
            subprocess.call([(proj)], shell=True)


def audit(project):
    # List for python imports
    pyimps = []
    # List for Java imports
    javaimp = []
    # List for C Includes
    cinclude = []
    # Counter for the amount of Python Files
    py = 0
    # Counter for the amount of shell scripts
    sh = 0
    # Counter for the amount of Java files
    java = 0
    # Counter for the amount of C source files
    c = 0
    for dirname, dirnames, filenames in os.walk(project):
        for filename in filenames:
            # check if python file
            if filename.endswith('.py'):
                # Lets count it
                py = py +1
                # Open the file to gather modules into pyimp list
                with open(os.path.join(dirname.rstrip(), filename)) as f:
                    for line in f.readlines():
                        # Regex match for import (e.g. import subprocess)
                        match = re.search(r'import (\w+)', line)
                        if match:
                            # Append each module to the pyimps list
                            pyimps.append(match.group(1))
            elif filename.endswith('.sh'):
                # Count shell scripts
                sh = sh +1
            elif filename.endswith('.java'):
                java = java +1
                with open(os.path.join(dirname.rstrip(), filename)) as f:
                    for line in f.readlines():
                        if 'import' in line:
                            line = line.split()
                            try:
                                javaimp.append(line[1])
                            except IndexError:
                                # Might need to improve on pass, its mainly
                                # there to capture out stuff that has proved
                                # useless
                                pass
            elif filename.endswith('.c'):
                c = c +1
                with open(os.path.join(dirname.rstrip(), filename)) as f:
                    for line in f.readlines():
                        if '#include' in line:
                            line = line.split()
                            try:
                                cinclude.append(line[1])
                            except IndexError:
                                pass
    if py > 1:
        sys.stdout.write("%s%s python files found.%s" % (MESSAGE,py, RESET))
        sys.stdout.write("\n\n")
        # Report the amount of Python Scrips found using the 'py counter'
        print '{0} python files found.\n'.format(py)
        # Print out the import modules found, in a nicer format then a long
        # python list
        sys.stdout.write("%sPython modules Imported:%s" % (MESSAGE, RESET))
        sys.stdout.write("\n")
        # Remove duplicates
        pyimps = list(set(pyimps))
        print('\n'.join('{}: {}'.format(*k) for k in enumerate(pyimps)))
        print '\n'
    if sh > 1:
        print '{0} shellscript files found\n'.format(sh)
    if java > 1:
        sys.stdout.write("%s%s python files found.%s" % (MESSAGE,java, RESET))
        sys.stdout.write("\n\n")
        sys.stdout.write("%sJava modules Imported:%s" % (MESSAGE, RESET))
        sys.stdout.write("\n")
        # Remove duplicates
        javaimp = list(set(javaimp))
        print('\n'.join('{}: {}'.format(*k) for k in enumerate(javaimp)))
    if c > 1:
        sys.stdout.write("%s%s C files found.%s" % (MESSAGE,c, RESET))
        sys.stdout.write("\n\n")
        # Remove duplicates
        sys.stdout.write("%sC libraries Imported:%s" % (MESSAGE, RESET))
        sys.stdout.write("\n")
        cinclude = list(set(cinclude))
        print('\n'.join('{}: {}'.format(*k) for k in enumerate(cinclude)))
    if py < 1 and sh < 1 and java < 1 and c < 1:
        print "No code found for this project\n"


def main():
    for project in  dirlist:
        print 'Project {0}:\n'.format(project)
        audit(project)


if __name__ == "__main__":
    # This needs work, would be better if it returned to prompt after each
    # action
    print "(c)lone or (u)pdate or (a)udit\n"
    val = raw_input("Enter Option: ").lower()
    print '\r'
    if val == 'c':
        clone()
    elif val == 'u':
        update()
    elif val == 'a':
        main()
    else:
        print "Not an option!"
