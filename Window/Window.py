# Simple class to manipulate a window's input
# by Mario Vilas (mvilas at gmail.com)

# Copyright (c) 2009, Mario Vilas
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the copyright holder nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER ''AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from win32con import *
from win32gui import *
from win32api import *

import time
import struct


VK_ALT = VK_MENU


class Position:
    "Window position on the screen"

    restoreToMaximized = False
    showCmd = 0     # Show state
    minX    = 0     # Minimized position: X coordinate
    minY    = 0     # Minimized position: Y coordinate
    maxX    = 0     # Maximized position: X coordinate
    maxY    = 0     # Maximized position: Y coordinate
    x       = 0     # Restored position: X coordinate
    y       = 0     # Restored position: Y coordinate
    w       = 0     # Restored position: width
    h       = 0     # Restored position: height

    def __init__(self, data = None):
        if data is not None:
            if type(data) == type(0):
                self.fromWindowHandle(data)
            elif type(data) == type( () ):
                self.fromWindowPlacement(data)
            elif hasattr(data, 'getHandle'):
                self.fromWindow(data)
            else:
                raise Exception, "Unknown parameter for Position constructor: %r" % data

    def fromWindow(self, win):
        self.fromWindowHandle( win.getHandle() )

    def fromWindowHandle(self, hWnd):
        self.fromWindowPlacement( GetWindowPlacement(hWnd) )

    def fromWindowPlacement(self, windowPlacement):
        self.restoreToMaximized = windowPlacement[0] == WPF_RESTORETOMAXIMIZED
        self.showCmd            = windowPlacement[1]
        self.minX               = windowPlacement[2][0]
        self.minY               = windowPlacement[2][1]
        self.maxX               = windowPlacement[3][0]
        self.maxY               = windowPlacement[3][1]
        self.x                  = windowPlacement[4][0]
        self.y                  = windowPlacement[4][1]
        self.w                  = windowPlacement[4][2] - self.x
        self.h                  = windowPlacement[4][3] - self.y

    def toWindowPlacement(self):
        rcToMax = 0
        if self.restoreToMaximized:
            rcToMax = WPF_RESTORETOMAXIMIZED
        windowPlacement = (
                            rcToMax,
                            self.showCmd,
                            ( self.minX, self.minY ),
                            ( self.maxX, self.maxY ),
                            ( self.x, self.y, self.x + self.w, self.y + self.h ),
                            )
        return windowPlacement


class Window:
    "Manipulates a window"

    # ------------------------------------------------------------------------
    # Operators

    def __init__(self, hWnd):
        self.pause = None

        # Window handle
        self.hWnd = hWnd
        if not self.isValid():
            raise Exception, "Invalid window handle"

        # Fake keyboard state
        self.Ctrl       = False
        self.Shift      = False
        self.Alt        = False

        # Fake mouse state
        self.MousePos   = self.fromScreen( * GetCursorPos() )
        self.Left       = False
        self.Middle     = False
        self.Right      = False
        #self.LeftX      = False
        #self.RightX     = False

    def __eq__(self, data):
        return self.hWnd == data.hWnd

    def __repr__(self):
        objid   = id(self)
        handle  = self.hWnd
        caption = self.getText()
        pos     = self.getPosition()
        x       = pos.x
        y       = pos.y
        w       = pos.w
        h       = pos.h
        mx, my  = self.MousePos

        state = "Unknown"
        if pos.showCmd in [ SW_SHOWNORMAL, SW_SHOW, SW_SHOWDEFAULT, SW_SHOWNA, SW_SHOWNOACTIVATE ]:
            state = "Normal"
        elif pos.showCmd == SW_RESTORE:
            state = "Restored"
        elif pos.showCmd == SW_SHOWMAXIMIZED:
            state = "Maximized"
        elif pos.showCmd in [ SW_SHOWMINIMIZED, SW_MINIMIZE, SW_FORCEMINIMIZE, SW_SHOWMINNOACTIVE ]:
            state = "Minimized"
        elif pos.showCmd == SW_HIDE:
            state = "Hidden"
        state += " (%x)" % pos.showCmd

        keystate = ''
        if self.Shift:
            keystate += ' Shift'
        if self.Ctrl:
            keystate += ' Ctrl'
        if self.Alt:
            keystate += ' Alt'
        if len(keystate) > 0:
            keystate = keystate[1:]

        mousestate = ''
        if self.Shift:
            mousestate += ' Left'
        if self.Ctrl:
            mousestate += ' Middle'
        if self.Alt:
            mousestate += ' Right'
        if len(mousestate) > 0:
            mousestate = mousestate[1:]

        return """<Window instance at 0x%(objid)0.8x>
|-- Handle:   0x%(handle)0.4x
|-- Caption:  %(caption)r
|-- Position: (%(x)i, %(y)i)
|-- Size:     (%(w)i, %(h)i)
|-- State:    %(state)s
|-- Keyboard: %(keystate)s
\\-- Mouse:    (%(mx)i, %(my)i) %(mousestate)s
"""     % vars()

    # ------------------------------------------------------------------------
    # Misc

    """
    def destroy(self):
        DestroyWindow(self.hWnd)
        self.hWnd = 0
    """

    def getHandle(self):
        "Returns the window handle to be manually used in API calls"
        return self.hWnd

    def getParent(self):
        return Window( GetParentWindow(self.hWnd) )

    def getChildren(self):
        return Children( self )

    def getChildAt(self, x, y):
        return ChildWindowFromPoint( self.hWnd, (x, y) )

    """
    def getSiblings(self):
        return ThreadWindows( GetWindowThreadProcessId(self.hWnd) )
    """

    def sendMessage(self, uMsg, wParam, lParam, pause = False):
        "Sends a message to the window"
        wParam = long(wParam)
        lParam = long(lParam)
        wParam = struct.pack('<L', wParam)
        lParam = struct.pack('<L', lParam)
        wParam = struct.unpack('<l', wParam)[0]
        lParam = struct.unpack('<l', lParam)[0]
        SendMessage(self.hWnd, uMsg, wParam, lParam)
        if pause and self.pause:
            time.sleep(self.pause)

    def postMessage(self, uMsg, wParam, lParam, pause = False):
        "Posts a message to the window queue"
        PostMessage(self.hWnd, uMsg, wParam, lParam)
        if pause and self.pause:
            time.sleep(self.pause)

    # ------------------------------------------------------------------------
    # State

    def isValid(self):
        "Determines if the window handle is still valid"
        return IsWindow(self.hWnd) == TRUE

    def isVisible(self):
        "Determines if the window is in a visible state"
        return IsWindowVisible(self.hWnd) == TRUE

    def isMaximized(self):
        "Determines if the window is maximized"
        #return IsZoomed(self.hWnd) == TRUE
        return self.getPosition().showCmd == SW_SHOWMAXIMIZED

    def isMinimized(self):
        "Determines if the window is minimized"
        return IsIconic(self.hWnd) == TRUE

    def isChild(self):
        return IsChild(self.hWnd) == TRUE

    isZoomed = isMaximized
    isIconic = isMinimized

    # ------------------------------------------------------------------------
    # Caption

    def getText(self):
        "Gets the window caption or text"
        return GetWindowText(self.hWnd)

    def setText(self, text = ''):
        "Sets the window caption or text"
        SetWindowText(self.hWnd, text)

    # ------------------------------------------------------------------------
    # Position

    def fromScreen(self, x, y):
        "Translates screen coordinates to window coordinates"
        #return MapWindowPoints(HWND_DESKTOP, self.hWnd, (x, y))
        return ScreenToClient(self.hWnd, (x, y))

    def toScreen(self, x, y):
        "Translates window coordinates to screen coordinates"
        #return MapWindowPoints(self.hWnd, HWND_DESKTOP, (x, y))
        return ClientToScreen(self.hWnd, (x, y))

    """
    def fromWindow(self, win):
        "Translates coordinates from another window into this one"
        return MapWindowPoints(win,hWnd, self.hWnd, (x, y))

    def toWindow(self, win):
        "Translates coordinates from this window into another one"
        return MapWindowPoints(self,hWnd, win.hWnd, (x, y))
    """

    def getPosition(self):
        "Gets the window placement on desktop"
        return Position( GetWindowPlacement(self.hWnd) )

    def setPosition(self, pos):
        "Sets the window placement on desktop"
        SetWindowPlacement(self.hWnd, pos.toWindowPlacement())

    def minimize(self):
        "Minimizes the window"
        #ShowWindow(self.hWnd, SW_MINIMIZE)
        ShowWindow(self.hWnd, SW_FORCEMINIMIZE)

    def maximize(self):
        "Maximizes the window"
        ShowWindow(self.hWnd, SW_MAXIMIZE)

    def restore(self):
        "Restores the window"
        ShowWindow(self.hWnd, SW_RESTORE)

    def hide(self):
        "Hides the window"
        ShowWindow(self.hWnd, SW_HIDE)

    def show(self):
        "Shows the window"
        ShowWindow(self.hWnd, SW_SHOW)

    def close(self):
        self.sendMessage(WM_SYSCOMMAND, SC_CLOSE, 0)

    def bring(self):
        SetForegroundWindow(self.hWnd)

    def move(self, x = None, y = None, w = None, h = None, repaint = True):
        "Moves and/or resizes the window"
        if x is None or y is None or w is None or h is None:
            pos = self.getPosition()
            if x is None:
                x = pos.x
            if y is None:
                y = pos.y
            if w is None:
                w = pos.w
            if h is None:
                h = pos.h
        if repaint:
            repaint = TRUE
        else:
            repaint = FALSE
        MoveWindow(self.hWnd, x, y, w, h, repaint)

    # ------------------------------------------------------------------------
    # Keyboard input

    def enable(self):
        EnableWindow(self.hWnd, TRUE)

    def disable(self):
        EnableWindow(self.hWnd, FALSE)

    def isEnabled(self):
        return IsWindowEnabled(self.hWnd)

    def pressShift(self):
        "Presses the shift key"
        self.Shift = True
        self.keyDown(VK_SHIFT)

    def releaseShift(self):
        "Releases the shift key"
        self.Shift = False
        self.keyUp(VK_SHIFT)

    def pressCtrl(self):
        "Presses the ctrl key"
        self.Ctrl = True
        self.keyDown(VK_CONTROL)

    def releaseCtrl(self):
        "Releases the ctrl key"
        self.Ctrl = False
        self.keyUp(VK_CONTROL)

    def pressAlt(self):
        "Presses the alt key"
        self.Alt = True
        self.keyDown(VK_ALT)

    def releaseAlt(self):
        "Releases the alt key"
        self.Alt = False
        self.keyUp(VK_ALT)

    def keyDown(self, key):
        "Presses a key"
        self.sendMessage(WM_KEYDOWN, key, 0x00000000)

    def keyUp(self, key):
        "Releases a key"
        self.sendMessage(WM_KEYUP,   key, 0x80000000)

    def hitKey(self, key):
        self.keyDown(key)
        self.keyUp(key)

    def typeText(self, text):
        "Types an ASCII text on the window"
        for c in text:
            self.hitKey( VkKeyScan(c) )

    def sendCharText(self, text):
        "Sends an ASCII text to the window using WM_CHAR"
        for c in text:
            self.sendMessage(WM_CHAR, ord(c), 0)

    # ------------------------------------------------------------------------
    # Mouse input

    def __setCursorPos(self, x, y):
        if x is None:
            x = self.MousePos[0]
        if y is None:
            y = self.MousePos[1]
        self.MousePos = (x, y)
        return (x, y)

    def __sendMouseMsg(self, uMsg):
        wParam = 0
        if self.Ctrl:
            wParam = wParam | MK_CTRL
        if self.Shift:
            wParam = wParam | MK_SHIFT
        if self.Left:
            wParam = wParam | MK_LBUTTON
        if self.Middle:
            wParam = wParam | MK_MBUTTON
        if self.Right:
            wParam = wParam | MK_RBUTTON
        #if self.LeftX:
        #    wParam = wParam | MK_XBUTTON1
        #if self.RightX:
        #    wParam = wParam | MK_XBUTTON2
        lParam = (self.MousePos[0] & 0xFFFF) + ((self.MousePos[1] & 0xFFFF ) << 16)
        self.sendMessage(uMsg, wParam, lParam)

    def hover(self, trace = [ (None, None) ]):
        "Moves the mouse to the specified coordinates in sequence"
        for (x, y) in trace:
            self.mouseMove(x, y)

    def mouseMove(self, x = None, y = None):
        "Moves the mouse to the specified window coordinates"
        self.__setCursorPos(x, y)
        self.__sendMouseMsg(WM_MOUSEMOVE)

    def leftButtonDown(self, x = None, y = None):
        "Presses the left mouse button on the specified window coordinates"
        self.__setCursorPos(x, y)
        self.__sendMouseMsg(WM_LBUTTONDOWN)
        self.Left = True

    def leftButtonUp(self, x = None, y = None):
        "Releases the left mouse button on the specified window coordinates"
        self.__setCursorPos(x, y)
        self.__sendMouseMsg(WM_LBUTTONUP)
        self.Left = False

    def leftClick(self, x = None, y = None):
        "Clicks the left mouse button on the specified window coordinates"
        self.__setCursorPos(x, y)
        self.__sendMouseMsg(WM_LBUTTONDOWN)
        self.Left = True
        self.__sendMouseMsg(WM_LBUTTONUP)
        self.Left = False

    def leftDoubleClick(self, x = None, y = None):
        "Doubleclicks the left mouse button on the specified window coordinates"
        self.leftClick(x, y)
        self.__sendMouseMsg(WM_LBUTTONDBLCLK)
        self.Left = True
        self.__sendMouseMsg(WM_LBUTTONUP)
        self.Left = False

    def leftDrag(self, xSource = None, ySource = None, xDest = None, yDest = None):
        "Drags the left mouse button over the specified window coordinates"
        self.leftButtonDown(xSource, ySource)
        self.mouseMove(xSource, ySource)
        self.mouseMove(xDest, yDest)
        self.leftButtonUp(xDest, yDest)

    def middleButtonDown(self, x = None, y = None):
        "Presses the middle mouse button on the specified window coordinates"
        self.__setCursorPos(x, y)
        self.__sendMouseMsg(WM_MBUTTONDOWN)
        self.Middle = True

    def middleButtonUp(self, x = None, y = None):
        "Releases the middle mouse button on the specified window coordinates"
        self.__setCursorPos(x, y)
        self.__sendMouseMsg(WM_MBUTTONUP)
        self.Middle = False

    def middleClick(self, x = None, y = None):
        "Clicks the middle mouse button on the specified window coordinates"
        self.__setCursorPos(x, y)
        self.__sendMouseMsg(WM_MBUTTONDOWN)
        self.Middle = True
        self.__sendMouseMsg(WM_MBUTTONUP)
        self.Middle = False

    def middleDoubleClick(self, x = None, y = None):
        "Doubleclicks the middle mouse button on the specified window coordinates"
        self.middleClick(x, y)
        self.__sendMouseMsg(WM_MBUTTONDBLCLK)
        self.Middle = True
        self.__sendMouseMsg(WM_MBUTTONUP)
        self.Middle = False

    def middleDrag(self, xSource = None, ySource = None, xDest = None, yDest = None):
        "Drags the middle mouse button over the specified window coordinates"
        self.middleButtonDown(xSource, ySource)
        self.mouseMove(xSource, ySource)
        self.mouseMove(xDest, yDest)
        self.middleButtonUp(xDest, yDest)

    def rightButtonDown(self, x = None, y = None):
        "Presses the right mouse button on the specified window coordinates"
        self.__setCursorPos(x, y)
        self.__sendMouseMsg(WM_RBUTTONDOWN)
        self.Right = True

    def rightButtonUp(self, x = None, y = None):
        "Releases the right mouse button on the specified window coordinates"
        self.__setCursorPos(x, y)
        self.__sendMouseMsg(WM_RBUTTONUP)
        self.Right = False

    def rightClick(self, x = None, y = None):
        "Clicks the right mouse button on the specified window coordinates"
        self.__setCursorPos(x, y)
        self.__sendMouseMsg(WM_RBUTTONDOWN)
        self.Right = True
        self.__sendMouseMsg(WM_RBUTTONUP)
        self.Right = False

    def rightDoubleClick(self, x = None, y = None):
        "Doubleclicks the right mouse button on the specified window coordinates"
        self.rightClick(x, y)
        self.__sendMouseMsg(WM_RBUTTONDBLCLK)
        self.Right = True
        self.__sendMouseMsg(WM_RBUTTONUP)
        self.Right = False

    def rightDrag(self, xSource = None, ySource = None, xDest = None, yDest = None):
        "Drags the right mouse button over the specified window coordinates"
        self.rightButtonDown(xSource, ySource)
        self.mouseMove(xSource, ySource)
        self.mouseMove(xDest, yDest)
        self.rightButtonUp(xDest, yDest)


class Enumerate:
    "Base class for window enumeration"

    def __wrap(self, data):
        if hasattr(data, '__class__') and data.__class__ == Window:
            return data
        else:
            return Window(data)

    def __init__(self, wl = []):
        self.__windowList = []
        for w in wl:
            self.append(w)

    def __iter__(self):
        return self.__windowList.__iter__()

    def __len__(self):
        return len(self.__windowList)

    def __getitem__(self, index):
        return self.__windowList[index]

    def __setitem__(self, index, data):
        data = self.__wrap(data)
        self.__windowList[index] = data

    def __repr__(self):
        t = ''
        for w in self.__windowList:
            t += '\n' + repr(w)
        if len(t) > 0:
            t = t[1:]
        return t

    def __contains__(self, data):
        data = self.__wrap(data)
        for w in self.__windowList:
            if w.hWnd == data.hWnd:
                return True
        return False

    def append(self, data):
        data = self.__wrap(data)
        if not data in self:
            self.__windowList.append(data)

    def find(self, caption):
        for w in self:
            if w.getText() == caption:
                return w
        raise Exception, "No windows found with caption %r" % caption

    def remove(self, data):
        data = self.__wrap(data)
        for w in self:
            if w == data:
                self.__windowList.remove(w)
                return


class TopLevel(Enumerate):
    """
    Enumerates top-level windows in the current desktop.
    Optionally you can specify a caption to look for.
    Search can be case-insensitive and accept partial text matches.
    """

    def __init__(self, caption = None, strictMatch = True, caseSensitive = True):
        Enumerate.__init__(self)

        def EnumWindowProc(hWnd, lParam):
            (self, caption, strictMatch, caseSensitive) = lParam
            if caption is None:
                self.append(hWnd)
                return
            t = GetWindowText(hWnd)
            if not caseSensitive:
                t = t.lower()
            if strictMatch:
                if t == caption:
                    self.append(hWnd)
                    return
            else:
                if t.find(caption) != -1:
                    self.append(hWnd)
                    return
            return

        if not caseSensitive:
            caption = caption.lower()

        lParam = (self, caption, strictMatch, caseSensitive)
        EnumWindows(EnumWindowProc, lParam)


class Children(Enumerate):
    "Enumerates child windows of a given window."

    def __init__(self, win = None):
        Enumerate.__init__(self)

        if win is None:
            win = GetDesktopWindow()

        def EnumChildWindowProc(hWnd, self):
            self.append(hWnd)

        EnumChildWindows(win.hWnd, EnumChildWindowProc, self)


class ThreadWindows(Enumerate):
    "Enumerates windows managed by a given thread."

    def __init__(self, tid):
        Enumerate.__init__(self)

        def EnumThreadWindowProc(hWnd, self):
            self.append(hWnd)

        EnumThreadWindows(tid, EnumThreadWindowProc, self)


def WindowAt(x, y):
    "Returns the window at the specified screen coordinates."
    return Window( WindowFromPoint(x, y) )

def Desktop():
    "Returns the current desktop window."
    return Window( GetDesktopWindow() )

def Foreground():
    "Returns the foreground window."
    return Window( GetForegroundWindow() )
