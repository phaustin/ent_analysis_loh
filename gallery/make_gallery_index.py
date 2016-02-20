"""

requires:

conda install pillow
pip install ruamel.yaml


 to run, cd to folder containg a directory with with png files
 put  gallery folder  in your PYTHONPATH

 and do:

 python -m make_gallery_index  my_png_folder  my_caption.yaml

 this will generate thumbnails in my_png_folder/thumbs, and a web
 page my_png_folder/index.html
"""

from jinja2 import Template
import build_gallery as bg
import ruamel.yaml
import textwrap, argparse

linebreaks=argparse.RawTextHelpFormatter
descrip=textwrap.dedent(globals()['__doc__'])
parser = argparse.ArgumentParser(formatter_class=linebreaks,description=descrip)
parser.add_argument('png_dir', type=str,help='folder containing png files')
parser.add_argument('caption_file', type=str,help = 'name of caption.yaml file')
args=parser.parse_args()


caption_file = args.caption_file
png_dir = args.png_dir

write_captions = True
if write_captions:
    figure_dict=bg.write_default_yaml(png_dir,caption_file)
else:
    with open(caption_file,'r') as f:
        figure_dict = ruamel.yaml.load(f)

caption_dict=bg.generateThumbnails(figure_dict)

template_path=bg.path_to_template('jinja_responsive.tmpl')
index_path='{}/index.html'.format(png_dir)    

with open(template_path,'r') as f:
    template = Template(f.read())

# #
# # this will write and index.html file in the png_dir directory
# # you should be able to see the plots by doing:
# #  > firefox index.html
# #
with open(index_path,'w') as f:
    f.write(template.render(captions=caption_dict))

