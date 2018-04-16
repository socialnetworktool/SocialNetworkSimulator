"""
Reading of database files (dbf) for Space-Time Analysis of Regional Systems
----------------------------------------------------------------------
AUTHOR(S):  Serge Rey sjrey@users.sourceforge.net
----------------------------------------------------------------------
Copyright (c) 2000-2006  Sergio J. Rey
======================================================================
This source code is licensed under the GNU General Public License,
Version 2.  See the file COPYING for more details.
======================================================================

OVERVIEW:

Reads database files.


Based on modification of code by:
Jeff Kunce <kuncej@mail.conservation.state.mo.us>
load dbf file into memory as a DbfLoader object, read file specs and data
mocons.lib.persist.dbfload.py
jjk  11/05/97  001  from MdcDbf.py 005
jjk  11/06/97  002
jjk  12/16/97  003  for CTdataTable ver 010
jjk  02/13/98  004  from CTdbfLoader
jjk  11/15/99  005  documentation updates

Usage:
see doc string for DbfLoader class
also see demo1() function

*** !!  USE AT YOUR OWN RISK    !! ***
*** !! NO WARRANTIES WHATSOEVER !! ***

Jeff Kunce <kuncej@mail.conservation.state.mo.us>
"""

import sys
import string

try:
    import binnum
except ImportError: from mocons.lib.utils import binnum

class DbfLoader:
    '''loads the contents of a dbf file into memory
    After successful load, the following info is available:
        self.fileName
        self.version
        self.lastUpdate    ('mm/dd/yy')
        self.recordCount
        self.headerLength
        self.recordLength
        self.fieldDefs      (list of DbfFieldDef objects)
        self.fieldNames()
        self.fieldInfo()    (list of (name, type, length, decimalCount))
        self.allRecords
        self.recordStatus
        self.fieldNames()
        self.liveRecords()
        self.deletedRecords()
    jjk  02/13/98'''

    def __init__(self, dbfFileName=''):
        '''public: initialize the receiver
        jjk  02/13/98'''
        if (dbfFileName): self.loadDbfFileName(dbfFileName)

    def loadDbfFileName(self, dbfFileName):
        '''public: load the specified dbf file into the receiver
        jjk  02/13/98'''
        dbfs = open(dbfFileName, 'rb')
        self.loadDbfFile(dbfs)
        dbfs.close()
        self.fileName = dbfFileName
        self.filename = self.fileName

    def loadDbfFile(self, dbfFile):
        '''public: load data from open dbf file
        jjk  02/13/98'''
        self.fileName = ''
        self.readHeaderData(dbfFile)
        self.loadRecordData(dbfFile)

    def readHeaderData(self, dbfs):
        '''private: read and dcode dbf header data from binary input stream
        jjk  11/05/97'''
        self.version = ord(dbfs.read(1))
        year = ord(dbfs.read(1))
        month = ord(dbfs.read(1))
        day = ord(dbfs.read(1))
        self.lastUpdate = "%2d/%2d/%2d" % (month, day, year)
        self.recordCount = binnum.unsigned_from_Intel4(dbfs.read(4))
        self.headerLength = binnum.unsigned_from_Intel2(dbfs.read(2))
        self.recordLength = binnum.unsigned_from_Intel2(dbfs.read(2))
        reserved = dbfs.read(20)
        self.fieldDefs = []
        fieldCount = (self.headerLength - 33) / 32
        start = 1 #byte 0 is delete flag
        for fn in range(fieldCount):
            fd = DbfFieldDef()
            fd.readFieldDef(dbfs, start)
            self.fieldDefs.append(fd)
            start = fd.end
        skip = dbfs.read(1)

    def loadRecordData(self, dbfs):
        '''private: read and dcode dbf record data from binary input stream.
        load data into data table.
        jjk  02/13/98'''
        self.allRecords = []
        self.recordStatus = []
        for rn in range(self.recordCount):
            rawrec = dbfs.read(self.recordLength)
            record = []
            for fd in self.fieldDefs:
                record.append(fd.decodeValue(rawrec))
            self.allRecords.append(record)
            self.recordStatus.append(rawrec[0]==' ')

    def fieldNames(self):
        '''Public: answer a list of the receiver's field names.
        jjk  11/06/97'''
        return(map(lambda x: x.name, self.fieldDefs))

    def fieldTypes(self):
        '''Public: answer a list of the receiver's field names.
        jjk  11/06/97'''
        return(map(lambda x: x.type, self.fieldDefs))


    def fieldInfo(self):
        '''Public: answer a list of the receiver's field info.
            for each: (name, type, length, decimalCount)
        jjk  11/06/97'''
        fi = []
        for fd in self.fieldDefs:
            fi.append(fd.fieldInfo())
        return(fi)

    def liveRecords(self):
        '''Public: answer a list undeleted records from the file
        jjk  02/13/98'''
        liveRecs = []
        for rn in range(len(self.recordStatus)):
            if (self.recordStatus[rn]):
                liveRecs.append(self.allRecords[rn])
        return(liveRecs)

    def deletedRecords(self):
        '''Public: answer a list deleted records from the file
        jjk  02/13/98'''
        delRecs = []
        for rn in range(len(self.recordStatus)):
            if (not self.recordStatus[rn]):
                delRecs.append(self.allRecords[rn])
        return(delRecs)

    def reportOn(self, outs=sys.stdout):
        '''Public: report info about the receiver
        jjk  02/13/98'''
        outs.write('DbfLoader   file: %s\n'%self.fileName)
        outs.write('  version: %d  last update: %s\n'%(self.version,self.lastUpdate))
        outs.write('  hdrlen: %d  reclen: %d  reccnt: %d\n'%(self.headerLength,self.recordLength,self.recordCount))
        outs.write('  FIELDS:\n')
        for fi in self.fieldInfo():
            outs.write('     %12s %2s %4d %4d\n'%fi)
        outs.write('  deleted records: %d\n\n'%len(self.deletedRecords()))

    def get_field_names(self):
        """Return a list of field names in the order of the dbf."""
        return self.fieldNames()

    def get_field_types(self):
        """Return a list of field names in the order of the dbf."""
        return self.fieldTypes()


    def summary(self):
        fields = self.get_field_names()
        nfields = len(fields)
        n = self.recordCount
        print "="*23   # ========================== "=" == 23
        so="DBF name: %s"%self.filename
        so+="\nNumber of records: %d"%n
        so+="\nNumber of fields: %d"%nfields
        print so
        #print "all records: ", self.allRecords
        fields = self.get_field_names()
        types = self.get_field_types()
        maxf = max([len(field) for field in fields])
        for field,type in zip(fields,types):
            print "%21s %s"%(field,type)

        print "="*23

    def returnAllrecords(self):
        if self.allRecords != None:
            return self.allRecords
        else:
            print "No records inside!"

    def table2list(self):
        """returns entire table in a list of n lists, where n is the number of
        records in the dbf."""
        return self.allRecords



class DbfFieldDef:

    def readFieldDef(self, dbfs, start):
        '''read and dcode dbf field definition from binary input stream
        jjk  11/05/97'''
        self.name = dbfs.read(11)
        while (self.name[-1:] == '\000'): self.name = self.name[:-1]
        self.type = dbfs.read(1)
        dataAddress = binnum.unsigned_from_Intel4(dbfs.read(4))
        self.length = ord(dbfs.read(1))
        self.start = start
        self.end = start + self.length
        self.decimalCount = ord(dbfs.read(1))
        reserved = dbfs.read(14)

    def fieldInfo(self):
        '''answer basic info about the receiver
        jjk  02/13/98'''
        return((self.name, self.type, self.length, self.decimalCount))

    def decodeValue(self, rawrec):
        '''decode and answer a field value from rawrec
        jjk  11/05/97'''
        rawval = rawrec[self.start:self.end]
        if (self.type == 'C'):         #string
            while (rawval[-1:] == ' '): rawval = rawval[:-1]
            return rawval
        if (self.type == 'D'):         #date 'yyyymmdd'
            return rawval
        if (self.type == 'N' or self.type == "F" or self.type == "L"):         #numeric
            if (self.decimalCount == 0):
                rawval = rawval.strip()
                if (rawval==''): return(0)
                try:
                    return(int(rawval))
                except ValueError:
                    return(long(rawval))
            else:
                return float(rawval)
        return(rawval)



def demo1():
    dl1 = DbfLoader('county.dbf')
    dl1.reportOn()
    print 'sample records:'
    for i1 in range(min(3,dl1.recordCount)):
        print dl1.allRecords[i1]

if (__name__=='__main__'):
    import pdb

    d1 = DbfLoader('data/geoda/nat.dbf')
