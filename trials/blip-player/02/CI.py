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
        "activity",
        "requestor",
        "responder",
        "event-source",
        "event-sink",
        "tx-id",
        "parent-tx-id",
        "sent-at",
        "received-at",
        "if-fnx-name",
        "event-name",
        "req-desc",
        "resp-desc",
        "ev-desc"
    ]

    m_constraints = {
        # M - Mandatory
        # O - Optional
        # X - Prohibited
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


if __name__ == '__main__':
    unittest.main()





