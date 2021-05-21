import simpy
from CI import CIRep

def segment_dispatcher(env):
    global g_dispatch_event
    while True:
        yield env.timeout(2)

        tx_id = 100 + env.now

        ci_rep = CIRep("request", True)
        fd     = ci_rep.field_dict
        fd["requestor"]   = "seg_dispatcher"
        fd["responder"]   = "seg_receiver"
        fd["if-fnx-name"] = "segrecv/publish"
        fd["sent-at"]     = env.now
        fd["tx-id"]       = tx_id
        print(ci_rep)

        g_dispatch_event.succeed(value=tx_id)
        g_dispatch_event = env.event()


def segment_receiver(env):
    while True:
        tx_id = yield g_dispatch_event

        ci_rep = CIRep("request", False)
        fd     = ci_rep.field_dict
        fd["requestor"]   = "seg_dispatcher"
        fd["responder"]   = "seg_receiver"
        fd["if-fnx-name"] = "segrecv/publish"
        fd["received-at"] = env.now
        fd["tx-id"]       = tx_id
        print(ci_rep)


env = simpy.Environment()

g_dispatch_event = env.event()

env.process(segment_dispatcher(env))
env.process(segment_receiver(env))

env.run(until=10)


