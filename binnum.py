"""
Binary encoding/decoding of numeric values for Space-Time Analysis of Regional Systems
----------------------------------------------------------------------
AUTHOR(S):  Serge Rey sjrey@users.sourceforge.net
----------------------------------------------------------------------
Copyright (c) 2000-2006  Sergio J. Rey
======================================================================
This source code is licensed under the GNU General Public License,
Version 2.  See the file COPYING for more details.
======================================================================

OVERVIEW:
functions for binary encoding/decoding of numeric values
Based on modification of code by:
Jeff Kunce <kuncej@mail.conservation.state.mo.us>
mocons.lib.utils.binnum.py
jjk  02/03/98  001  from mdcutil.py
jjk  02/13/98  002  add unsigned 2,4 from Intel
jjk  02/19/98  003  add unsigned as Intel 2,4
jjk  11/15/99  004  documentation updates

Equivalent built-in python functions may be available.
If so, I wrote these before they were available, or
before I was aware of them. :-)

def integers_from_char1(int_string):
def integer_from_char1(int_string):
def integers_from_Intel2(int_string):
def integer_from_Intel(int_string):
def integer_from_Intel2(int_string):
def integers_from_Intel4(int_string):
def integer_from_Intel4(int_string):
def unsigned_from_Intel2(int_string):
def unsigned_from_Intel4(int_string):
def unsigned_as_Intel2(uint):
def unsigned_as_Intel4(uint):

*** !!  USE AT YOUR OWN RISK    !! ***
*** !! NO WARRANTIES WHATSOEVER !! ***

"""

def integers_from_char1(int_string):
	# return list of integers decoded from 1-byte-format string
	# jjk  12/08/95
        lst = []
	pos = 0
	while (pos < len(int_string)):
		lst.append(integer_from_char1(int_string[pos]))
		pos = pos + 1
	return(lst)

def integer_from_char1(int_string):
	# return first integer decoded from 1-byte-format string
	# jjk  12/08/95
	return(ord(int_string))

def integers_from_Intel2(int_string):
	# return list of integers decoded from 2-byte-intel-format string
	# jjk  12/08/95
        lst = []
	pos = 2
	while (pos <= len(int_string)):
		lst.append(integer_from_Intel2(int_string[pos-2:pos]))
		pos = pos + 2
	return(lst)

def integer_from_Intel(int_string):
	# return signed integer decoded from n-byte-intel-format string
	# jjk  04/25/96  handles negative #'s
		value = 0
		isNegative = 0
		if (len(int_string) > 0):
			bytes = map(ord,int_string)
			bytes.reverse()
			if (bytes[0] >= 0x80):
				isNegative = 1
				bytes[0] = bytes[0] - 0x80
			for byte in bytes:
				value = (value * 256) + byte
		if isNegative:
			value = -value
		return value

def integer_from_Intel2(int_string):
	# return first integer decoded from 2-byte-intel-format string
	# jjk  04/25/96
		return integer_from_Intel(int_string[:2])

def integers_from_Intel4(int_string):
	# return list of integers decoded from 4-byte-intel-format string
	# jjk  01/11/96
		lst = []
		pos = 0
		while (pos <= len(int_string)):
			lst.append(integer_from_Intel4(int_string[pos:(pos+4)]))
			pos = pos + 4
		return(lst)

def integer_from_Intel4(int_string):
	# return first integer decoded from 4-byte-intel-format string
	# jjk  04/25/96
		return integer_from_Intel(int_string[:4])

def unsigned_from_Intel2(int_string):
	'''return unsigned signed integer decoded from 2-byte-intel-format string
	jjk 11/05/97  from mdcutil.py'''
	return ord(int_string[0]) + (256 * ord(int_string[1]))

def unsigned_from_Intel4(int_string):
	'''return unsigned signed integer decoded from 2-byte-intel-format string
	jjk 11/05/97  from mdcutil.py'''
	return (unsigned_from_Intel2(int_string[:2]) +
		(65536 * unsigned_from_Intel2(int_string[2:])))

def unsigned_as_Intel2(uint):
	'''return 2-byte-intel-format string encoded from unsigned signed integer
	jjk  02/19/98'''
	encInt = int(abs(uint))	#enforce unsingned integer
	hiByte = encInt/256
	loByte = encInt%256
	return(chr(loByte)+chr(hiByte))

def unsigned_as_Intel4(uint):
	'''return 4-byte-intel-format string encoded from unsigned signed integer
	jjk  02/19/98'''
	encInt = int(abs(uint))	#enforce unsingned integer
	hiWord = encInt/65536
	loWord = encInt%65536
	return(unsigned_as_Intel2(loWord)+unsigned_as_Intel2(hiWord))
