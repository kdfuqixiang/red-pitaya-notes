#!/usr/bin/env python

# GNU Radio blocks for the Red Pitaya transceiver
# Copyright (C) 2015  Renzo Davoli
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import os
import numpy
import struct
import socket
from gnuradio import gr, blocks

class source(gr.hier_block2):
  '''Red Pitaya Source'''
  def __init__(self, addr, port, freq, rate, corr):
    gr.hier_block2.__init__(
      self,
      name = "red_pitaya_source",
      input_signature = gr.io_signature(0, 0, 0),
      output_signature = gr.io_signature(1, 1, gr.sizeof_gr_complex)
    )
    self.ctrl_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.ctrl_sock.connect((addr, port))
    self.ctrl_sock.send(struct.pack('<I', 0))
    self.data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.data_sock.connect((addr, port))
    self.data_sock.send(struct.pack('<I', 1))
    fd = os.dup(self.data_sock.fileno())
    self.connect(blocks.file_descriptor_source(gr.sizeof_gr_complex, fd), self)
    self.set_freq(freq, corr)
    self.set_rate(rate)

  def set_freq(self, freq, corr):
    self.ctrl_sock.send(struct.pack('<I', 0<<28 | int((1.0 + 1e-6 * corr) * freq)))

  def set_rate(self, rate):
    if rate in source.rates:
      code = source.rates[rate]
      self.ctrl_sock.send(struct.pack('<I', 1<<28 | code))
    else:
      raise ValueError("acceptable sample rates are 20k, 50k, 100k, 250k, 500k")

source.rates={20000:0, 50000:1, 100000:2, 250000:3, 500000:4}

class sink(gr.hier_block2):
  '''Red Pitaya Sink'''
  def __init__(self, addr, port, freq, rate, corr):
    gr.hier_block2.__init__(
      self,
      name = "red_pitaya_sink",
      input_signature = gr.io_signature(1, 1, gr.sizeof_gr_complex),
      output_signature = gr.io_signature(0, 0, 0)
    )
    self.ctrl_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.ctrl_sock.connect((addr, port))
    self.ctrl_sock.send(struct.pack('<I', 0))
    self.data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.data_sock.connect((addr, port))
    self.data_sock.send(struct.pack('<I', 1))
    fd = os.dup(self.data_sock.fileno())
    self.connect(self, blocks.file_descriptor_sink(gr.sizeof_gr_complex, fd))
    self.set_freq(freq, corr)
    self.set_rate(rate)

  def set_freq(self, freq, corr):
    self.ctrl_sock.send(struct.pack('<I', 0<<28 | int((1.0 + 1e-6 * corr) * freq)))

  def set_rate(self, rate):
    if rate in source.rates:
      code = source.rates[rate]
      self.ctrl_sock.send(struct.pack('<I', 1<<28 | code))
    else:
      raise ValueError("acceptable sample rates are 20k, 50k, 100k, 250k, 500k")

  def set_ptt(self, on):
    self.ctrl_sock.send(struct.pack('<I', (2<<28, 3<<28)[on == False]))

sink.rates={20000:0, 50000:1, 100000:2, 250000:3, 500000:4}
