import simpy

class School:
    def __init__(self, env):
        self.env = env
        self.class_ends = env.event()
        self.pupil_procs = [env.process(self.pupil(ord('a')+i)) for i in range(3)]
        self.bell_proc = env.process(self.bell())

    def bell(self):
        for i in range(2):
            yield self.env.timeout(45)
            self.class_ends.succeed()
            self.class_ends = self.env.event()
            print("BELL")

    def pupil(self, id):
        for i in range(2):
            #print(r' \o/%c' % id, end='')
            print("<B %c" % id)
            yield self.class_ends
            print(">B %c" % id)

env = simpy.Environment()

school = School(env)

env.run()

