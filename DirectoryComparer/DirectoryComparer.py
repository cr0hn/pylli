#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys, filecmp
from multiprocessing import *


__license__ = '''
This file is part of "Pylli - Python Lost Libraries"
Copyright (C) 2011-2012  Daniel Garcia (cr0hn) | dani@iniqua.com

PyLli project site: http://code.google.com/p/pylli/
PyLli project mail: project.pylli@gmail.com

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
'''

__author__ = "Daniel Garcia (cr0hn) - dani@iniqua.com"
__copyright__ = "Copyright 2011-2012 - Python Lost Libraries project"
__credits__ = ["Daniel Garcia (cr0hn)"]
__maintainer__ = "Daniel Garcia"
__email__ = "project.pylli@gmail.com"
__status__ = "Testing"


'''

This file contains functionality for compare 2 dirs and get equals files.

1 - How to use?

        You can use use with command line or with api.
        
2 - Use with command line

        You can use with comman line:
        
        >> DirectoryComparer.py dir1 dir2
        [-] Start
        [-] Results (display equals files):
        [--] /home/cr0hn/dir1/file1 <-> /home/cr0hn/ekdir/file1
        [--] /home/cr0hn/dir1/oaks/file2 <-> /home/cr0hn/okwl/file2

3 - Use as library

        For use as library you must follow the next steps:
        
        from DirectoryComprarer import *
        
        d = DirectoryComparer()
        results = d.CheckDirs(dir1, dir2)
        print results

'''



#
# DirectoryComparer
class DirectoryComparer:
        
        #
        # __init__
        def __init__(self, maxthreads = 10):
                '''
                @param maxthreads: Maximun number of process
                @type maxthreads: int
                '''
                #: Store modified files in mutual exclusion
                self._files = Manager().list()
                self._pool = Pool(processes=maxthreads)
        # END __init__
        #
        
                
        #
        # CheckDirs
        def CheckDirs(self, dir1, dir2):
                '''
                Compare dir1 with dir2, file to file, and find files that are equals.
                
                @param dir1: dir1 to compare.
                @type dir1: str
                
                @param dir2: dir2 to compare.
                @type dir2: str
                
                @return: list of list that contains files that are equals.
                @rtype: list(list())
                '''
                # Start
                self._walkDir1(dir1, dir2)
                
                # wail for all threads
                self._pool.close()
                self._pool.join()
    
                return self._files
        # END CheckDirs
        #
        
        
        #
        # _walkDir1
        def _walkDir1(self, dir, dir2):
                '''
                Looking for files of dir tree into dir2.
                
                @param dir: first dir to compare.
                @type dir: str
                
                @param dir2: second dir to compare.
                @type dir2: str
                
                @return: None
                '''
                dir = os.path.abspath(dir)
                for file in [file for file in os.listdir(dir) if not file in [".",".."]]:
                        nfile = os.path.join(dir,file)
                        
                        # recurisivity
                        if os.path.isdir(nfile):
                                # Recursivity
                                self._walkDir1(nfile, dir2)                                   
                        else:
                                # Looking for second dir
                                self._pool.apply_async(_walkDir2, (dir2, nfile, self._files))
        # END _walkDir1
        #
        
# END DirectoryComparer
#
                                
# 
# _walkDir2
def _walkDir2(dir, compare_file, files_):
        '''
        Search matches of "compare_file" into dir and their tree.
        
        @param dir: dir where fin file.
        @type dir: str
        
        @param compare_file: file to find.
        @type compare_file: str
        
        @param files_: list where store results
        @type files_: list
        
        @return: None
        '''
        dir = os.path.abspath(dir)
        for file in [file for file in os.listdir(dir) if not file in [".",".."]]:
                # Complete path name
                nfile = os.path.join(dir,file)
                # recurisivity
                if os.path.isdir(nfile):
                        _walkDir2(nfile, compare_file, files_)
                else: 
                        # if are equals => append
                        if filecmp.cmp(nfile, compare_file):
                                files_.append([nfile, compare_file])
# END _walkDir2
#


#
# Usage
def Usage():
        print ""
        print "Usage: DirectoryComparer Dir1 Dir2"        
        print ""
# END Usage
#
        
#
# Credits
def Credits():
        print ""
        print "Daniel Garcia (cr0hn) - dani@iniqua.com"
        print ""
# END Credits
#


if __name__ == "__main__":
        
        
        Credits()        
        
        arg = sys.argv        
        
        # Check params
        if len(arg) != 3:
                Usage()
                sys.exit(1)

        dir1 = arg[1]        
        dir2 = arg[2]
        
        if os.path.exists(dir1) is False:
                print "[!] %s not exist" % dir1
                sys.exit(1)
        
        if os.path.exists(dir2) is False:
                        print "[!] %s not exist" % dir2
                        sys.exit(1)
         
        # Start
        print "[-] Start"
        d = DirectoryComparer().CheckDirs(dir1, dir2)
        print "[-] Results (display equals files):"
        
        for l_d in d:
                print "[--] %s <-> %s" % (l_d[0], l_d[1])
                
        print ""
