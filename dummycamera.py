#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  dummycamera.py
#
#   A very minimal dummy 'PiCamera' class that can be used
#   with roboserv.py in case no real PiCamera is available.
#
#  by M.H.V. Werts, May 2019
#  
#  

import shutil

IMGSOURCE = './default.jpg'

class PiCamera:
    def capture(self, fp):
        shutil.copy(IMGSOURCE, fp)


# ~ def main(args):
    # ~ return 0

# ~ if __name__ == '__main__':
    # ~ import sys
    # ~ sys.exit(main(sys.argv))

