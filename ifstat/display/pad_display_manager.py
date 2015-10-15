import curses

class PadDisplayManager(object):
    def __init__(self, ylocation=0, xlocation=0):
        self._ylocation = ylocation
        self._xlocation = xlocation
        self._xoffset = 0
        self._yoffset = 0

    def key(self, key):
        if key == curses.KEY_RIGHT and self._xoffset > 0:
            self._xoffset -= 1
        if key == curses.KEY_LEFT:
            self._xoffset += 1

    def refresh(self, pad, maxy, maxx, ysize, xsize):
        if self._ylocation > maxy:
            return

        smaxrow = self._ylocation + ysize
        if smaxrow > maxy:
            smaxrow = maxy - 1
        
        # Don't let the pad 'run to the left' too much - always display
        # the maximum amount of characters from the screen
        if self._xoffset > xsize or xsize - self._xoffset < maxx:
            self._xoffset = xsize - maxx

        # If the screen is large enough to display the entire pad,
        # reset xoffset, and display the entire pad
        if self._xlocation + xsize <= maxx - 1:
            self._xoffset = 0
            smaxcol = self._xlocation + xsize
        else:
            smaxcol = maxx - 1

        pad.refresh(self._yoffset,
                    self._xoffset,
                    self._ylocation,
                    self._xlocation,
                    smaxrow,
                    smaxcol)
