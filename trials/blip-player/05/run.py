import simpy
from CI import CIRep

def segment_dispatcher(env, store):
    while True:
        tx_id = 100 + env.now

        ci_rep = CIRep("request", True)
        fd     = ci_rep.field_dict
        fd["requestor"]   = "seg_dispatcher"
        fd["responder"]   = "seg_receiver"
        fd["if-fnx-name"] = "segrecv/publish"
        fd["sent-at"]     = env.now
        fd["tx-id"]       = tx_id
        print(ci_rep)

        store.put(tx_id)

        yield env.timeout(2)


def segment_receiver(env, store):
    while True:
        tx_id = yield store.get()

        ci_rep = CIRep("request", False)
        fd     = ci_rep.field_dict
        fd["requestor"]   = "seg_dispatcher"
        fd["responder"]   = "seg_receiver"
        fd["if-fnx-name"] = "segrecv/publish"
        fd["received-at"] = env.now
        fd["tx-id"]       = tx_id
        print(ci_rep)

        yield env.timeout(1)


env = simpy.Environment()
store = simpy.Store(env)

env.process(segment_dispatcher(env, store))
env.process(segment_receiver(env, store))

env.run(until=10)

