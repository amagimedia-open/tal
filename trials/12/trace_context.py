import datetime
import random
import uuid
import sys

# https://en.wikipedia.org/wiki/Universally_unique_identifier
# https://datatracker.ietf.org/doc/html/rfc4122.html

#----------------------------------------------------------------------------

class W3CTC00TraceIdGenerator():
    """
    Default implementation for
    https://www.w3.org/TR/trace-context/#trace-id
    """

    def __init__(self):
        return

    def generate(self):
        return uuid.uuid4().hex

#----------------------------------------------------------------------------

class W3CTC00ParentIdGenerator():
    """
    Default implementation for
    https://www.w3.org/TR/trace-context/#parent-id
    """

    def __init__(self):
        return

    def generate(self):

        rand_32 = random.randint(0, 0xffffffff)
        s_r32   = hex(rand_32)[2:].zfill(8)

        seconds_since_epoch = \
            int((datetime.datetime.utcnow() - \
                 datetime.datetime(1970, 1, 1)).total_seconds())
        s_sse = hex(seconds_since_epoch)[2:].zfill(8)

        return f"{s_r32}{s_sse}"

#----------------------------------------------------------------------------

class W3CTC00Traceparent():

    def __init__(self, trace_id_str, parent_id_str, trace_flags_str):
        self.m_version_str     = "00"
        self.m_trace_id_str    = trace_id_str
        self.m_parent_id_str   = parent_id_str
        self.m_trace_flags_str = trace_flags_str

        self.traceparent = f"{self.m_version_str}-" \
                           f"{self.m_trace_id_str}-" \
                           f"{self.m_parent_id_str}-" \
                           f"{self.m_trace_flags_str}" 

    def __str__(self):
        return self.traceparent

    @property
    def version_str(self):
        return self.m_version_str

    @property
    def trace_id_str(self):
        return self.m_trace_id_str

    @property
    def parent_id_str(self):
        return self.m_parent_id_str

    @property
    def flags_str(self):
        return self.m_trace_flags_str

    @staticmethod
    def parse (tc00_str):
        """
        Returns a 3-tuple
        (parse_status, parse_error_str, W3CTC00Traceparent)
        """

        while True: # just need a 'block'

            fields = tc00_str.split("-")
            n = len(fields)
            if (n != 4):
                error_str =  "w3c/tc/00/tp num. fields mismatch. " +\
                            f"found {n}. expected 4."
                ret = (False, error_str, None)
                break

            version_str = fields[0]
            if (version_str != "00"): 
                error_str =  "w3c/tc/00/tp 'version' mismatch. " +\
                            f"found {version_str}. expected 00."
                ret = (False, error_str, None)
                break

            trace_id_str = fields[1]
            if (trace_id_str == "0" * 32): 
                error_str = "w3c/tc/00/tp invalid 'trace id' value of all 0's."
                ret = (False, error_str, None)
                break

            parent_id_str = fields[2]
            if (parent_id_str == "0" * 32): 
                error_str = "w3c/tc/00/tp invalid 'parent id' value of all 0's."
                ret = (False, error_str, None)
                break

            trace_flags_str = fields[3]
            if (not (trace_flags_str == "00" or 
                     trace_flags_str == "01")):
                # SAMPLED_FLAG
                error_str = "w3c/tc/00/tp invalid 'trace flag' value."
                ret = (False, error_str, None)
                break

            traceparent = W3CTC00Traceparent(
                            trace_id_str,
                            parent_id_str,
                            trace_flags_str)
            ret = (True, "", traceparent)
            break

        return ret

#----------------------------------------------------------------------------

class W3CTC00TraceparentRoot():
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
            self.trace_id_gen = W3CTC00TraceIdGenerator()

        if "parent_id_gen" in kwargs:
            self.parent_id_gen = kwargs["parent_id_gen"]
        else:
            self.parent_id_gen = W3CTC00ParentIdGenerator()

        self.trace_id = self.trace_id_gen.generate()

        return

    def generate(self, sampled_flag=True):
        """
        returns an W3CTC00Traceparent instance
        """

        return W3CTC00Traceparent(
                self.trace_id,
                self.parent_id_gen.generate(),
                "01" if (sampled_flag) else "00")
        
#----------------------------------------------------------------------------

class W3CTC00TraceparentForward():
    """
    Default implementation for
    https://www.w3.org/TR/trace-context version 00
    TODO: use incoming trace context
          bad incoming trace context
    """

    def __init__(self, tcp, **kwargs):
        """
        tcp => Non erroneous W3CTC00TraceparentParser
        """

        # kwargs parameter names
        # parent_id_gen

        if "parent_id_gen" in kwargs:
            self.parent_id_gen = kwargs["parent_id_gen"]
        else:
            self.parent_id_gen = W3CTC00ParentIdGenerator()

        self.tcp = tcp

        return

    def generate(self, sampled_flag=True):

        """
        returns an W3CTC00Traceparent instance
        """

        return W3CTC00Traceparent(
                self.tcp.trace_id_str,
                self.parent_id_gen.generate(),
                "01" if (sampled_flag) else self.tcp.trace_flags_str)

#----------------------------------------------------------------------------

class UnitTests():

    def __init__(self):
        return

    def root_n_forward(self, context, tp_r):

        # at client

        tp_r = tp_r.generate()
        print(f"{context}: client >>> {tp_r} >>> server", file=sys.stderr)

        # at server

        (status, error_str, tp_p) = W3CTC00Traceparent.parse(str(tp_r))
        if (not status):
            print (error_str, file=sys.stderr)
            return

        tp_f = W3CTC00TraceparentForward(tp_p).generate()
        print(f"{context}: client <<< {tp_f} <<< server", file=sys.stderr)

        print()

    def tc_1(self):
        tp_r_1 = W3CTC00TraceparentRoot()
        self.root_n_forward("r-1-tx-1", tp_r_1)
        self.root_n_forward("r-1-tx-2", tp_r_1)

        tp_r_2 = W3CTC00TraceparentRoot()
        self.root_n_forward("r-2-tx-1", tp_r_2)
        self.root_n_forward("r-2-tx-2", tp_r_2)


if __name__ == '__main__':

    ut = UnitTests()
    ut.tc_1()


    

