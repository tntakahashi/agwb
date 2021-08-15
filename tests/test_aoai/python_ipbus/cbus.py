#!/usr/bin/python3
# -*- coding: utf-8 -*-

def bus_write(adr,dana):
    cmd="W"+("%8.8x" % adr)+","+("%8.8x" % dana)+"\n"
    wrpip.write(cmd)
    wrpip.flush()
    s=rdpip.readline()
    if s.strip()=="ACK":
       return
    else:
       raise Exception("Wrong status returned:"+s.strip())
def bus_read(adr):
    cmd="R"+("%8.8x" % adr)+"\n"
    wrpip.write(cmd)
    wrpip.flush()
    s=rdpip.readline()
    if s.strip()=="ERR":
       print ("Error status returned")
       return 0xa5a5a5
    return eval("0x"+s)

def bus_delay(time_ns):
    cmd="T"+("%8.8x" % time_ns)+"\n"
    wrpip.write(cmd)
    wrpip.flush()
print("Python controller ready. Start the simulation!\n")
wrpip=open("/tmp/wrpipe","w")
rdpip=open("/tmp/rdpipe","r")

import xml.etree.ElementTree as et
class cbus_obj(object):
  def __init__(self,adr,perm,mask):
    self.adr=adr
    self.can_read=False
    if perm.find("r")>=0:
       self.can_read=True
    self.can_write=False
    if perm.find("w")>=0:
       self.can_write=True
    #Now analyze mask
    if mask==0:
       self.mask = mask
    else:
       self.mask = mask
       #Find shift
       shift=0;
       while mask & 1 == 0:
          mask >>= 1
          shift+=1
       self.shift = shift
  def write(self,value):
      if not self.can_write:
         raise Exception("I can't write to this object")
      if self.mask==0:
         return bus_write(self.adr,value)
      else:
         prev=bus_read(self.adr)
         new_val=value << self.shift
         if (new_val & self.mask) != new_val:
            raise Exception("Attempt to write outside the mask!")
         prev |= self.mask
         prev ^= self.mask
         prev |= new_val
         return bus_write(self.adr, prev)
         
  def read(self):
      if not self.can_read:
         raise Exception("I can't read this object")
      if self.mask==0:
         return bus_read(self.adr)
      else:
         val = bus_read(self.adr)
         val &= self.mask
         val >>= self.shift
      return val

def cbus_read_nodes(addr_directory,address_table_file,base_name="",base_addr=0,nodes={}):
    #If address_table_file starts with "file://", remove it, and add addr_directory
    furl="file://"
    if address_table_file.find(furl)==0:
       address_table_file=addr_directory+"/"+address_table_file.replace(furl,"")
    plik1=et.ElementTree(file=address_table_file)
    print("Reading file: "+address_table_file)
    #Take the root element
    er=plik1.getroot()
    #It should be "node"
    if er.tag != "node":
        raise Exception("Wrong type of the root element!")
    #Scan child nodes
    for el in er.findall("node"):
        print(el.tag)
        print(el.attrib)
        if base_name != "":
            name = base_name+"."
        else:
            name = ""
        name += el.attrib['id']
        adr = base_addr+int(el.attrib['address'],16)
        if 'module' in el.attrib:
            #This is a nested module
            cbus_read_nodes(addr_directory,el.get('module'),name,adr,nodes)
        else:
          # This is a register
          perm = el.attrib['permission']
          mask = int(el.get('mask','0x0'),16)
          # Now we need to check if there are bitfields inside...
          for bf in el.findall("node"):
             mask = int(bf.get('mask','0x0'),16)
             bfname=name+"."+bf.get('id')
             nodes[bfname]=cbus_obj(adr,perm,mask)
          nodes[name]=cbus_obj(adr,perm,mask)
    return nodes

