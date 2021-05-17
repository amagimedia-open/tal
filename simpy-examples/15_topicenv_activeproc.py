import simpy

def subfunc(env):
    print("@C", env.active_process)  # will print "p1"

def my_proc(env):
    while True:
        print("@B", env.active_process)  # will print "p1"
        subfunc(env)
        yield env.timeout(1)

env = simpy.Environment()
p1 = env.process(my_proc(env))

print("@A", env.active_process)  # None
env.step()
print("@D", env.active_process)  # None
