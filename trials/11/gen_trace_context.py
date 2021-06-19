import datetime
import random
import os.path
import uuid
import sys
from   hashids import Hashids

g_gtc_version = "1"

#----------------------------------------------------------------------------

def get_secs_since_epoch():
    return int((datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds())

#----------------------------------------------------------------------------

def gen_default_id_dict (**kwargs):
    global g_gtc_version

    # kwargs must be composed of none or more of the following
    # comp_name
    # comp_csver # component compressed semantic version
    #
    # see "Generate ids based on timestamp"
    # https://hashids.org/python/#how-does-it-work

    id_dict = {
        "gtc_ver"    : g_gtc_version,
        "comp_name"  : kwargs["comp_name"],
        "comp_csver" : kwargs["comp_csver"],
        "ss_epoch"   : get_secs_since_epoch()
    }

    return id_dict

#----------------------------------------------------------------------------

def str_2_int(s):
    l = bytearray(s.encode())
    s = "" 
    for i in l:
        s = s + str(i)

    return int(s)

#----------------------------------------------------------------------------

def hexencode_str(s):
    l = bytearray(s.encode())
    s = "" 
    for i in l:
        s = s + hex(i)[2:]

    return s

#----------------------------------------------------------------------------

def id_dict_2_int_list (id_dict):
    l = [ 
          #id_dict["gtc_ver"], 
          id_dict["ss_epoch"] 
        ]
    l.append(str_2_int(id_dict["comp_name"]))
    #l.append(id_dict["comp_csver"])
    #TODO: identify a trace tree uniquely
    return l

#----------------------------------------------------------------------------

def int_list_2_trace_id (int_list, salt):
    h = Hashids(salt, 32, "0123456789abcdef")
    e = h.encode(*int_list)
    return e

#----------------------------------------------------------------------------

def int_list_2_trace_id (int_list, salt):
    h = Hashids(salt, 32, "0123456789abcdef")
    e = h.encode(*int_list)
    return e

#----------------------------------------------------------------------------

def id_dict_2_trace_id__1 (id_dict):

    int_list = id_dict_2_int_list (id_dict)
    print(int_list, file=sys.stderr)

    return int_list_2_trace_id (int_list, "com.amagi.w3c.trace_context")

#----------------------------------------------------------------------------

def id_dict_2_trace_id__2 (id_dict):

    hex_out_str = ""

    gtc_ver_str = hex(id_dict["gtc_ver"])[2:]
    print(f"gtc_ver_str = {gtc_ver_str}", file=sys.stderr)
    hex_out_str += gtc_ver_str

    ss_epoch_str = hex(id_dict["ss_epoch"])[2:]
    print(f"ss_epoch_str = {ss_epoch_str}", file=sys.stderr)
    hex_out_str += ss_epoch_str

    comp_name_str = hexencode_str(id_dict["comp_name"])
    print(f"comp_name_str = {comp_name_str}", file=sys.stderr)
    hex_out_str += comp_name_str

    comp_csver_str = id_dict["comp_csver"]
    print(f"comp_csver_str = {comp_csver_str}", file=sys.stderr)
    hex_out_str += comp_csver_str

    return hex_out_str

#-------------------------[MAIN]---------------------------------------------

class UnitTests():

    def __init__(self):
        self.id_dict = {
            "gtc_ver"    : 9,           # max 1 digit
            "ss_epoch"   : 2357899999 * 1000,  # Max: Mon Sep 19 17:43:19 IST 2044
            "comp_name"  : "FOOBOOZOO", # max 3 characters
            "comp_csver" : "999999"     # MMmmpp (Major Minor Patch) in hex !
        }

    def tc_1(self):
        print(self.id_dict, file=sys.stderr)
        trace_id_1 = id_dict_2_trace_id__1 (self.id_dict)
        print(trace_id_1, len(trace_id_1), file=sys.stderr)

    def tc_2(self):
        # Advantages
        # clear encoding. can be decoded visibly.
        #
        # larger gtc_ver value
        # f (> 9)
        #
        # larger ss_epoch value
        # $ printf "%d\n" 0xffffffff
        # 4294967295
        # $ date --date=@4294967295
        # Sun Feb  7 11:58:15 IST 2106
        #
        # larger comp_csver value
        # "FFFFFF"
        #
        # takes up only 21 characters. 11 more available.

        print(self.id_dict, file=sys.stderr)
        trace_id_2 = id_dict_2_trace_id__2 (self.id_dict)
        print(trace_id_2, len(trace_id_2), file=sys.stderr)


if __name__ == '__main__':

    ut = UnitTests()
    ut.tc_1()
    print("#---", file=sys.stderr)
    ut.tc_2()


"""
Sat Jun 19 13:45:42 IST 2021
Sashi
* time since epoch in milliseconds
"""
