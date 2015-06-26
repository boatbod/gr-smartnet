#!/usr/bin/env python
""" 
    This program decodes the Motorola SmartNet II trunking protocol from the control channel
    Tune it to the control channel center freq, and it'll spit out the decoded packets.
    In what format? Who knows.

    This program does not include audio output support. It logs channels to disk by talkgroup name. If you don't specify what talkgroups to log, it logs EVERYTHING.
"""

from gnuradio import gr, gru, blks2, optfir, digital
from grc_gnuradio import blks2 as grc_blks2
from gnuradio import audio
from gnuradio import eng_notation
from fsk_demod import fsk_demod
from logging_receiver import logging_receiver
from optparse import OptionParser
from gnuradio.eng_option import eng_option
from gnuradio import smartnet
#from gnuradio.wxgui import slider
#from gnuradio.wxgui import stdgui2, fftsink2, form

#from pkt import *
import time
import gnuradio.gr.gr_threading as _threading
import csv
import os
import sys

class top_block_runner(_threading.Thread):
    def __init__(self, tb):
        _threading.Thread.__init__(self)
        self.setDaemon(1)
        self.tb = tb
        self.done = False
        self.start()

    def run(self):
        self.tb.run()
        self.done = True

class my_top_block(gr.top_block):
    def __init__(self, options, args, queue):
        gr.top_block.__init__(self)

        self.options = options
        self.args = args
        self.rate = int(options.rate)
        
        if options.filename is None and options.udp is None and not options.rtlsdr:
          #UHD source by default
          from gnuradio import uhd
          self.u = uhd.single_usrp_source(options.args, uhd.io_type_t.COMPLEX_FLOAT32, 1)
          time_spec = uhd.time_spec(0.0)
          self.u.set_time_now(time_spec)
        
          #if(options.rx_subdev_spec is None):
          #  options.rx_subdev_spec = ""
          #self.u.set_subdev_spec(options.rx_subdev_spec)
          if not options.antenna is None:
            self.u.set_antenna(options.antenna)
        
          self.u.set_samp_rate(rate)
          self.rate = int(self.u.get_samp_rate()) #retrieve actual
        
          if options.gain is None: #set to halfway
            g = self.u.get_gain_range()
            options.gain = (g.start()+g.stop()) / 2.0
        
          if not(self.tune(options.freq)):
            print "Failed to set initial frequency"
        
          print "Setting gain to %i" % options.gain
          self.u.set_gain(options.gain)
          print "Gain is %i" % self.u.get_gain()
          
        elif options.rtlsdr: #RTLSDR dongle
            import osmosdr
            self.u = osmosdr.source_c(options.args)
            self.u.set_sample_rate(2.4e6) #fixed for RTL dongles
            if not self.u.set_center_freq(options.centerfreq - options.error):
                print "Failed to set initial frequency"
        
            self.u.set_gain_mode(0) #manual gain mode
            if options.gain is None:
                options.gain = 25#34
                
            self.u.set_gain(options.gain)
            print "Gain is %i" % self.u.get_gain()
        
            use_resampler = True
            self.rate=2.4e6
                    
        else:
          if options.filename is not None:
            self.u = gr.file_source(gr.sizeof_gr_complex, options.filename)
          elif options.udp is not None:
            self.u = gr.udp_source(gr.sizeof_gr_complex, "localhost", options.udp)
          else:
            raise Exception("No valid source selected")
        
        
        print "Samples per second is %i" % self.rate
        
        self._syms_per_sec = 3600;
        
        options.audiorate = 11025
        options.rate = self.rate
        
        options.samples_per_second = self.rate #yeah i know it's on the list
        options.syms_per_sec = self._syms_per_sec
        options.gain_mu = 0.01
        options.mu=0.5
        options.omega_relative_limit = 0.3
        options.syms_per_sec = self._syms_per_sec
        options.offset = options.centerfreq - options.freq
        print "Control channel offset: %f" % options.offset
        
        self.demod = fsk_demod(options)
        self.start_correlator = gr.correlate_access_code_tag_bb("10101100",0,"smartnet_preamble") #should mark start of packet #digital.
        self.smartnet_deinterleave = smartnet.deinterleave()
        self.smartnet_crc = smartnet.crc(queue)       
        self.connect(self.u, self.demod)
        self.connect(self.demod, self.start_correlator,  self.smartnet_deinterleave, self.smartnet_crc)

        
    def tune(self, freq):
        result = self.u.set_center_freq(freq)
        return True

def getfreq(chanlist, cmd):
    if chanlist is None: #if no chanlist file, make a guess. there are four extant bandplan schemes, and i believe this one is the most common.
        if cmd < 0x2d0:        
            freq = float(cmd * 0.025 + 851.0125)
        else:
            freq = None
    else: #program your channel listings, get the right freqs.
        if chanlist.get(str(cmd), None) is not None:
            freq = float(chanlist[str(cmd)])
        else:
            freq = None

    return freq

def parsefreq(s, chanlist):
    retfreq = None
    [address, groupflag, command] = s.split(",")
    command = int(command)
    address = int(address) & 0xFFF0
    groupflag = bool(groupflag)

    if chanlist is None:
        if command < 0x2d0:
            retfreq = getfreq(chanlist, command)

    else:
        if chanlist.get(str(command), None) is not None: #if it falls into the channel somewhere
            retfreq = getfreq(chanlist, command)
    return [retfreq, address] # mask so the squelch opens up on the entire group



def main():
    # Create Options Parser:
    parser = OptionParser (option_class=eng_option, conflict_handler="resolve")
    expert_grp = parser.add_option_group("Expert")

    parser.add_option("-f", "--freq", type="eng_float", default=857.422e6,
                        help="set control channel frequency to MHz [default=%default]", metavar="FREQ")
    parser.add_option("-c", "--centerfreq", type="eng_float", default=857e6,
                        help="set center receive frequency to MHz [default=%default]. Set to center of 800MHz band for best results")
    parser.add_option("-g", "--gain", type="int", default=None,
                        help="set RF gain", metavar="dB")
    parser.add_option("-r", "--rate", type="eng_float", default=64e6/18,
                        help="set sample rate [default=%default]")
    parser.add_option("-b", "--bandwidth", type="eng_float", default=3e6,
                        help="set bandwidth of DBS RX frond end [default=%default]")
    parser.add_option("-C", "--chanlistfile", type="string", default="motochan14.csv",
                        help="read in list of Motorola channel frequencies (improves accuracy of frequency decoding) [default=%default]")
    parser.add_option("-E", "--error", type="eng_float", default=0,
                        help="enter an offset error to compensate for USRP clock inaccuracy")
    parser.add_option("-m", "--monitor", type="int", default=None,
                        help="monitor a specific talkgroup")
    parser.add_option("-v", "--volume", type="eng_float", default=3.0,
                        help="set volume gain for audio output [default=%default]")
    parser.add_option("-s", "--squelch", type="eng_float", default=28,
                        help="set audio squelch level (default=%default, play with it)")
    parser.add_option("-L", "--directory", type="string", default="./log",
                        help="choose a directory in which to save log data [default=%default]")
    parser.add_option("-a", "--addr", type="string", default="",
                        help="address options to pass to UHD")
    parser.add_option("-s", "--subdev", type="string",
                        help="UHD subdev spec", default=None)
    parser.add_option("-A", "--antenna", type="string", default=None,
                        help="select Rx Antenna where appropriate")
    parser.add_option("-d","--rtlsdr", action="store_true", default=False,
                        help="Use RTLSDR dongle instead of UHD source")
    parser.add_option("-u","--udp", type="int", default=None,
                        help="Use UDP source on specified port")
    parser.add_option("-D", "--args", type="string",
                        help="arguments to pass to UHD/RTL constructor", default="")
    parser.add_option("-F","--filename", type="string", default=None,
                        help="read data from file instead of USRP")
    #receive_path.add_options(parser, expert_grp)

    (options, args) = parser.parse_args ()

    if len(args) != 0:
        parser.print_help(sys.stderr)
        sys.exit(1)


    if options.chanlistfile is not None:
        clreader=csv.DictReader(open(options.chanlistfile), quotechar='"')
        chanlist={"0": 0}
        for record in clreader:
            chanlist[record['channel']] = record['frequency']
    else:
        chanlist = None

    # build the graph
    queue = gr.msg_queue()
    tb = my_top_block(options, args, queue)

    runner = top_block_runner(tb)

    updaterate = 10 #main loop rate in Hz
    audiologgers = [] #this is the list of active audio sinks.
    rxfound = False #a flag to indicate whether or not an audio sink was found with the correct talkgroup ID; see below


    try:
        while 1:
            if not queue.empty_p():
                msg = queue.delete_head() # Blocking read
                sentence = msg.to_string()
                
                [newfreq, newaddr] = parsefreq(sentence, chanlist)

                monaddr = newaddr & 0xFFF0 #last 8 bits are status flags for a given talkgroup

                if newfreq == options.freq/1e6:
                    newfreq = None #don't log the audio from the trunk itself

                #we have a new frequency assignment. look through the list of audio logger objects and find if any of them have been allocated to it
                rxfound = False

                for rx in audiologgers:

                    #print "Logger info: %i @ %f idle for %fs" % (rx.talkgroup, rx.getfreq(options.centerfreq), rx.timeout()) #TODO: debug

                    #first look through the list to find out if there is a receiver assigned to this talkgroup
                    if rx.talkgroup == monaddr: #here we've got one
                        if newfreq != rx.getfreq(options.centerfreq) and newfreq is not None: #we're on a new channel, though
                            rx.tuneoffset(newfreq, options.centerfreq)
                        
                        rx.unmute() #this should be unnecessary but it does update the timestamp
                        rxfound = True
                        #print "New transmission on TG %i, updating timestamp" % rx.talkgroup

                    else:
                        if rx.getfreq(options.centerfreq) == newfreq: #a different talkgroup, but a new assignment on that freq! time to mute.
                            rx.mute()

                if rxfound is False and newfreq is not None: #no existing receiver for this talkgroup. time to create one.
                    #lock the flowgraph
                    tb.lock()
                    audiologgers.append( logging_receiver(newaddr, options) ) #create it
                    audiologgers[-1].tuneoffset(newfreq, options.centerfreq) #tune it
                    tb.connect(tb.u, audiologgers[-1]) #connect to the flowgraph
                    tb.unlock()
                    audiologgers[-1].unmute() #unmute it

                if newfreq is not None:
                    print "TG %i @ %f, %i active loggers" % (newaddr, newfreq, len(audiologgers))


            else:
                time.sleep(1.0/updaterate)

            for rx in audiologgers:
                if rx.timeout() >= 5.0: #if this receiver has been muted more than 3 seconds
                    rx.close() #close the .wav file that the logger has been writing to
                    tb.lock()
                    tb.disconnect(rx)
                    tb.unlock()
                    audiologgers.remove(rx) #delete the audio logger object from the list

    except KeyboardInterrupt:
        #perform cleanup: time to get out of Dodge
        for rx in audiologgers: #you probably don't need to lock, disconnect, unlock, remove. but you might as well.
            rx.close()
            #tb.lock()
            #tb.disconnect(rx)
            #tb.unlock()
            audiologgers.remove(rx)

        tb.stop()

        runner = None

if __name__ == '__main__':
    main()


