/* -*- c++ -*- */

#define SMARTNET_API

%include "gnuradio.i"  // the common stuff

//load generated python docstrings
%include "smartnet_swig_doc.i"

%{
#include "smartnet/crc.h"
#include "smartnet/deinterleave.h"
#include "smartnet/parity.h"
#include "smartnet/parser.h"
#include "smartnet/subchannel_framer.h"
#include "smartnet/wavsink.h"
%}


%include "smartnet/crc.h"
GR_SWIG_BLOCK_MAGIC2(smartnet, crc);
%include "smartnet/deinterleave.h"
GR_SWIG_BLOCK_MAGIC2(smartnet, deinterleave);
%include "smartnet/parity.h"
GR_SWIG_BLOCK_MAGIC2(smartnet, parity);
%include "smartnet/parser.h"
GR_SWIG_BLOCK_MAGIC2(smartnet, parser);
%include "smartnet/subchannel_framer.h"
GR_SWIG_BLOCK_MAGIC2(smartnet, subchannel_framer);
%include "smartnet/wavsink.h"
GR_SWIG_BLOCK_MAGIC2(smartnet, wavsink);
