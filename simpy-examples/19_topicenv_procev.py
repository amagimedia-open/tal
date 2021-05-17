import simpy

def sub(env):
    yield env.timeout(1)
    return 23

def parent(env):
    ret = yield env.process(sub(env))
    return ret

env = simpy.Environment()

ret_val = env.run(env.process(parent(env)))

assert ret_val == 23
