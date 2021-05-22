import sys
import simpy
from CI import CIRep

#----------------------------------------------------------------------------

def create_ci_rep(activity, 
                  is_source, 
                  reqtr, 
                  respdr, 
                  if_name, 
                  tx_id, 
                  p_tx_id):

    ci_rep = CIRep(activity, is_source)
    fd     = ci_rep.field_dict
    fd["requestor"]    = reqtr
    fd["responder"]    = respdr
    fd["if-fnx-name"]  = if_name
    fd["tx-id"]        = tx_id
    fd["parent-tx-id"] = p_tx_id
    if (is_source):
        fd["sent-at"]     = env.now
    else:
        fd["received-at"] = env.now

    return ci_rep

#----------------------------------------------------------------------------

class SegmentSender:

    def __init__(self, env, out_store):

        self.m_env        = env
        self.m_out_store  = out_store
        self.m_tx_counter = 0
        self.m_who        = "ss"

    def run(self, instructions):

        for instr in instructions:

            command    = instr[0]
            data       = instr[1]

            print(f"now={env.now},\
            who={who},\
            comment=processing {command}", 
            file=sys.stderr)

            if (command == "waitfor"):

                duration = data[0]

                print(f"now={env.now},\
                who={self.m_who},\
                comment=waitfor {duration} units",
                file=sys.stderr)

                yield env.timeout(duration)

                continue

            if (command == "publish"):

                tx_id = f"{self.m_who}-{self.m_tx_counter}"
                self.m_tx_counter += 1

                req = (instr, env.now, self.m_who, tx_id, None)
                self.m_out_store.put(req)

                print(f"now={env.now},\
                who={self.m_who},\
                comment=sent {command} command",
                file=sys.stderr)

                continue

#----------------------------------------------------------------------------

class SegmentReceiver:

    def __init__(self, 
                 env, 
                 in_store, 
                 out_store, 
                 publish_look_ahead):

        self.m_env        = env
        self.m_in_store   = in_store
        self.m_out_store  = out_store
        self.m_pll        = publish_look_ahead
        self.m_tx_counter = 0
        self.m_who        = "sr"

    def run(self):

        while True:

            req = yield in_store.get()

            instr     = req[0]
            command   = instr[0]
            data      = instr[1]
            sent_at   = req[1]
            requestor = req[2]
            tx_id     = req[3]
            p_tx_id   = req[4]

            ci_rep = create_ci_rep(
                        "request",
                        False,
                        requestor,
                        self.m_who,
                        command,
                        tx_id,
                        p_tx_id)
            print(ci_rep)

            if (command == "publish"):

                #---[command data]---

                seg_id     = data[0]
                duration   = data[1]
                asset_list = data[2]
                effect_at  = data[3]

                #---[pre publish wait]---

                wait_for = effect_at - (env.now + self.m_pll)
                if (wait_for > 0):

                    print(f"now={env.now},\
                    who={self.m_who},\
                    comment=waitfor {wait_for} before publish",
                    file=sys.stderr)

                    yield env.timeout(wait_for)

                #---[publish]---

                p_tx_id = tx_id
                tx_id = f"{self.m_who}-{self.m_tx_counter}"
                self.m_tx_counter += 1

                req = (instr, env.now, self.m_who, tx_id, p_tx_id)
                self.m_out_store.put(req)

                print(f"now={env.now},\
                who={self.m_who},\
                comment=sent {command} command",
                file=sys.stderr)

                #---[post publish wait]---

                seg_end_time = effect_at + duration
                wait_for     = seg_end_time - (env.now + self.m_pll)
                if (wait_for > 0):

                    print(f"now={env.now},\
                    who={self.m_who},\
                    comment=waitfor {wait_for} after publish",
                    file=sys.stderr)

                    yield env.timeout(wait_for)

#----------------------------------------------------------------------------

class SegmentItemSequencer:

    def __init__(self, 
                 env, 
                 in_store, 
                 out_store,
                 playout_look_ahead):

        self.m_env        = env
        self.m_in_store   = in_store
        self.m_out_store  = out_store
        self.m_pll        = playout_look_ahead
        self.m_tx_counter = 0
        self.m_who        = "sis"

    def run(self):

        while True:

            req = yield in_store.get()

            instr     = req[0]
            command   = instr[0]
            data      = instr[1]
            sent_at   = req[1]
            requestor = req[2]
            tx_id     = req[3]
            p_tx_id   = req[4]

            ci_rep = create_ci_rep(
                        "request",
                        False,
                        requestor,
                        self.m_who,
                        command,
                        tx_id,
                        p_tx_id)
            print(ci_rep)

            if (command == "publish"):

                #---[command data]---

                seg_id     = data[0]
                duration   = data[1]
                asset_list = data[2]
                effect_at  = data[3]
                index      = 0
                p_tx_id    = tx_id

                for asset_info in asset_list:

                    asset_id  = asset_info[0]
                    asset_len = asset_info[1]

                    print(f"now={env.now},\
                    who={self.m_who},\
                    asset={asset_id},
                    len={asset_len},
                    comment=playout at {effect_at}",
                    file=sys.stderr)

                    #---[pre play wait]---

                    wait_for = effect_at - (env.now + self.m_pll)
                    if (wait_for > 0):

                        print(f"now={env.now},\
                        who={self.m_who},\
                        asset={asset_id},
                        len={asset_len},
                        comment=waitfor {wait_for} before issuing play command",
                        file=sys.stderr)

                        yield env.timeout(wait_for)

                    #---[issue play command]---

                    tx_id = f"{self.m_who}-{self.m_tx_counter}"
                    self.m_tx_counter += 1

                    command = "play"
                    instr = (command, (asset_id, asset_len, effect_at, env.now))
                    req = (instr, env.now, self.m_who, tx_id, p_tx_id)
                    self.m_out_store.put(req)

                    print(f"now={env.now},\
                    who={self.m_who},\
                    comment=sent {command} command for {asset_id} len {asset_len}",
                    file=sys.stderr)

                    #---[pre play wait]---

                    asset_end_time = effect_at + asset_len
                    wait_for       = asset_end_time - (env.now + self.m_pll)
                    if (wait_for > 0):

                        print(f"now={env.now},\
                        who={self.m_who},\
                        asset={asset_id},
                        len={asset_len},
                        comment=waitfor {wait_for} after issuing play command",
                        file=sys.stderr)

                        yield env.timeout(wait_for)

                    effect_at += asset_len

#----------------------------------------------------------------------------

class Player:

    def __init__(self, 
                 env, 
                 in_store, 
                 playout_look_ahead):

        self.m_env        = env
        self.m_in_store   = in_store
        self.m_pll        = playout_look_ahead
        self.m_tx_counter = 0
        self.m_who        = "plyr"

    def run(self);

        while True:

            req = yield in_store.get()

            instr     = req[0]
            command   = instr[0]
            data      = instr[1]
            sent_at   = req[1]
            requestor = req[2]
            tx_id     = req[3]
            p_tx_id   = req[4]

            ci_rep = create_ci_rep(
                        "request",
                        False,
                        requestor,
                        self.m_who,
                        command,
                        tx_id,
                        p_tx_id)
            print(ci_rep)

            if (command == "play"):

                #---[command data]---

                asset_id  = data[0]
                asset_len = data[1]
                effect_at = data[2]
                sent_at   = data[3]

                print(f"now={env.now},\
                who={self.m_who},\
                comment=play command sent at {sent_at} for {asset_id} len {asset_len} at {sent_at}",
                file=sys.stderr)

#----------------------------------------------------------------------------

g_publish_look_ahead = 10

g_instructions = [
    # (seg_name, duration, asset_list, effect_at)
    ("publish", 
        ("A/v1", 
         30, 
         [ ("x", 5), ("y", 20),("z", 5)  ], 
         20)),

    ("waitfor", (5)),

    ("publish", 
        ("B/v1", 
         30, 
         [ ("x", 5), ("c", 15),("d", 10) ], 
         50))
]

#----------------------------------------------------------------------------

env = simpy.Environment()
ev_store = simpy.Store(env)

env.process(seg_sendr(env, ev_store, g_segments))
env.process(seg_recvr(env, ev_store))

env.run(until=100)

