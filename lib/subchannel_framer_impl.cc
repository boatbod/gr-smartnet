/* -*- c++ -*- */
/* 
 * Copyright 2012 Nick Foster
 * Copyright 2020 Graham Norbury
 * 
 * This is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3, or (at your option)
 * any later version.
 * 
 * This software is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this software; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "subchannel_framer_impl.h"
#include <sstream>
#include <stdio.h>

namespace gr {
    namespace smartnet {

        subchannel_framer::sptr
            subchannel_framer::make()
        {
                return gnuradio::get_initial_sptr
                    (new subchannel_framer_impl());
        }

        /*
         * The private constructor
         */
        subchannel_framer_impl::subchannel_framer_impl()
            : gr::sync_block("subchannel_framer",
                    gr::io_signature::make(1, 1, sizeof(char)),
                    gr::io_signature::make(1, 1, sizeof(char)))
        {
            set_output_multiple(42);
        }

        /*
         * Our virtual destructor.
         */
        subchannel_framer_impl::~subchannel_framer_impl()
        {
        }

        int
            subchannel_framer_impl::work(int noutput_items,
                    gr_vector_const_void_star &input_items,
                    gr_vector_void_star &output_items)
        {
            const char *in = (const char *) input_items[0];
            char *out = (char *) output_items[0];

            //iterate over all output items
            //if you get one with a correlator trigger, if there's 21 more left in the queue, if the 21st one on also has a trigger, then it's good! otherwise clear it cause it's a false flag

            for(int i=0; i < noutput_items; i++) {
                if(in[i] & 0x02) {
                    //if(noutput_items-i >= 21) {
                    //if(in[i+21] & 0x02) {
                    out[i] = in[i];
                    printf("Subchannel frame data: ");
                    for(int q = 0; q < 42; q++) {
                        if(in[i+q-5] & 0x01) printf("1");
                        else printf("0");
                    }
                    printf("\n");
                    //				}
                    //	else out[i] = in[i] & 0x01;
                    //} else return i; //weren't enough to validate it, so go back for more
                } else out[i] = in[i];

            }

            // Tell runtime system how many output items we produced.
            return noutput_items;
        }

    } /* namespace smartnet */
} /* namespace gr */

