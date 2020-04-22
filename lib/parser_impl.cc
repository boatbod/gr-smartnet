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
#include "parser_impl.h"
#include <smartnet/types.h>
#include <ctype.h>
#include <iostream>
#include <ostream>
#include <iomanip>
#include <gnuradio/msg_queue.h>

namespace gr {
    namespace smartnet {

        parser::sptr
            parser::make(gr::msg_queue::sptr queue)
        {
                return gnuradio::get_initial_sptr
                    (new parser_impl(queue));
        }

        /*
         * The private constructor
         */
        parser_impl::parser_impl(gr::msg_queue::sptr queue)
            : gr::sync_block("parser",
                    gr::io_signature::make(1, 1, sizeof(struct smartnet_packet)),
                    gr::io_signature::make(0, 0, 0))
        {
            //	set_output_multiple(2);
        }

        /*
         * Our virtual destructor.
         */
        parser_impl::~parser_impl()
        {
        }

        int
            parser_impl::work(int noutput_items,
                    gr_vector_const_void_star &input_items,
                    gr_vector_void_star &output_items)
        {
            const struct smartnet_packet *in = (const struct smartnet_packet *) input_items[0];

            d_payload.str("");
            int i = 0;

            //	printf("Invoked with %i requested outputs\n", noutput_items);
            while (i < noutput_items) {
                d_payload.str("");

                d_payload << in[i].address << "," << in[i].groupflag << "," << in[i].command;
                gr::message::sptr msg = gr::message::make_from_string(std::string(d_payload.str()));
                d_queue->handle(msg);

                i++;
            }

            return i; //be sure to let the caller know how many items you've processed
        }

    } /* namespace smartnet */
} /* namespace gr */

