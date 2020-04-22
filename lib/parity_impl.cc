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
#include "parity_impl.h"
#include <gnuradio/tags.h>

#define VERBOSE 1

namespace gr {
    namespace smartnet {

        parity::sptr
            parity::make()
        {
                return gnuradio::get_initial_sptr
                    (new parity_impl());
        }

        /*
         * The private constructor
         */
        parity_impl::parity_impl()
            : gr::block("parity",
                    gr::io_signature::make(1, 1, sizeof(char)),
                    gr::io_signature::make(1, 1, sizeof(char)))
        {
            set_relative_rate(0.5);
            set_output_multiple(38);
        }

        /*
         * Our virtual destructor.
         */
        parity_impl::~parity_impl()
        {
        }

        void
            parity_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
        {
                ninput_items_required[0] = noutput_items * 2;
        }

        int
            parity_impl::general_work (int noutput_items,
                    gr_vector_int &ninput_items,
                    gr_vector_const_void_star &input_items,
                    gr_vector_void_star &output_items)
        {
            const char *in = (const char *) input_items[0];
            char *out = (char *) output_items[0];

            char expected[noutput_items * 2];
            char syndrome[noutput_items * 2];

            //first we calculate the EXPECTED parity bits from the RECEIVED bitstream
            //parity is I[i] ^ I[i-1]
            //since the bitstream is still interleaved with the P bits, we can do this while running
            expected[0] = in[0] & 0x01; //info bit
            expected[1] = in[0] & 0x01; //this is a parity bit, prev bits were 0 so we call x ^ 0 = x
            for(int k = 2; k < noutput_items*2; k+=2) {
                expected[k] = in[k] & 0x01; //info bit
                expected[k+1] = (in[k] & 0x01) ^ (in[k-2] & 0x01); //parity bit
            }

            for(int k = 0; k < noutput_items*2; k++) {
                syndrome[k] = expected[k] ^ (in[k] & 0x01); //calculate the syndrome
                if(VERBOSE) if(syndrome[k]) std::cout << "Bit error at bit " << k << std::endl;
            }

            for(int k = 0; k < noutput_items-1; k++) {
                //now we correct the data using the syndrome: if two consecutive parity bits are flipped, you've got a bad previous bit
                if(syndrome[2*k+1] && syndrome[2*k+3]) {
                    out[k] = (in[2*k] & 0x01) ? 0 : 1; //byte-safe bit flip
                    if(VERBOSE) std::cout << "I just flipped a bit!" << std::endl;
                }
                else out[k] = in[2*k];
            }
            out[noutput_items-1] = in[2*(noutput_items-1)]; //guard bit at the end

            if(VERBOSE) {
                int errors = 0;
                for(int k = 0; k < noutput_items * 2; k++) if(syndrome[k]) errors++;
                if(errors != 0) std::cout << errors << " syndrome errors" << std::endl;
            }

            consume_each(noutput_items*2); //tell gnuradio how many input items we used
            return noutput_items; // Tell runtime system how many output items we produced.
        }

    } /* namespace smartnet */
} /* namespace gr */

