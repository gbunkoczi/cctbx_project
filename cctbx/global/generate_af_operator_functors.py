import sys

from operator_functor_info import *

def write_copyright():
  print \
"""/* Copyright (c) 2001 The Regents of the University of California through
   E.O. Lawrence Berkeley National Laboratory, subject to approval by the
   U.S. Department of Energy. See files COPYRIGHT.txt and
   cctbx/LICENSE.txt for further details.

   Revision history:
     Feb 2002: Created (Ralf W. Grosse-Kunstleve)

   *****************************************************
   THIS IS AN AUTOMATICALLY GENERATED FILE. DO NOT EDIT.
   *****************************************************

   Generated by:
     %s
 */""" % (sys.argv[0],)

def generate_aipbinop_function_objects():
  for op in arithmetic_in_place_binary_ops:
    print """
  template <typename T>
  struct %s : std::binary_function<T, T, T> {
    T& operator()(T& x, const T& y) const { x %s y; return x; }
  };""" % (aipbinop_function_objects[op], op)

def run():
  f = open("operator_functors.h", "w")
  sys.stdout = f
  write_copyright()
  print """
#ifndef CCTBX_ARRAY_FAMILY_OPERATOR_FUNCTORS_H
#define CCTBX_ARRAY_FAMILY_OPERATOR_FUNCTORS_H

#include <functional>

namespace cctbx { namespace vector {"""

  generate_aipbinop_function_objects()

  print """
}} // namespace cctbx::vector

#endif // CCTBX_ARRAY_FAMILY_OPERATOR_FUNCTORS_H"""
  sys.stdout = sys.__stdout__
  f.close()

if (__name__ == "__main__"):
  run()
