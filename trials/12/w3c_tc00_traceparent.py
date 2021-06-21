import datetime
import random
import uuid
import sys
import w3c_tc00_utils as U

#----------------------------------------------------------------------------

class DefaultUUIDGenerator():

    def __init__(self):
        return

    def generate32(self):
        """
        Default implementation for
        https://www.w3.org/TR/trace-context/#trace-id
        """

        return uuid.uuid4().hex

    def generate16(self):
        """
        Default implementation for
        https://www.w3.org/TR/trace-context/#parent-id

        <---random----><---seconds-since-epoch--->
        <---8 hex-----><---8 hex----------------->
        """

        rand_32 = random.randint(0, 0xffffffff)
        s_r32   = hex(rand_32)[2:].zfill(8)

        seconds_since_epoch = \
            int((datetime.datetime.utcnow() - \
                 datetime.datetime(1970, 1, 1)).total_seconds())
        s_sse = hex(seconds_since_epoch)[2:].zfill(8)

        return f"{s_r32}{s_sse}"


#----------------------------------------------------------------------------

class W3CTC00Traceparent():

    S_OK = 0
    S_INVALID_LEN         = 1
    S_NUM_FIELDS_MISMATCH = 2
    S_INVALID_VERSION     = 3
    S_INVALID_TRACE_ID    = 4
    S_INVALID_PARENT_ID   = 5
    S_INVALID_TRACE_FLAG  = 6

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
    def parse (tc00tp_str):
        """
        Returns a 3-tuple
        (parse_status, W3CTC00Traceparent)
        see https://www.w3.org/TR/trace-context/#versioning-of-traceparent
        """

        while True: # just need a 'block'

            if (len(tc00tp_str) != 55):
                ret = (W3CTC00Traceparent.S_INVALID_LEN, None)
                break

            fields = tc00tp_str.split("-")
            n = len(fields)
            if (n != 4):
                ret = (W3CTC00Traceparent.S_NUM_FIELDS_MISMATCH, None)
                break

            version_str = fields[0]
            if (version_str != "00"): 
                ret = (W3CTC00Traceparent.S_INVALID_VERSION, None)
                break

            trace_id_str = fields[1]
            if (not U.is_hex_string(trace_id_str, 32)):
                ret = (W3CTC00Traceparent.S_INVALID_TRACE_ID, None)
                break

            parent_id_str = fields[2]
            if (not U.is_hex_string(parent_id_str, 16)):
                ret = (W3CTC00Traceparent.S_INVALID_PARENT_ID, None)
                break

            trace_flags_str = fields[3]
            if (not U.is_hex_string(trace_flags_str, 2)):
                ret = (W3CTC00Traceparent.S_INVALID_TRACE_FLAG, None)
                break
            if (not (trace_flags_str == "00" or 
                     trace_flags_str == "01")):
                # SAMPLED_FLAG
                ret = (W3CTC00Traceparent.S_INVALID_TRACE_FLAG, None)
                break

            traceparent = W3CTC00Traceparent(
                            trace_id_str,
                            parent_id_str,
                            trace_flags_str)
            ret = (W3CTC00Traceparent.S_OK, traceparent)
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

    def __init__(self, uuid_gen=None):

        if (uuid_gen != None):
            self.uuid_gen = uuid_gen
        else:
            self.uuid_gen = DefaultUUIDGenerator()

        self.trace_id = self.uuid_gen.generate32()

        return

    def generate(self, sampled_flag=True):
        """
        returns an W3CTC00Traceparent instance
        """

        return W3CTC00Traceparent(
                self.trace_id,
                self.uuid_gen.generate16(),
                "01" if (sampled_flag) else "00")
        
#----------------------------------------------------------------------------

class W3CTC00TraceparentModf():
    """
    Default implementation for
    https://www.w3.org/TR/trace-context version 00
    """

    def __init__(self, traceparent, uuid_gen=None):
        """
        traceparent => Non erroneous W3CTC00Traceparent
        """

        if (uuid_gen != None):
            self.uuid_gen = uuid_gen
        else:
            self.uuid_gen = DefaultUUIDGenerator()

        self.tcp = traceparent

        return

    def generate(self, sampled_flag=True):
        """
        returns an W3CTC00Traceparent instance
        """

        return W3CTC00Traceparent(
                self.tcp.trace_id_str,
                self.uuid_gen.generate16(),
                "01" if (sampled_flag) else self.tcp.trace_flags_str)

