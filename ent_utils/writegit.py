#!/usr/bin/env python
"""
  this utility writes git commit information out as dictonary and
  as a json file

  to use:

  put ent_analysis in your PYTHONPATH

  cd to the repository folder  

  python -m ent_utils.writegit  

  if status is clean, output should look like

  OrderedDict([   ('commitid', 'eb8ec6d'),
                ('branch', 'phil'),
                ('commit_date', '2016-02-20 11:38:12 -0800'),
                ('nearest_tag', 'HEAD undefined'),
                ('working_dir', '/Users/phil/repos/ent_analysis_loh'),
                (   'machine',
                    'Darwin rail.local 14.5.0 Darwin Kernel Version 14.5.0: '
                    'Tue Sep  1 21:23:09 PDT 2015; '
                    'root:xnu-2782.50.1~1/RELEASE_X86_64 x86_64')])
"""

import json
import os,textwrap,re,string
from collections import OrderedDict
import subprocess, argparse

linebreaks=argparse.RawTextHelpFormatter
descrip=textwrap.dedent(globals()['__doc__'])
parser = argparse.ArgumentParser(formatter_class=linebreaks,description=descrip)
args = parser.parse_args()

find_branch=re.compile('^\#\#\s(?P<branch>.*)')

def gitinfo():
    #first get the branch and check to see whether it's clean
    status,output=subprocess.getstatusoutput("git status -s -b -uno")
    output=output.split('\n')
    thematch=find_branch.match(output[0])
    branch=thematch.group('branch')
    if len(output) !=1:
        text = """
                  #########################
                  git status says files need to be checked in,
                  either commit or stash:
                  ------------------------
                  {}
               """
        raise Exception(textwrap.dedent(text).format('\n'.join(output[1:])))
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
    import pprint
    pp = pprint.PrettyPrinter(indent=4)
    configfile='/tmp/versioninfo.json'
    writeconfig(configfile)
    print("writing: ",configfile)
    with open(configfile,'r') as f:
        gitoutput= json.loads(f.read(),object_pairs_hook=OrderedDict)
    pp.pprint(gitoutput)
    
    
    


