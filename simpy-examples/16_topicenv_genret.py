import simpy

def my_proc(env):
    yield env.timeout(1)
    return 42

def other_proc(env):
    ret_val = yield env.process(my_proc(env))
    assert ret_val == 42

env = simpy.Environment()

env.process(other_proc(env))

env.run()
