import simpy

def progressbar_update(t):
    print('>' * t)

def clock(env, name, tick):
    while True:
        print(name, env.now)
        yield env.timeout(tick)

env = simpy.Environment()

env.process(clock(env, 'fast', 0.5))
env.process(clock(env, 'slow', 1))

for i in range(10):
    env.run(until=i+1)
    progressbar_update(i)

