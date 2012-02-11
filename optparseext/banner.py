# Copyright (c) 2012, Mario Vilas
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
Banner formatters for optparse
by Mario Vilas (mvilas at gmail dot com)

These are copies of IndentedHelpFormatter and TitledHelpFormatter, but they
allow you to print a banner before the help message.

You can set the banner at the first argument of the constructor, and change it
later by setting a new value for the "banner" instance variable.
"""

__all__ = ['BannerIndentedHelpFormatter', 'BannerTitledHelpFormatter']

import optparse

class BannerIndentedHelpFormatter(optparse.IndentedHelpFormatter):
    def __init__(self, banner, *argv, **argd):
        self.banner = banner
        optparse.IndentedHelpFormatter.__init__(self, *argv, **argd)
    def format_usage(self, usage):
        msg = optparse.IndentedHelpFormatter.format_usage(self, usage)
        return '%s\n%s' % (self.banner, msg)

class BannerTitledHelpFormatter(optparse.TitledHelpFormatter):
    def __init__(self, banner, *argv, **argd):
        self.banner = banner
        optparse.TitledHelpFormatter.__init__(self, *argv, **argd)
    def format_usage(self, usage):
        msg = optparse.TitledHelpFormatter.format_usage(self, usage)
        return '%s\n%s' % (self.banner, msg)
