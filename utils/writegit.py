#!/usr/bin/env python
from __future__ import print_function
from configobj import ConfigObj
from pyutils import process
import os,textwrap,re,string

find_branch=re.compile('^\#\#\s(?P<branch>.*)')

def writeconfig(versionfile):
    #first get the branch and check to see whether it's clean
    status,output=process.command("git status -s -b -uno")
    output=output.split('\n')
    thematch=find_branch.match(output[0])
    branch=thematch.group('branch')
    if len(output) !=2:
        text = """
                  #########################
                  git status says files need to be checked in,
                  either commit or stash:
                  ------------------------
                  %s
               """
        raise Exception(textwrap.dedent(text) % string.join(output[1:],'\n'))
    status,commitid=process.command("git log --pretty='%h' -n 1")
    status,date=process.command("git log --pretty='%ci' -n 1")
    status,tags=process.command("git name-rev --always --tags HEAD")
    status,machine_output=process.command("uname -a")
    working_dir= os.getcwd()
    machine= machine_output.strip()
    versionobj=ConfigObj()
    versionobj.clear()
    versionobj['commitid']=commitid.strip()
    versionobj['branch']=branch.strip()
    versionobj['commit_date']=date.strip()
    versionobj['nearest_tag']=tags.strip()
    versionobj['working_dir']=working_dir
    versionobj['machine']=machine
    outfile=open(versionfile,'w')
    versionobj.write(outfile)
    outfile.write('\n')
    outfile.close()

if __name__=="__main__":
    configfile='/tmp/versioninfo.cfg'
    writeconfig(configfile)
    print("writing: ",configfile)
    
    


