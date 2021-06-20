import datetime
import random
import uuid
import sys

# https://en.wikipedia.org/wiki/Universally_unique_identifier
# https://datatracker.ietf.org/doc/html/rfc4122.html

#----------------------------------------------------------------------------

class TraceContextFnxs():

    @staticmethod
    def hexencode_str(s):
        l = bytearray(s.encode())
        s = "" 
        for i in l:
            s = s + hex(i)[2:]
        return s

#----------------------------------------------------------------------------

class TraceIdGenerator():
    """
    Default implementation for
    https://www.w3.org/TR/trace-context/#trace-id
    """

    def __init__(self):
        return

    def generate(self):
        return uuid.uuid4().hex

#----------------------------------------------------------------------------

class ParentIdGenerator():
    """
    Default implementation for
    https://www.w3.org/TR/trace-context/#parent-id
    """

    def __init__(self):
        return

    def generate(self):

        rand_32 = random.randint(0, 0xffffffff)
        s_r32   = hex(rand_32)[2:]

        seconds_since_epoch = \
            int((datetime.datetime.utcnow() - \
                 datetime.datetime(1970, 1, 1)).total_seconds())
        s_sse = hex(seconds_since_epoch)[2:]

        return f"{s_r32:8}{s_sse:8}"

#----------------------------------------------------------------------------

class TraceContext00Generator():
    """
    Default implementation for
    https://www.w3.org/TR/trace-context version 00
    TODO: use incoming trace context
          bad incoming trace context
    """

    def __init__(self, **kwargs):

        # kwargs parameter names
        # trace_id_gen
        # parent_id_gen

        if "trace_id_gen" in kwargs:
            self.trace_id_gen = kwargs["trace_id_gen"]
        else:
            self.trace_id_gen = TraceIdGenerator()

        if "parent_id_gen" in kwargs:
            self.parent_id_gen = kwargs["parent_id_gen"]
        else:
            self.parent_id_gen = ParentIdGenerator()

        self.trace_id = self.trace_id_gen.generate()

        return

    def generate(self):

        version     = "00"
        trace_id    = self.trace_id
        parent_id   = self.parent_id_gen.generate()
        trace_flags = "01"  # SAMPLED FLAG

        return f"{version}-{trace_id}-{parent_id}-{trace_flags}"

#----------------------------------------------------------------------------

class UnitTests():

    def __init__(self):
        return

    def tc_1(self):
        tc00_g = TraceContext00Generator()
        tc00_1 = tc00_g.generate()
        tc00_2 = tc00_g.generate()
        print(tc00_1, len(tc00_1), file=sys.stderr)
        print(tc00_2, len(tc00_2), file=sys.stderr)


if __name__ == '__main__':

    ut = UnitTests()
    ut.tc_1()

