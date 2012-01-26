__license__ = '''
This file is part of "Pylli - Python Lost Libraries"
Copyright (C) 2011-2012  Daniel Garcia (cr0hn) | dani@iniqua.com

Golismero project site: http://code.google.com/p/pylli/
Golismero project mail: pylli.project@gmail.com

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
__copyright__ = "Copyright 2011-2012 - GoLismero project"
__credits__ = ["Daniel Garcia (cr0hn)"]
__maintainer__ = "Daniel Garcia"
__email__ = "pilly.project@gmail.com"
__status__ = "Testing"

import types
import xml.dom.minidom 

#
# MagicSerializer
class MagicSerializer:
    '''
    This class provide methods for serialize and deserialize and object. The file must have been serialized with this
    class because only understands their format.
    
    For serialize you need a structure data. The structure must be made by classes. Only this way is valid.
    
    Public methods are: Serialize and Deserialize. And you can use it writing: 
        - MagicSerializer.Serialize(...)
        - MagicSerializer.Deserialize(...)
    
    Examples:
    =========
    
        1. Serialize a structure data into a xml file.
        
            The data:
            ---------------------------------------
            class one:
                def __init__(self):
                    self.myvar = "bye"
                    self.other = "hello!"
            class two:
                def __init__(self):
                    self.name = "cr0hn"
                    self.myclass = one()
            ---------------------------------------
            
            We want to save data serialized into XML file calle "myproj.xml"
            >> v = two()
            >> MagicSerializer.Serialize(v, "myproj.xml")
            
            Now we can see results: 
            <two>                                                                                                                                                                                   
             <one>                                                                                                                                                                                  
               <myvar>bye</myvar>                                                                                                                                                                   
               <other>hello!</other>                                                                                                                                                                
             </one>                                                                                                                                                                                 
             <name>cr0hn</name>                                                                                                                                                                    
            </two>
            
        2. Deserialize file info contain into. Deserializer need where is location of your data definition. We want to load serialized the next:
            - An XML file (named "data.xml")
            - Into an object (named "a")
            - Your library is located in "mylibs.common.data"
            - And our class is the same that above.
            
            >>a = MagicSerializer.Deserialize(two, "data.xml", "mylibs.common.data")
            >> print a.name
            cr0hn
            >> print a.myclass.myvar
            bye
        
    '''    
    #: Location of libraries
    _libraries = None 
    
    #
    # Serialize
    @staticmethod
    def Serialize(obj_, file_):
        '''
        Serialize an object into a file.
        
        @param obj_: object to serialize
        @type obj_: object
        
        @param file_: File path to write info
        @type file_: str
        
        @return: no return.
        '''    
        if obj_ is not None and file_ is not None:
            # Open file
            f_h = None
            try:
                f_h = open(file_, "w")
            except:
                raise IOError("Error while try to open file")
            
            # Call private deserialzer
            MagicSerializer._serialize(obj_, f_h)
            
            f_h.flush()
            f_h.close()
            
            
        else:
            raise TypeError("obj_ and file_ must be not null")
            
    # END Serialize
    #
    
    #
    # _serialize
    @staticmethod
    def _serialize(obj_, file_, level_ = 0):
        '''
        Serialize an object
        
        @param obj_: object to serialize
        @type obj_: object
        
        @param file_: File handle to write info
        @type file_: file handle
        
        @param level_: deep level. Used for internal. Not be asigned.
        @type level_: int
        
        @return: no return.
        '''
        if obj_ is not None and file_ is not None:
            # Spaces for ident in file
            m_spaces = " " * level_
    
            # Check if obj_ is an Array
            if MagicSerializer._isList(obj_):
                
                # If dict
                if type(obj_) == types.DictionaryType:
                    for k, v in obj_.iteritems():
                        # If value is a list => recursivity
                        if MagicSerializer._isList(v):    
                            file_.write("{spaces}<{tag}>\n".format(tag = str(k), spaces = m_spaces))
                            MagicSerializer._serialize(v, file_, level_ + 1)
                            file_.write("{spaces}</{tag}>\n".format(tag = str(k), spaces = m_spaces))
                            
                        # If value is simple type write it
                        elif MagicSerializer._isSimple(v):
                            m_value = ""
                            if v is not None:
                                m_value = str(v).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
                                
                            file_.write("{spaces}<{tag}>{value}</{tag}>\n".format(tag = str(k), value = m_value, spaces = m_spaces))
                        # If value is an instance => recursivity
                        elif type(v) == types.InstanceType:
                            MagicSerializer._serialize(v, file_, level_ + 1)
                
                # If list
                if type(obj_) == types.ListType:
                    for v in obj_:
                        # If value is a list or an instance => recursivity
                        if MagicSerializer._isList(v) or type(v) == types.InstanceType:
                            MagicSerializer._serialize(v, file_, level_ + 1)
                        # If is a simpley type => write into file
                        elif MagicSerializer._isSimple(v):
                            file_write("{spaces}<{tag}>{value}</{tag}>".format(spaces = m_spaces, value = str(v), tag = obj_.__class__.__name__))
                            
            
            # If object is an instance   
            elif type(obj_) == types.InstanceType:
                
                # Write root
                file_.write("{spaces}<{tag}>\n".format(spaces = m_spaces, tag = obj_.__class__.__name__))
                
                # Looking for params
                for key, val in obj_.__dict__.iteritems():
                    # Check if is not a single type
                    if type(val) == types.InstanceType:
                        MagicSerializer._serialize(val, file_, level_ + 1)

                    # Si es una lista => recursividad
                    elif MagicSerializer._isList(val):   
                        file_.write("{spaces}  <{tag}>\n".format(spaces = m_spaces, tag = key))
                        MagicSerializer._serialize(val, file_, level_ + 4)
                        file_.write("{spaces}  </{tag}>\n".format(spaces = m_spaces, tag = key))
                    # If is a basic type
                    else:
                        
                        m_val = ""
                        if val is not None:
                            m_val = str(val).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
                        
                        # Write info
                        file_.write("{spaces} <{tag}>{value}</{tag}>\n".format(spaces = m_spaces, tag = key, value = m_val))
                
                # Ending tag
                file_.write("{spaces}</{tag}>\n".format(spaces = m_spaces, tag = obj_.__class__.__name__))
    # END _serialize
    #
    
    #
    # Deserialize
    @staticmethod
    def Deserialize(obj_, file_, libs_):
        '''
        Deserialize an object
        
        @param obj_: object type to deserialize
        @type obj_: object
        
        @param file_: path of file that contain xml info
        @type file_: str
        
        @param libs_: String with location of libraries of data that want to be loaded: for example: "thirdparty.mylibs"
        @type libs_: str
        
        @return: return an object filled as param obj_ type.
        @rtype: object
        '''
        if obj_ is not None and file_ is not None:
            dom = xml.dom.minidom.parse(file_)
            dom.hasChildNodes()
            
            # create private vars for libraries
            MagicSerializer._libraries = libs_
            
            return MagicSerializer._deserialize(obj_, dom)
    
    # END Deserialize
    #
            
    #
    # _deserialize
    @staticmethod
    def _deserialize(obj_, dom_):
        '''
        Private function of deserializer.
        
        @param obj_: object type to deserializer.
        @type obj_: object
        
        @param dom_: dom document from xml.dom.minidom.
        @type dom_: xml.dom.minidom.Document
        
        @return: object filled with xml info.
        @rtype: object
        
        '''
        # Object to return
        m_object_result = None 
        
        if obj_ is not None and dom_ is not None:
            # Check if obj_ is an Array
            if MagicSerializer._isList(obj_):
               # For each child node do:
                for cn in dom_:
                    # skip white spaces. A framework defect when load xml file
                    if cn.nodeType == xml.dom.Node.TEXT_NODE:
                        continue          
                    
                    exec("from %s import *" % MagicSerializer._libraries )
                    exec("m_object_result=%s()" % cn.nodeName)
                    

                    MagicSerializer._deserializeParams(cn , m_object_result)                    
                                
            
            # If object is an instance   
            elif type(obj_) == types.ClassType:
                
                for root in dom_.childNodes:
                    
                    # skip white spaces. A framework defect when load xml file
                    if root.nodeType == xml.dom.Node.TEXT_NODE:
                        continue
                    
                    # Get root
                    if obj_.__name__ != root.nodeName:
                        raise IOError("Invalid XML")

                    # Object must be created with "exec" call because if we create it with "type()", 
                    # for example, when we check the type returned it's "type" and don't have properties
                    # of "__class__" and "__dict__", needed for build an object
                    exec("from %s import *" % MagicSerializer._libraries )
                    exec("m_object_result=%s()" % obj_.__name__)

                    MagicSerializer._deserializeParams(root, m_object_result)

        return m_object_result

    # END _deserialize
    #    
    
    #
    # _exploreParams
    @staticmethod
    def _deserializeParams(root, object_result_):
        '''
        This method explore properties of a class/object 
        
        @param root: XML Node that contains properties associated to object "object_result_"
        @type root: xml.dom.minidom.Document
        
        @param object_result_: Object to explore
        @type object_result_: Object
        
        @return: None
        '''
        xml.dom.minidom.Document
        # Examine object type looking for each attribute into xml
        for at_value, at_type in object_result_.__dict__.iteritems():
            # If is simple type => store xml value (between tags) into object.
            if MagicSerializer._isSimple(at_type):
                l_n = root.getElementsByTagName(at_value)[0].childNodes
                if len(l_n) > 0:
                    object_result_.__dict__[at_value] = l_n[0].data
                    
            # If is a list or dict => store xml value (between tags) into object.
            elif MagicSerializer._isList(at_type):
                # dict?
                if type(at_type) == types.DictionaryType:
                    # Get container tag and then => recursivity
                    l_list = root.getElementsByTagName(at_value)[0].childNodes
                    t = MagicSerializer._deserialize(at_type, l_list)
                    if t is not None:
                        if isinstance(t, dict):
                            object_result_.__dict__[at_value].update(t)
                        else:
                            object_result_.__dict__[at_value] = t
                    
                # list?
                if type(at_type) == types.ListType:
                    # Fill with recursivity return
                    l_list = root.getElementsByTagName(at_value)[0].childNodes
                    t = MagicSerializer._deserialize(at_type, l_list)
                    if t is not None:
                        if isinstance(t, list):               
                            object_result_.__dict__[at_value].extend(t)        
                        else:
                            object_result_.__dict__[at_value].append(t)
    # END _exploreParams
    #
    
    #
    # _isList
    @staticmethod        
    def _isList(obj_):
        '''
        Check if parameter is a list or dict type
        
        @param obj_: object to check
        @type obj_: object
        
        @return: True if is a list, False otherwise
        @rtype: bool
        '''
        if type(obj_) == types.ListType or type(obj_) == types.DictType:
            return True
        else:
            return False 
    # END _isList    
    #
        
    
    #
    # _isSimple
    @staticmethod
    def _isSimple(obj_):
        '''
        Check if parameter is a simple type like a int, str, long...
        
        @param obj_: object to check
        @type obj_: object
        
        @return: True if is a simple type, False otherwise
        @rtype: bool
        '''    
        if type(obj_) != types.ListType and type(obj_) != types.DictType and type(obj_) != types.InstanceType:
            return True
        else:
            return False     
    # END _isSimple
    #
# END MagicSerializer
#
    
    