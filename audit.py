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
import subprocess

dirlist = os.walk('.').next()[1]
projects = ['Compliance','apex','armband','availability','bottlenecks','compass4nfv','conductor','copper','cperf','doctor','domino','dovetail','dpacc','enfv','escalator','fastpathmetrics','fds','fuel','functest','genesis','genesisreq','inspector','ipv6','joid','kvmfornfv','lsoapi','models','moon','movie','multisite','netready','octopus','onosfw','oscar','ovno','ovsnfv','parser','pharos','pinpoint','policytest','prediction','promise','qtip','releng','rs','sandbox','sdnvpn','securedlab','sfc','storperf','vnf_forwarding_graph','vswitchperf','yardstick']
script_dir = os.path.dirname(os.path.abspath(__file__))


def update():
    for project in  dirlist:
        print 'Pulling updates from {0}\n'.format(project)
        os.chdir(os.path.join(script_dir.rstrip(), project))
        subprocess.call(["git", "pull"])
        print '\n'


def clone():
    for project in projects:
        if os.path.isdir(project):
            print 'A clone of {0} already exists'.format(project)
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
        print '{0} python files\n'.format(py)
        print 'Python modules Imported:\n'
        # Remove duplicates
        pyimps = list(set(pyimps))
        print pyimps
        print '\n'
    if sh > 1:
        print '{0} shellscript files\n'.format(sh)
    if java > 1:
        print '{0} java files\n'.format(java)
        print 'Java modules Imported:\n'
        # Remove duplicates
        javaimp = list(set(javaimp))
        print javaimp
        print '\n'
    if c > 1:
        print '{0} c files\n'.format(c)
        # Remove duplicates
        cinclude = list(set(cinclude))
        print cinclude
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
