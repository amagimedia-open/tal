import sys
from collections import OrderedDict

#----------------------------------------------------------------------------

def is_hex_string(s, expected_len=0, non_zero_value=True):

    fname = "is_hex_string"

    if (expected_len > 0):
        actual_len = len(s)
        if (actual_len != expected_len):
            print(f"{fname}:s={s},exp_len={expected_len},actual_len={l}", file=sys.stderr)
            return False

    try:
        val = int(f"0x{s}", 16)
        if (non_zero_value and val == 0):
            print(f"{fname}:s={s},zero valued", file=sys.stderr)
            return False
    except ValueError:
        print(f"{fname}:s={s},not in hex", file=sys.stderr)
        return False

    return True

#----------------------------------------------------------------------------

def csnv_2_odict(s):

    s = "".join(s.split())
    return OrderedDict((map(lambda x: x.split('='), s.split(','))))

#----------------------------------------------------------------------------

def dict_2_csnv(d):

    return ",".join([ f"{k}={d[k]}" for k in d ])


#----------------------------------------------------------------------------

class UnitTests():

    def __init__(self):
        return

    def tc_1(self):

        s = "a = 100 , b=200, c = 300"
        od = csnv_2_odict(s)
        print(od, file=sys.stderr)

        csnv = dict_2_csnv(od)
        print(csnv, file=sys.stderr)

        # simulating modification of trace-context/tracestate
        od.pop("c", None)
        csnv = dict_2_csnv(od)
        csnv = "c=500," + csnv
        print(csnv, file=sys.stderr)


if __name__ == '__main__':

    ut = UnitTests()
    ut.tc_1()

