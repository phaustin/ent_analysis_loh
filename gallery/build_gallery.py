#!/usr/bin/env python
"""
  utility functions for building figure gallery
"""
from __future__ import print_function
import os
import os.path
from PIL import Image
import shutil


OPTIONS = {
    "thumbSize" : (300,300),
    }


def generateThumbnails(galleryinfo):
    """
      generates thumbnails of a list of figures
      input:
         galleryinfo:  a dictionary with at least two keys:
           plotdir:  full path to directory containing png files
           figlist:  list of dictonaries, each with keys
              figpath:  full path to figure
              plotfile:  name of png file
    """
    thumbdir='{}/thumbs'.format(galleryinfo['plotdir'])
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
    return None

def path_to_template(template_name):
    """
        find the directory containing the template file template_name
    """
    head, _ =os.path.split(__file__)
    template='{}/{}'.format(head,template_name)
    if not os.path.exists(template):
        raise Exception('could not find {}'.format(template_name))
    return template

