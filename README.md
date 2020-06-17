# AJAX-instrument-control: towards controlling (scientific) instruments using a web browser via a (Raspberry Pi) server.

## Introduction

This is an example of how one might remotely control a scientific instrument using a web browser. The instrument would be physically connected (USB, RS232... GPIB, why not?) to a computer that controls it. The computer also runs a web server that provides a way for the web browser client to connect to it. This example is drawn from a small project, in which the 'instrument' was a (Raspberry Pi) camera controlled by a Raspberry Pi computer.

The remote client computer only needs to have a compatible web browser. The server computer (e.g. the aforementioned Raspberry Pi) runs Python and serves an HTML page to the client web browser. This HTML page contains AJAX-style Javascript. In this context, AJAX means [AJAX](https://en.wikipedia.org/wiki/Ajax_(programming)), not [AJAX!](https://www.youtube.com/watch?v=_uyK9mGAFyo)

Documentation is minimal. The code is relatively self-explanatory. It is mainly intended to demonstrate the idea. All the basic functionality for remote control and read-out is there: changing the state of the instrument (setting parameters, triggering acquisition) and transferring recorded data (e.g. image, spectrum) to the client for analysis.

## Warning!

No guarantees whatsoever. Use at your own risk.

## Usage

All files from this repository are to be copied onto the instrument server (e.g. Raspberry Pi connected to the instrument). Carefully configure and adapt the ``roboserv.py`` script for your purpose by editing the source code. On the server, run:

```
python3 roboserv.py
```

and connect your browser to ``localhost:8080`` or to the IP address/port you configured.

## Installation

All the files in the repository should go on the server side, in one and the same directory, from which ``roboserv.py`` is run.

**Note** In the present version, a writable directory called ``/ramdisk`` is required in the root of your filesystem (mount point of the RAM-disk). This location can be changed in the ``roboserv.py`` code. Instructions for setting up the RAM-disk can be found in the ``roboserv.py`` code. If you just run the script "out of the box", it will not work: it needs to be tailored to the specific system you run it on.

On the client side, all that is needed is a compatible web browser software (most recent browsers will work; Firefox recommended).


## Some particularities

- In the Python script, the instrument is represented by a singleton class. A singleton class can be instantiated several times in a script, but the different instances will always connect to one and the same object, which will manage the instrument control. If you have several instruments to control, you will create a singleton class for each instrument. The instrument is initialized, the first time the singleton is instantiated by the script (so do that at the beginning of the script).
- In the example, we have a Raspberry Pi camera as the prototype 'instrument'. The images are stored to a RAM-disk (a beautiful concept from 1980s home-computing) in order to ease traffic on the SD card. If you are running Linux (and have sudo privileges), you can easily create a small RAM-disk on your system.


## Related work

The question of communicating with remote instruments over TCP/IP is also addressed by the [Serpy library](https://github.com/ArthurLuciani/serpy) developed by Arthur Luciani. That Python library concerns low-level, potentially very high speed data communication directly at the 'network socket' level. It requires a bit more programming also on the client side, but can reach very high data transfer rates (limited by the Ethernet hardware).


## To do's

- Further structure the code and document the example.
- Add further concrete examples of remote control/read-out of lab instruments.




