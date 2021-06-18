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

def str_2_hex(s):
    l = bytearray(s.encode())
    s = "" 
    for i in l:
        s = s + str(i)

    return int(s)

#----------------------------------------------------------------------------

def id_dict_2_int_list (id_dict):
    l = [ 
          id_dict["gtc_ver"], 
          id_dict["ss_epoch"] 
        ]
    l.append(str_2_hex(id_dict["comp_name"]))
    l.append(str_2_hex(id_dict["comp_csver"]))
    return l

#----------------------------------------------------------------------------

def int_list_2_trace_id (int_list, salt):

    h = Hashids(salt, 32, "0123456789abcdef")
    e = h.encode(*int_list)
    return e

#-------------------------[MAIN]---------------------------------------------

class UnitTests():

    def tc_1(self):

        id_dict = {
            "gtc_ver"    : 9,           # max 1 digit
            "comp_name"  : "FOO",       # max 3 characters
            "comp_csver" : "999999",    # MMmmpp (Major Minor Patch)
            "ss_epoch"   : 2357899999   # Max: Mon Sep 19 17:43:19 IST 2044
        }
        print(id_dict, file=sys.stderr)

        int_list = id_dict_2_int_list (id_dict)
        print(int_list, file=sys.stderr)

        trace_id = int_list_2_trace_id (int_list, "com.amagi.w3c.trace_context")
        print(trace_id, len(trace_id), file=sys.stderr)


if __name__ == '__main__':

    ut = UnitTests()
    ut.tc_1()


