import site,glob
import os
site.addsitedir('../gallery')
from jinja2 import Template
import build_gallery as bg
figures=glob.glob('plots/*png')
print(figures)
captions=dict()

files=['plots/chan1.png', 'plots/chan31.png', 'plots/cloudmask.png', 'plots/landmask.png']
captions['chan1.png']='channel 1 reflectance (%)'
captions['chan31.png']='channel 31 radiance (W/m^2/um/sr)'
captions['cloudmask.png']='0 = Cloud;1 = 66% prob. Clear;2 = 95% prob. Clear;3 = 99% prob. Clear'
captions['landmask.png']='0=Water;1=Coastal;2=Desert;3=Land'


figlist=[]
title='title'
for count,i in enumerate(files):
    the_dir,plotfile=os.path.split(i)
    figpath=os.path.abspath(i)
    figlist.append(dict(title=title,plotfile=plotfile,figpath=figpath,
                    caption=captions[plotfile]))

plotdir='plots'    
figdict=dict(plotdir=plotdir,title='cloudmask',description='MYD021KM.A2014125.2135',
             figlist=figlist)

bg.generateThumbnails(figdict)

template_path=bg.path_to_template('jinja_responsive.tmpl')
index_path='{}/index.html'.format(plotdir)    

with open(template_path,'r') as f:
    template = Template(f.read())

#
# this will write and index.html file in the plotdir directory
# you should be able to see the plots by doing:
#  > firefox index.html
#
with open(index_path,'w') as f:
    f.write(template.render(captions=figdict))

