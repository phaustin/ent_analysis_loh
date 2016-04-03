#!/usr/bin/env python
"""
  utility functions for building figure gallery
"""
from __future__ import print_function
import os
import os.path
from PIL import Image
import shutil
from collections import OrderedDict
import glob
import ruamel.yaml
import copy

"""
need to do pip install ruamel.yaml

Note if you can't use https://pypi.python.org/pypi/ruamel.yaml  then these suggestions show
how to get ordered read/write in pyyaml

#http://stackoverflow.com/questions/5121931/in-python-how-can-you-load-yaml-mappings-as-ordereddicts
import yaml
from collections import OrderedDict

def ordered_dump(data, stream=None, Dumper=yaml.Dumper, **kwds):
    class OrderedDumper(Dumper):
        pass
    def _dict_representer(dumper, data):
        return dumper.represent_mapping(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            data.items())
    OrderedDumper.add_representer(OrderedDict, _dict_representer)
    return yaml.dump(data, stream, OrderedDumper, **kwds)

# usage:
ordered_dump(data, Dumper=yaml.SafeDumper)

def ordered_load(stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
    class OrderedLoader(Loader):
        pass
    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))
    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)

# usage example:
#ordered_load(stream, yaml.SafeLoader)

#http://stackoverflow.com/questions/16782112/can-pyyaml-dump-dict-items-in-non-alphabetical-order
def represent_ordereddict(dumper, data):
    value = []
    for item_key, item_value in data.items():
        node_key = dumper.represent_data(item_key)
        node_value = dumper.represent_data(item_value)
        value.append((node_key, node_value))
    return yaml.nodes.MappingNode(u'tag:yaml.org,2002:map', value)

 #use: yaml.dump(figure_dict, f, default_flow_style=False)
"""

OPTIONS = {
    "thumbSize" : (300,300),
    }


def write_default_yaml(png_dir,caption_file = None):
    """
      scan png_dir for files ending in png, and build a nested
      dictionary with captions and file locations
      if caption_file exists, write it out as as yaml file

      sample yaml file:

        !!omap
        - title: big title for header bar
        - description: general gallery description
        - figures: !!omap
          - core_29875: !!omap
            - figpath: plots/core_29875.png
            - plotfile: core_29875.png
            - caption: 'write caption here for : core_29875.png'
          - core_29908: !!omap
            - figpath: plots/core_29908.png
            - plotfile: core_29908.png
            - caption: 'write caption here for : core_29908.png'
    """
    pngfiles='{}/*png'.format(png_dir)
    figpaths = glob.glob(pngfiles)
    print('found {} png files in pngfiles'.format(len(figpaths),pngfiles))
    plotfiles = [os.path.split(item)[1] for item in figpaths]
    captions = ['write caption here for : {}'.format(item)
                for item in plotfiles]
    yaml_dict = OrderedDict()
    yaml_dict['title']='big title for header bar'
    yaml_dict['description']= 'general gallery description'
    yaml_dict['png_dir'] = png_dir
    yaml_dict['figures'] = OrderedDict()
    for item in zip(figpaths, plotfiles, captions):
        figpath, plotfile, caption = item
        key, ext = os.path.splitext(plotfile)
        yaml_dict['figures'][key] = OrderedDict()
        # figdict=OrderedDict(figpath=figpath_a,plotfile=plotfile_a,caption=caption_a)
        # yaml_dict['figures'][key]= figdict
        dictpairs=[('figpath',figpath),('plotfile',plotfile),('caption',caption)]
        for innerkey,innervalue in dictpairs:
            print(innerkey,innervalue)
            yaml_dict['figures'][key][innerkey]=innervalue
    if caption_file:
        with open(caption_file,'w') as f:
            ruamel.yaml.dump(yaml_dict,f,Dumper=ruamel.yaml.RoundTripDumper,default_flow_style=False)
        print('wrote {}'.format(caption_file))
    return yaml_dict


def generateThumbnails(figure_dict):
    """
      generates thumbnails of a list of figures
      input:
         figure_dict:  a dictionary with the following nested (yaml) structure

        !!omap
        - title: big title for header bar
        - description: general gallery description
        - png_dir: plots
        - figures: !!omap
          - core_29875: !!omap
            - figpath: plots/core_29875.png
            - plotfile: core_29875.png
            - caption: 'write caption here for : core_29875.png'
          - core_29908: !!omap
            - figpath: plots/core_29908.png
            - plotfile: core_29908.png
            - caption: 'write caption here for : core_29908.png'

       returns:
         a deepcopy of figure_dict with the new key figlist containing
         the figures in a list for the jinja2 template generator.
    """
    galleryinfo = copy.deepcopy(figure_dict)
    figlist=[]        
    for key,figure in galleryinfo['figures'].items():        
        figlist.append(figure)
    galleryinfo['figlist'] = figlist
    thumbdir='{}/thumbs'.format(galleryinfo['png_dir'])
    if os.path.exists(thumbdir):
        shutil.rmtree(thumbdir)
        os.mkdir(thumbdir)
    else:
        os.mkdir(thumbdir)

    for fig_dict in galleryinfo['figlist']:
        # get figure filename
        # split up file and ext so it is easier to make jpg thumbnails, if so desired
        # make thumbnail
        im = Image.open(fig_dict['figpath'])
        im.thumbnail(OPTIONS['thumbSize'], Image.ANTIALIAS)
        print("processing %s" % fig_dict['plotfile'])
        im.save("{}/{}".format(thumbdir,fig_dict['plotfile']), "PNG")
    return galleryinfo

def path_to_template(template_name):
    """
        find the directory containing the template file template_name
    """
    head, _ =os.path.split(__file__)
    template='{}/{}'.format(head,template_name)
    if not os.path.exists(template):
        raise Exception('could not find {}'.format(template_name))
    return template

if __name__ == "__main__":
    #
    # execute in a directory which contains a folder called plots with png files
    # generate a nested dictionary for all the png files in the plots folder
    #
    out=write_default_yaml('plots')
    #
    #  write to test.yaml
    #
    caption_file ='test.yaml'
    with open(caption_file,'w') as f:
        ruamel.yaml.dump(out,f,Dumper=ruamel.yaml.RoundTripDumper,default_flow_style=False)
    with open(caption_file,'r') as f:
        input = ruamel.yaml.load(f,Loader=ruamel.yaml.RoundTripLoader)
    print(type(input),input)
    #
    # if you don't want to modify nested dictionary you can go straight to the file
    #
    figure_dict=write_default_yaml('plots','test2.yaml')
    
