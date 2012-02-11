# Reusable generator
# Copyright (c) 2009, Mario Vilas
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice,this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the copyright holder nor the names of its
#       contributors may be used to endorse or promote products derived from
#       this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

"""
Calls a generator and iterates it. When it's finished iterating, the
generator is called again. This allows you to iterate a generator more
than once (well, sort of, since the generator is actually recreated).

@see: U{http://breakingcode.wordpress.com/2009/12/13/quickpost-reusing-python-generator-objects/}
"""

__all__ = ['Regenerator']

class Regenerator(object):
    """
    Calls a generator and iterates it. When it's finished iterating, the
    generator is called again. This allows you to iterate a generator more
    than once (well, sort of, since the generator is actually recreated).
    """
    def __iter__(self):
        return self
    def __init__(self, g_function, *v_args, **d_args):
        self.__g_function = g_function
        self.__v_args     = v_args
        self.__d_args     = d_args
        self.__g_object   = None
    def next(self):
        if self.__g_object is None:
            self.__g_object = self.__g_function( *self.__v_args, **self.__d_args )
        try:
            return self.__g_object.next()
        except StopIteration:
            self.__g_object = None
            raise

def _squares( size ):
    """
    Auxiliary function to L{squares}.
    """
    for x in xrange( size ):
        yield x * x
    return
def squares( size ):
    """Example of reusable generator.

    >>> gen = squares( 10 )
    >>> list( gen )
    [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
    >>> list( gen )
    [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
    >>> list( gen )
    [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
    """
    return Regenerator( _squares, size )

