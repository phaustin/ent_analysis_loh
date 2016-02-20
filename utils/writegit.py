#!/usr/bin/env python
import json
import os,textwrap,re,string
from collections import OrderedDict
import subprocess

find_branch=re.compile('^\#\#\s(?P<branch>.*)')

def gitinfo():
    #first get the branch and check to see whether it's clean
    status,output=subprocess.getstatusoutput("git status -s -b -uno")
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
    status,commitid=subprocess.getstatusoutput("git log --pretty='%h' -n 1")
    status,date=subprocess.getstatusoutput("git log --pretty='%ci' -n 1")
    status,tags=subprocess.getstatusoutput("git name-rev --always --tags HEAD")
    status,machine_output=subprocess.getstatusoutput("uname -a")
    working_dir= os.getcwd()
    machine= machine_output.strip()
    versiondict=OrderedDict()
    versiondict['commitid']=commitid.strip()
    versiondict['branch']=branch.strip()
    versiondict['commit_date']=date.strip()
    versiondict['nearest_tag']=tags.strip()
    versiondict['working_dir']=working_dir
    versiondict['machine']=machine
    return versiondict

def writeconfig(versionfile):
    versiondict=gitinfo()
    with open(versionfile,'w') as f:
        f.write(json.dumps(versiondict,indent=4,ensure_ascii=False))

if __name__=="__main__":
    configfile='/tmp/versioninfo.json'
    writeconfig(configfile)
    print("writing: ",configfile)
    with open(configfile,'r') as f:
        gitinfo = json.loads(f.read(),object_pairs_hook=OrderedDict)
    print('got: {}'.format(gitinfo))
    
    
    


