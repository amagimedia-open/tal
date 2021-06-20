import sys
import w3c_tc00_traceparent as TP

#----------------------------------------------------------------------------

class W3CTC00NaiveTraceIdGenerator():

    def __init__(self):
        self.counter = 0xdeadbeef
        return

    def generate(self):
        s = hex(self.counter)[2:].zfill(32)
        self.counter += 1
        return s

#----------------------------------------------------------------------------

class W3CTC00NaiveParentIdGenerator():

    def __init__(self):
        self.counter = 0
        return

    def generate(self):
        self.counter += 1
        s = hex(self.counter)[2:].zfill(16)
        return s

#----------------------------------------------------------------------------

class UnitTests():

    def __init__(self):
        return

    def root_n_forward(self, context, tp_r):

        # at client (generation of root)

        tp_r = tp_r.generate()
        print(f"{context}: client >>> {tp_r} >>> server", file=sys.stderr)

        # at server (generation of forward)

        (status, tp_p) = TP.W3CTC00Traceparent.parse(str(tp_r))
        if (status != TP.W3CTC00Traceparent.S_OK):
            print (f"status_code={status}", file=sys.stderr)
            return

        tp_f = TP.W3CTC00TraceparentForward(tp_p).generate()
        print(f"{context}: client <<< {tp_f} <<< server", file=sys.stderr)

        print()

    def tc_1(self):

        tp_r_1 = TP.W3CTC00TraceparentRoot()
        self.root_n_forward("r-1-tx-1", tp_r_1)
        self.root_n_forward("r-1-tx-2", tp_r_1)

        tp_r_2 = TP.W3CTC00TraceparentRoot(
                    trace_id_gen=W3CTC00NaiveTraceIdGenerator(),
                    parent_id_gen=W3CTC00NaiveParentIdGenerator())
        self.root_n_forward("r-2-tx-1", tp_r_2)
        self.root_n_forward("r-2-tx-2", tp_r_2)


if __name__ == '__main__':

    ut = UnitTests()
    ut.tc_1()

