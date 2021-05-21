import sys
from collections import OrderedDict

class CIRep:

    m_activity_values = [ 
        "request", 
        "response", 
        "event" 
    ]

    m_field_names = [
        # Dont change the field name order
        # m_constraints needs it to be in this order
        "activity",         #a
        "requestor",        #b
        "responder",        #c
        "event-source",     #d
        "event-sink",       #e
        "tx-id",            #f
        "parent-tx-id",     #g
        "sent-at",          #h
        "received-at",      #i
        "if-fnx-name",      #j
        "event-name",       #k
        "req-desc",         #l
        "resp-desc",        #m
        "ev-desc"           #n
    ]

    m_constraints = {
                            # M - Mandatory
                            # O - Optional
                            # X - Prohibited

                            #abcdefghijklmn
        "request/source"  : "MMOXXMOMXMXOXX",
        "request/sink"    : "MOMXXMOOMMXOXX",
        "response/sink"   : "MOMXXMOMXMXXOX",
        "response/source" : "MMOXXMOOMMXXOX",
        "event/source"    : "MXXMOMOMXXMXXO",
        "event/sink"      : "MXXOMMOOMXMXXO"
    }

    def __init__(self, activity, source=True):

        # source == True  => requestor or event-source
        # source == False => responder or event-sink

        if not activity in self.m_activity_values :
            raise LookupError(f"activity value '{activity}' is invalid")

        self.m_field_dict = OrderedDict()
        for field_name in self.m_field_names:
            self.m_field_dict[field_name] = None

        self.m_field_dict["activity"] = activity
        self.m_source = source
        return

    @property
    def field_dict(self):
        return self.m_field_dict

    def validate(self):
        constraint_key = self.m_field_dict["activity"] + "/" + \
                         "source" if self.m_source else "sink"
        constraint_val = self.m_constraints[constraint_key]

        #print(f"constraint_key = {constraint_key}", file=sys.stderr)
        #print(f"constraint_val = {constraint_val}", file=sys.stderr)

        index = 0
        error = None
        for key in self.m_field_dict:
            #print(f"index={index},key={key}", file=sys.stderr)

            # note that self.m_field_dict is an OrderedDict
            constraint = constraint_val[index]
            index += 1

            if (constraint == 'M' and 
                self.m_field_dict[key] == None):
                error = f"Value for {key} mandatory"
                break

            if (constraint == 'X' and 
                self.m_field_dict[key] != None):
                error = f"Value for {key} prohibited"
                break

        ret = (error == None)
        return (ret, error)


    def __str__(self):
        csnv = []
        for key in self.m_field_dict:
            if self.m_field_dict[key] != None:
                csnv.append(f"{key}={self.m_field_dict[key]}")
        return ",".join(csnv)


#------------------[unit test cases]-----------------------------------------

# https://realpython.com/python-testing/

import unittest

class TestCIRep(unittest.TestCase):
    def test_cirep_str_1 (self):
        ci_rep = CIRep("request", True)
        fd = ci_rep.field_dict
        fd["requestor"] = "Comp-A"
        fd["responder"] = "Comp-B"
        fd["tx-id"]     = 100
        fd["if-fnx-name"] = "segrecv/publish"

        exp_result = "activity=request,requestor=Comp-A,responder=Comp-B,tx-id=100,if-fnx-name=segrecv/publish"
        act_result = str(ci_rep)


        self.assertEqual(exp_result, act_result)


    def test_cirep_validate_1 (self):
        ci_rep = CIRep("request", True)
        fd = ci_rep.field_dict
        fd["requestor"] = "Comp-A"
        fd["responder"] = "Comp-B"
        fd["tx-id"]     = 100
        fd["if-fnx-name"] = "segrecv/publish"

        (valid, error) = ci_rep.validate()

        self.assertEqual(valid, False)
        self.assertEqual(error, "Value for sent-at mandatory")

    def test_cirep_validate_2 (self):
        ci_rep = CIRep("request", True)
        fd = ci_rep.field_dict
        fd["requestor"] = "Comp-A"
        fd["responder"] = "Comp-B"
        fd["tx-id"]     = 100
        fd["if-fnx-name"] = "segrecv/publish"
        fd["sent-at"] = "2"
        fd["event-source"] = "foo"

        (valid, error) = ci_rep.validate()

        self.assertEqual(valid, False)
        self.assertEqual(error, "Value for event-source prohibited")


if __name__ == '__main__':
    unittest.main()

