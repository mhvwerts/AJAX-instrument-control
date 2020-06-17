#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  roboserv.py
#
# by M.H.V. Werts, May 2019
#
# CHANGELOG
# 20190512  make it possible to run in dummy mode for development and
#           testing


from http.server import BaseHTTPRequestHandler,HTTPServer
import shutil
import os
import os.path
import datetime

try:
    from picamera import PiCamera
except:
    print("picamera not found. using dummycamera")
    from dummycamera import PiCamera


STORE = '/ramdisk'
IMGBUFLEN = 30
FSTREND = '.jpg'
FSTR = 'img{0:04d}' + FSTREND

PORT = 8080
INDEXHTML = 'server_index.html'
FAVICON = 'favicon.ico'
DEFAULTIMG = 'default.jpg'

# If the ramdisk does not exist (i.e. is not present in /etc/fstab),
# create it in the following way:
#   $ sudo mkdir /ramdisk
#   $ sudo mount -t tmpfs -o size=16m tmpfs /ramdisk



class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        # ~ print('singleton recreation event')
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]



class Logger_singleton(metaclass=Singleton):
    """example/test singleton class
    
    also demonstrates how one could have several instruments
    being controlled using the same server: each physical instrument 
    would live in a (singleton) class of its own.
    """
    def __init__(self):
        # ~ print('Logger init event')
        self.N = 1

    def inc(self):
        self.N += 1



class CamPic_singleton(metaclass=Singleton):
    """singleton class for interfacing the Pi camera
    
    make sure that the CamPic singleton is initialized at the very
    start of the program (Gremlin-type advice: 
    "Do not feed after midnight" - "Do not initialize after main()")
    """
    def __init__(self):
        # ~ print('CamPic init event')
        self.PiC = PiCamera()
        self.PiC.vflip = True
        self.PiC.hflip = True
        
        self.lastpic = 'default.jpg'
        self.piclist = []
        self.N = 0
        self.Nhistory = 0

    def takepic(self):
        fimg = FSTR.format(self.N)
        imgfp = os.path.join(STORE,fimg)
        self.PiC.capture(imgfp)
        self.lastpic = fimg
        self.piclist.append(fimg)
        self.Nhistory = 1 # reset 'history' pointer
        self.N += 1
        if (len(self.piclist) > IMGBUFLEN):
            # ~ print('piclist N:',len(self.piclist))
            fimgpop = self.piclist.pop(0)
            # ~ print('popped: ',fimgpop)
            os.remove(os.path.join(STORE,fimgpop))
            # ~ print('piclist N:',len(self.piclist))
            
    def history_bk(self):
        """should return the name of one image farther back in time"""
        # ~ print('Nhistory =',self.Nhistory)
        # ~ print('len piclist=',len(self.piclist))
        if len(self.piclist) < 1:
            fname = self.lastpic
        else:
            if (self.Nhistory < IMGBUFLEN)\
                    and (self.Nhistory < len(self.piclist)):
                self.Nhistory += 1
                fname = self.piclist[-self.Nhistory]
            else:
                fname = self.piclist[-self.Nhistory]
        return fname
    
    def history_fwd(self):
        """should return the name of one image later in time"""
        # ~ print('Nhistory =',self.Nhistory)
        # ~ print('len piclist=',len(self.piclist))
        if (self.Nhistory > 1):
            self.Nhistory -= 1
            fname = self.piclist[-self.Nhistory]
        else:
            self.Nhistory = 1
            fname = self.lastpic
        return fname
            


class myHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.cam = CamPic_singleton()
        super().__init__(*args, **kwargs)

	#Handler for the GET requests
    def do_GET(self):
        if self.path == '/campic':
            self.do_get_picture()
        elif self.path == '/prevpic':
            self.do_history('bk')
        elif self.path == '/nextpic':
            self.do_history('fwd')
        elif self.path == '/datetime':
            self.do_datetime()
        elif self.path == '/favicon.ico':
            self.do_favicon()
        elif self.path == '/':
            self.do_index()
        elif self.path.endswith(FSTREND): 
            # TODO: better implement request style
            #  ../getimg=<filename.jpg> (even without extension)
            fname = self.path[1:]
            self.do_serv_img(fname)
        else:
            self.replyheader()
            msg = "<p>unsupported request</p>"+\
                  "<p>" + self.path + "</p>"
            self.wfile.write(msg.encode('utf-8'))

    def replyheader(self, content='text'):
        self.send_response(200)
        if content=='jpeg':
            self.send_header('Content-type','image/jpeg')
        elif content=='ico':
            self.send_header('Content-type','image/ico')
        else: # always default to text/html 
            self.send_header('Content-type','text/html; charset=utf-8')
        self.end_headers()

    def do_index(self):
        self.replyheader()
        with open(os.path.join(STORE,INDEXHTML),'rb') as f1:
            self.copyfile(f1,self.wfile)

    def do_favicon(self):
        self.replyheader('ico')
        with open(os.path.join(STORE,FAVICON),'rb') as f1:
            self.copyfile(f1,self.wfile)

    def do_serv_img(self, fname):
        self.replyheader('jpeg')
        with open(os.path.join(STORE,fname),'rb') as f1:
            self.copyfile(f1,self.wfile)

    def do_get_picture(self):
        self.cam.takepic()
        self.replyheader() # we are sending the code for displaying 
        # the picture, not the picture itself.
        # Send the html message
        msg1 = '<p>picture: '+self.cam.lastpic+'</p>'
        msg2 = '<p><img src="'+self.cam.lastpic+'" alt="CAM IMAGE"></p>'
        msg = msg1 + msg2
        self.wfile.write(msg.encode('utf-8'))

    def do_history(self, action):
        if action=='fwd':
            fname = self.cam.history_fwd()
        else:
            fname = self.cam.history_bk()
        msg1 = '<p>picture: '+fname+'</p>'
        msg2 = '<p><img src="'+fname+'" alt="CAM HISTORY IMAGE"></p>'
        msg = msg1 + msg2
        self.replyheader() # we are sending the code for displaying 
        # the picture, not the picture itself.
        # Send the html message
        self.wfile.write(msg.encode('utf-8'))


    def do_datetime(self):
        self.replyheader()
        # Send the html message
        msg = "<p>"+str(datetime.datetime.now())+"</p>"
        self.wfile.write(msg.encode('utf-8'))

        
    def copyfile(self, source, outputfile):
        """Copy all data between two file objects.

        The SOURCE argument is a file object open for reading
        (or anything with a read() method) and the DESTINATION
        argument is a file object open for writing (or
        anything with a write() method).

        The only reason for overriding this would be to change
        the block size or perhaps to replace newlines by CRLF
        -- note however that this the default server uses this
        to copy binary data as well.

        """
        shutil.copyfileobj(source, outputfile)





def mainloop(args):
    server = HTTPServer(('', PORT), myHandler)
    print('Started httpserver on port ', PORT)
    #Wait forever for incoming http requests
    server.serve_forever()
    return 0




if __name__ == '__main__':
    #The following  test code demonstrates
    # that Logger_singleton() and CamPic_singleton() are each
    # independent and invididual Singleton objects
    # ~ ax = Logger_singleton()
    # ~ ax.inc()
    # ~ bx = CamPic_singleton()
    # ~ print('logger:',ax.N)
    # ~ print('campic:',bx.N)

    # Initialize hardware device singletons
    # (i.e. claim and open hardware)
    cam = CamPic_singleton()

    # copy files to STORE location (e.g. RAM-disk)
    for fname in [INDEXHTML, FAVICON, DEFAULTIMG]:
        shutil.copy(fname,os.path.join(STORE,fname))

    # run the mainloop
    import sys
    sys.exit(mainloop(sys.argv))
