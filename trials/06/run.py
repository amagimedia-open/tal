import simpy
from CI import CIRep

#----------------------------------------------------------------------------

class Segment:

    def __init__(self, id, duration, asset_list):
        self.m_name = id
        self.m_duration = duration
        self.m_asset_list = asset_list

    @property
    def asset_list(self):
        return self.m_asset_list

#----------------------------------------------------------------------------

class SegmentRequest:

    def __init__(self, env, requestor, tx_id, if_name, segment, effect_at):
        self.m_req_at    = env.now
        self.m_requestor = requestor
        self.m_tx_id     = tx_id
        self.m_if_name   = if_name
        self.m_segment   = segment
        self.m_effect_at = effect_at

    @property
    def req_at(self):
        return self.m_req_at

    @property
    def requestor(self):
        return self.m_requestor

    @property
    def tx_id(self):
        return self.m_tx_id

    @property
    def if_name(self):
        return self.m_if_name

    @property
    def segment(self):
        return self.m_segment

    @property
    def effect_at(self):
        return self.m_effect_at

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

def seg_sendr(env, ev_store, segments):

    global g_tx_id

    for seg_info in segments:

        seg_id     = seg_info[0]
        duration   = seg_info[1]
        asset_list = seg_info[2]
        effect_at  = seg_info[3]

        wait_for = effect_at - (env.now + g_publish_look_ahead)
        if (wait_for > 0):
            print(f"now={env.now},wait_for={wait_for},reason=pre_publish_lookahead")
            yield env.timeout(wait_for)

        seg = Segment(seg_id, duration, asset_list)
        seg_req = SegmentRequest(env, "seg_sendr", g_tx_id, "publish", seg, effect_at)
        g_tx_id += 1
        ev_store.put(seg_req)
        print(f"now={env.now},reason=sent_seg_req")

        seg_end_time = effect_at + duration
        wait_for     = seg_end_time - (env.now + g_publish_look_ahead)
        if (wait_for > 0):
            print(f"now={env.now},wait_for={wait_for},reason=post_publish_lookahead")
            yield env.timeout(wait_for)

#----------------------------------------------------------------------------

def seg_recvr(env, ev_store):

    while True:

        seg_req = yield ev_store.get()

        ci_rep = create_ci_rep(
                    "request",
                    False,
                    seg_req.requestor,
                    "seg_recvr",
                    seg_req.if_name,
                    seg_req.tx_id)
        print(ci_rep)

        #yield env.timeout(1)

#----------------------------------------------------------------------------

g_tx_id = 100
g_publish_look_ahead = 10

g_segments = [
    # (seg_name, duration, asset_list, effect_at)
    ("A/v1", 30, [ ("x", 5), ("y", 20),("z", 5)  ], 20),
    ("B/v1", 30, [ ("x", 5), ("c", 15),("d", 10) ], 50)
]


#----------------------------------------------------------------------------

env = simpy.Environment()
ev_store = simpy.Store(env)

env.process(seg_sendr(env, ev_store, g_segments))
env.process(seg_recvr(env, ev_store))

env.run(until=100)

