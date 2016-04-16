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

dirlist = os.walk('.').next()[1]
projects = ['Compliance','apex','armband','availability','bottlenecks','compass4nfv','conductor','copper','cperf','doctor','domino','dovetail','dpacc','enfv','escalator','fastpathmetrics','fds','fuel','functest','genesis','genesisreq','inspector','ipv6','joid','kvmfornfv','lsoapi','models','moon','movie','multisite','netready','octopus','onosfw','oscar','ovno','ovsnfv','parser','pharos','pinpoint','policytest','prediction','promise','qtip','releng','rs','sandbox','sdnvpn','securedlab','sfc','storperf','vnf_forwarding_graph','vswitchperf','yardstick']
script_dir = os.path.dirname(os.path.abspath(__file__))


def update():
    for project in  dirlist:
        sys.stdout.write("%sPulling updates from %s%s" % (MESSAGE, project, RESET))
        sys.stdout.write("\n\n")
        #print 'Pulling updates from {0}\n'.format(project)
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
    pyimps = []
    javaimp = []
    cinclude = []
    py = 0
    sh = 0
    java = 0
    c = 0
    for dirname, dirnames, filenames in os.walk(project):
        for filename in filenames:
            # check if python files
            if filename.endswith('.py'):
                py = py +1
                with open(os.path.join(dirname.rstrip(), filename)) as f:
                    for line in f.readlines():
                        match = re.search(r'import (\w+)', line)
                        if match:
                            pyimps.append(match.group(1))
            elif filename.endswith('.sh'):
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
        #print '{0} python files found.\n'.format(py)
        sys.stdout.write("%sPython modules Imported:%s" % (MESSAGE, RESET))
        sys.stdout.write("\n\n")
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
        sys.stdout.write("\n\n")
        # Remove duplicates
        javaimp = list(set(javaimp))
        print('\n'.join('{}: {}'.format(*k) for k in enumerate(javaimp)))
    if c > 1:
        sys.stdout.write("%s%s C files found.%s" % (MESSAGE,c, RESET))
        sys.stdout.write("\n\n")
        # Remove duplicates
        sys.stdout.write("%sC libraries Imported:%s" % (MESSAGE, RESET))
        sys.stdout.write("\n\n")
        cinclude = list(set(cinclude))
        print('\n'.join('{}: {}'.format(*k) for k in enumerate(cinclude)))
    if py < 1 and sh < 1 and java < 1 and c < 1:
        print "No code found for this project\n"


def main():
    for project in  dirlist:
        print 'Project {0}:\n'.format(project)
        audit(project)


if __name__ == "__main__":
    choice = None
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
