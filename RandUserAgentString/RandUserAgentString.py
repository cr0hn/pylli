#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2011 Francisco J. Gomez (aka) ffranz
# All rights reserved.

import urllib
import re
import sys
import os
import urllib2
from random import choice
try:
	from BeautifulSoup import BeautifulSoup
except ImportError:
	print ("BeautifulSoup can't be imported.")
	sys.exit()

__license__ = '''
Copyright (C) 2012  Francisco J. Gomez (@ffranz) // ffranz@iniqua.com

Source data is not mantained by script author and could change.

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
__author__ = "Francisco J. Gomez (@ffranz) - ffranz@iniqua.com"
__copyright__ = "Copyright 2012"
__credits__ = ["@ffranz"]
__maintainer__ = "Francisco J. Gomez"
__email__ = "ffranz@iniqua.com"
__status__ = "Beta"

"""
TODO:
	- To implement limit User Agent list control lenght
	
Example:
        
    from RandUserAgentString import *
    
	data = RandUserAgentString()
	print "Random User String: "+data.getOne()
	print "Founded "+str(len(data.getList()))+" user strings."
"""

class RandUserAgentString:

	def __init__(self, length = 25):
		"""
		@param length: User Agent list length
		@type length: int
		"""
		self._last = 0
		self._length = length
		self._list = []
		self._loadList()
	
	def _getData(self):
		"""
		Get data from URL or File

		@return: URL or file data
		#rtype: file-like  
		"""

		url = "http://www.useragentstring.com/pages/All/"
		try:
			data = urllib2.urlopen(url)
			file = open('randuseragentstring.html','w')
			aux = data.read()
			file.write(aux)
			file.close()
			data.close()
			return aux
		except urllib2.URLError, e:
			auxfile = "randuseragentstring.html"
			return open(auxfile, 'r')

	def _loadList(self):
		"""
		Generate variable length list of User Angents Strings
		
		@return: None
		"""
		try:
			pastes = self._getData()
			souppastes = BeautifulSoup(pastes)
			links = souppastes.findAll('a')
			for link in links:
				try:
					if link['href']:
						if link['href'].find("_id_") != -1:
							self._list.append(link.string)
				except Exception:
					# Handle programer 'href' errors 
					pass
		except Exception, e:
			print ('[!] Error found: ',str(e))

	def reloadList(self,len = -1):
		"""
	 	Regenerate variable length list of User Angents Strings
	 	
	 	@return: None
		"""
		if len != -1: self._length = len
		self._list = []
		self._last = 0
		self._loadList()
	
	def getOne(self,rand = True):
		"""
		Get one User String from list using random or round-robin politic.
		
		@param rand: Determine used politic for selection
		@type rand: bool
		
		@return: User Agent string
		@rtype: string
		"""
		if rand == True:
			if len(self._list) == 0:
				return ""
			else:
				return choice(self._list)
		else:
			self._last = self._last + 1
			if self._last == len(self._list):
				self._last = 0
			return self._list[self._last]
	
	def getList(self):
		"""
		Get all User Agent string list
		
		@return: User Agent string list
		@rtype: list
		"""
		return self._list
			
def testing():
	data = RandUserAgentString()
	print "Random User String: "+data.getOne()
	print "Found "+str(len(data.getList()))+" user strings."

if __name__ == "__main__":
	sys.exit(testing())
