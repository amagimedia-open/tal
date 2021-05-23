import sys
import simpy
from CI import CIRep

#----------------------------------------------------------------------------

class Request:

    def __init__(self, obj, instruction, p_tx_id=None):

        """
        instruction must be of the form (cmd, (param1, param2, ...))
        p_tx_id is 'parent tx_id'
        """

        tx_id = f"{obj.m_who}-{obj.m_tx_counter}"
        obj.m_tx_counter += 1

        self.m_instr     = instruction
        self.m_sent_at   = obj.m_env.now
        self.m_requestor = obj.m_who
        self.m_tx_id     = tx_id
        self.m_p_tx_id   = p_tx_id

    @property
    def instruction(self):
        return self.m_instr

    @property
    def command(self):
        return self.m_instr[0]

    @property
    def params(self):
        return self.m_instr[1]

    @property
    def sent_at(self):
        return self.m_sent_at

    @property
    def requestor(self):
        return self.m_requestor

    @property
    def tx_id(self):
        return self.m_tx_id

    @property
    def p_tx_id(self):
        return self.m_p_tx_id

    def dump_as_incoming_ci(self, obj):

        ci_rep = CIRep("request", False)
        fd     = ci_rep.field_dict
        fd["requestor"]    = self.requestor
        fd["responder"]    = obj.m_who
        fd["if-fnx-name"]  = self.command
        fd["tx-id"]        = self.tx_id
        fd["parent-tx-id"] = self.p_tx_id
        if (is_source):
            fd["sent-at"]     = obj.m_env.now
        else:
            fd["received-at"] = obj.m_env.now

        print(ci_rep)

    def __repr__(self):

        return (self.m_instr,
                self.m_sent_at,
                self.m_requestor,
                self.m_tx_id,
                self.m_p_tx_id)

#----------------------------------------------------------------------------

def debugm (obj,msg):

    print(f"now={obj.m_env.now},who={obj.m_who},{msg}",\
          file=sys.stderr)

#----------------------------------------------------------------------------

def wait_for_event(obj, event_at, comment):

    wait_for = event_at - (obj.m_env.now + obj.m_look_ahead)
    if (wait_for > 0):
        debugm (obj, f"wait_for={wait_for},comment={comment}")
        yield env.timeout(wait_for)

#----------------------------------------------------------------------------

class SegmentSender:

    def __init__(self, env, out_store):

        self.m_env        = env
        self.m_who        = "ss"
        self.m_tx_counter = 0
        self.m_out_store  = out_store

    def run(self, instructions):

        for instr in instructions:

            (command, params) = instr

            debugm (self, f"comment=processing {command}")

            if (command == "waitfor"):

                duration = params[0]

                debugm (self, f"comment=waitfor {duration} units")

                yield env.timeout(duration)

                continue

            if (command == "publseg"):

                self.m_out_store.put (Request (self, instr))

                debugm (self, f"comment=sent {command} command")

                continue

#----------------------------------------------------------------------------

class SegmentReceiver:

    def __init__(self, 
                 env, 
                 in_store, 
                 out_store, 
                 publish_look_ahead):

        self.m_env        = env
        self.m_who        = "sr"
        self.m_tx_counter = 0
        self.m_in_store   = in_store
        self.m_out_store  = out_store
        self.m_look_ahead = publish_look_ahead

    def run(self):

        while True:

            #---[incoming request]---

            in_req = yield in_store.get()

            #---[dump component interaction representation]---

            in_req.dump_as_incoming_ci (self)

            #---[handle command(s)]---

            if (in_req.command == "publseg"):

                #---[command params]---

                params   = in_req.params
                duration = params[1]
                start_at = params[3]

                #---[pre publish wait]---

                wait_for_event (obj, start_at, "pre publseg")

                #---[publish]---

                out_req = Request (self, in_req.instruction, in_req.tx_id)

                self.m_out_store.put (out_req)

                debugm ("sent {out_req.command} command")

                #---[post publish wait]---

                seg_end_time = start_at + duration
                wait_for_event (self, seg_end_time, "post publseg")

#----------------------------------------------------------------------------

class SegmentItemSequencer:

    def __init__(self, 
                 env, 
                 in_store, 
                 out_store,
                 playout_look_ahead):

        self.m_env        = env
        self.m_who        = "sis"
        self.m_tx_counter = 0
        self.m_in_store   = in_store
        self.m_out_store  = out_store
        self.m_look_ahead = playout_look_ahead

    def run(self):

        while True:

            #---[incoming request]---

            in_req = yield in_store.get()

            #---[dump component interaction representation]---

            in_req.dump_as_incoming_ci (self)

            #---[handle command(s)]---

            if (command == "publseg"):

                #---[command data]---

                params     = in_req.params
                asset_list = params[2]
                start_at   = params[3]

                for asset_info in asset_list:

                    asset_id  = asset_info[0]
                    asset_len = asset_info[1]

                    debugm (self, "asset={asset_id},len={asset_len},start_at={start_at}")

                    #---[wait before play cmd issue]---

                    wait_for_event (self, start_at, "before issuing play command")

                    #---[issue play command]---

                    instr = ("play", (asset_id, asset_len, start_at, self.m_env.now))
                    out_req = Request (self, instr, in_req.tx_id)

                    self.m_out_store.put (out_req)

                    debugm ("comment=sent {out_req.command} command")

                    #---[wait after play cmd issue]---

                    asset_end_time = start_at + asset_len
                    wait_for_event (self, asset_end_time, "after issuing play command")

                    #---[advance to start of next asset]---

                    start_at += asset_len

#----------------------------------------------------------------------------

class Player:

    def __init__(self, 
                 env, 
                 in_store):

        self.m_env        = env
        self.m_who        = "plyr"
        self.m_in_store   = in_store

    def run(self);

        while True:

            #---[incoming request]---

            in_req = yield in_store.get()

            #---[dump component interaction representation]---

            in_req.dump_as_incoming_ci (self)

            #---[handle command(s)]---

            if (in_req.command == "play"):

                #---[command data]---

                params    = in_req.params
                asset_id  = params[0]
                asset_len = params[1]
                start_at  = params[2]
                req_at    = params[3]

                debugm (self, "command=play,asset={asset_id},len={asset_len},\
                start_at={start_at},req_at={req_at}")

#----------------------------------------------------------------------------

g_publish_segment_look_ahead = 10
g_play_cmd_look_ahead = 5

g_instructions = [
("publseg", 
    ("A/v1",    # segment name
     30,        # duration
     [ ("x", 5), ("y", 20),("z", 5)  ], # asset list
     20)),      # start at

("waitfor", 
    (5)),       # sleep duration

("publseg", 
    ("B/v1", 
     30, 
     [ ("x", 5), ("c", 15),("d", 10) ], 
     50))
]

#----------------------------------------------------------------------------

env = simpy.Environment()

#---[stores]---

segrecv_store    = simpy.Store (env)
segitemseq_store = simpy.Store (env)
player_store     = simpy.Store (env)

#---[define services]---

ss = SegmentSender (env, segrecv_store)

sr = SegmentReceiver (\
        env,\
        segrecv_store,\
        segitemseq_store,\
        g_publish_segment_look_ahead)

sis = SegmentItemSequencer (\
        env, \
        segitemseq_store,\
        player_store,\
        g_play_cmd_look_ahead)

plyr = Player (env, player_store)

#---[start services]---

env.process(plyr.run())
env.process(sis.run())
env.process(sr.run())
env.process(ss.run(g_instructions))

#---[start main event loop]---

env.run(until=100)

