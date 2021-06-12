import simpy
from CI import CIRep

#----------------------------------------------------------------------------

def create_ci_rep(activity, is_source, reqtr, respdr, if_name, tx_id):

    ci_rep = CIRep(activity, is_source)
    fd     = ci_rep.field_dict
    fd["requestor"]   = reqtr
    fd["responder"]   = respdr
    fd["if-fnx-name"] = if_name
    fd["tx-id"]       = tx_id
    if (is_source):
        fd["sent-at"]     = env.now
    else:
        fd["received-at"] = env.now

    return ci_rep

#----------------------------------------------------------------------------

def segment_dispatcher(env, store):

    while True:

        tx_id = 100 + env.now

        '''
        ci_rep = create_ci_rep(
                    "request",
                    True,
                    "segsend",
                    "segrecv",
                    "segrecv/publish",
                    tx_id)
        print(ci_rep)
        '''

        store.put(tx_id)

        yield env.timeout(2)

#----------------------------------------------------------------------------

def segment_receiver(env, store):

    while True:

        tx_id = yield store.get()

        ci_rep = create_ci_rep(
                    "request",
                    False,
                    "segsend",
                    "segrecv",
                    "segrecv/publish",
                    tx_id)
        print(ci_rep)

        yield env.timeout(1)

#----------------------------------------------------------------------------

env = simpy.Environment()
store = simpy.Store(env)

env.process(segment_dispatcher(env, store))
env.process(segment_receiver(env, store))

env.run(until=10)

