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

        self.m_obj       = obj
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
        fd["received-at"]  = obj.m_env.now

        #print(ci_rep)
        print(f"now={self.m_obj.m_env.now},{ci_rep}")

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
    sys.stderr.flush()

#----------------------------------------------------------------------------

def calc_wait_for (obj,event_at):

    wait_for = event_at - (obj.m_env.now + obj.m_look_ahead)
    debugm (obj, f"event_at={event_at},lookahead={obj.m_look_ahead}," +\
                 f"wait_for={wait_for}")
    return wait_for

#----------------------------------------------------------------------------

class SegmentSender:

    def __init__(self, env, out_store, instructions):

        self.m_env        = env
        self.m_who        = "ss"
        self.m_tx_counter = 0
        self.m_out_store  = out_store
        self.m_proc       = env.process(self.run(instructions))

    def run(self, instructions):

        for instr in instructions:

            (command, params) = instr

            debugm (self, f"instr={instr}")

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
                 out_store, 
                 publish_look_ahead):

        self.m_env        = env
        self.m_who        = "sr"
        self.m_tx_counter = 0
        self.m_in_store   = simpy.Store (env)
        self.m_out_store  = out_store
        self.m_look_ahead = publish_look_ahead
        self.m_proc       = env.process(self.run())

    @property
    def comm(self):
        return self.m_in_store

    def run(self):

        while True:

            in_req = yield self.m_in_store.get()

            in_req.dump_as_incoming_ci (self)

            debugm (self, f"instr={in_req.instruction}")

            if (in_req.command == "publseg"):

                #---[command params]---

                params   = in_req.params
                seg_id   = params[0]
                duration = params[1]
                start_at = params[3]

                #debugm (self, f"duration={duration},start_at={start_at}")

                #---[pre publish wait]---

                wait_for = calc_wait_for (self, start_at)
                if (wait_for > 0):
                    debugm (self,
                            f"wait_for={wait_for},seg_id={seg_id}," +\
                            f"comment=pre publseg")
                    yield env.timeout(wait_for)

                #---[publish]---

                out_req = Request (self, in_req.instruction, in_req.tx_id)

                self.m_out_store.put (out_req)

                debugm (self, f"sent {out_req.command} command")

                #---[post publish wait]---

                seg_end_time = start_at + duration
                wait_for = calc_wait_for (self, seg_end_time)
                if (wait_for > 0):
                    debugm (self,
                            f"wait_for={wait_for},seg_id={seg_id}," +\
                            f"comment=post publseg")
                    yield env.timeout(wait_for)

#----------------------------------------------------------------------------

class SegmentItemSequencer:

    def __init__(self, 
                 env, 
                 out_store,
                 playout_look_ahead):

        self.m_env        = env
        self.m_who        = "sis"
        self.m_tx_counter = 0
        self.m_in_store   = simpy.Store (env)
        self.m_out_store  = out_store
        self.m_look_ahead = playout_look_ahead
        self.m_proc       = env.process(self.run())

    @property
    def comm(self):
        return self.m_in_store

    def run(self):

        while True:

            in_req = yield self.m_in_store.get()

            in_req.dump_as_incoming_ci (self)

            debugm (self, f"instr={in_req.instruction}")

            if (in_req.command == "publseg"):

                #---[command data]---

                params     = in_req.params
                seg_id     = params[0]
                asset_list = params[2]
                start_at   = params[3]

                for asset_info in asset_list:

                    asset_id  = asset_info[0]
                    asset_len = asset_info[1]

                    debugm (self, 
                            f"seg_id={seg_id},asset={asset_id}," +\
                            f"len={asset_len},start_at={start_at}")

                    #---[wait before play cmd issue]---

                    wait_for = calc_wait_for (self, start_at)
                    if (wait_for > 0):
                        debugm (self,
                                f"wait_for={wait_for},asset_id={asset_id}," +\
                                f"comment=before issuing play command")
                        yield env.timeout(wait_for)

                    #---[issue play command]---

                    instr = ("play", (seg_id, asset_id, asset_len, start_at, self.m_env.now))
                    out_req = Request (self, instr, in_req.tx_id)

                    self.m_out_store.put (out_req)

                    debugm (self, f"comment=sent {out_req.command} command")

                    #---[wait after play cmd issue]---

                    asset_end_time = start_at + asset_len
                    wait_for = calc_wait_for (self, asset_end_time)
                    if (wait_for > 0):
                        debugm (self,
                                f"wait_for={wait_for},asset_id={asset_id}," +\
                                f"comment=after issuing play command")
                        yield env.timeout(wait_for)

                    #---[advance start_at]---

                    start_at += asset_len

#----------------------------------------------------------------------------

class Player:

    def __init__(self, 
                 env):

        self.m_env      = env
        self.m_who      = "plyr"
        self.m_in_store = simpy.Store (env)
        self.m_proc     = env.process(self.run())

    @property
    def comm(self):
        return self.m_in_store

    def run(self):

        while True:

            in_req = yield self.m_in_store.get()

            in_req.dump_as_incoming_ci (self)

            if (in_req.command == "play"):

                #---[command data]---

                params    = in_req.params
                seg_id    = params[0]
                asset_id  = params[1]
                asset_len = params[2]
                start_at  = params[3]
                req_at    = params[4]

                debugm (self, f"command=play,seg_id={seg_id}," +\
                              f"asset={asset_id},len={asset_len}," +\
                              f"start_at={start_at},req_at={req_at}")

#----------------------------------------------------------------------------

g_publish_segment_look_ahead = 10
g_play_cmd_look_ahead = 5

g_ss_instructions = [
("publseg", 
    ("A/v1",    # segment name
     30,        # duration
     [ ("x", 5), ("y", 20),("z", 5)  ], # asset list
     20)),      # start at

("waitfor", 
    (5,)),       # sleep duration

("publseg", 
    ("B/v1", 
     30, 
     [ ("x", 5), ("c", 15),("d", 10) ], 
     50))
]

#----------------------------------------------------------------------------

env = simpy.Environment()

#---[define services]---

plyr = Player (env)
sis  = SegmentItemSequencer (env, plyr.comm, g_play_cmd_look_ahead)
sr   = SegmentReceiver (env, sis.comm, g_publish_segment_look_ahead)
ss   = SegmentSender (env, sr.comm, g_ss_instructions)

#---[start main event loop]---

#env.run(until=100)

until = 100
while env.peek() < until:
    x = input (f"{env.now}:<enter> to step:")
    #print('#Stepping')
    env.step()

