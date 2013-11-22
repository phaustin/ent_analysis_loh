#!/usr/bin/python                                                                                             
import os, glob, shutil
import model_param as mc

def transfer(filename):
	f = filename.split('_')
	print "Transferring... " + filename
	
	# netCDF file destination base folder
	dst = mc.data_directory
	if(f[1] == 'CORE'):
		shutil.move(filename, '%s/core_entrain/' % (dst))
	elif (f[1] == 'CLOUD'):
		shutil.move(filename, '%s/condensed_entrain/' % (dst))
	else:
		shutil.move(filename, '%s/variables/' % (dst))

	return

if __name__ == "__main__":
	transfer()