import simpy

def Foo(env):
    global next_timeout_duration
    while True:
        print('Next timeout duration %d' % next_timeout_duration)
        yield env.timeout(next_timeout_duration)
        print('Current time is %d' % env.now)
        next_timeout_duration *= 2

next_timeout_duration = 2
env = simpy.Environment()

env.process(Foo(env))

until = 20
while env.peek() < until:
    print('#Stepping')
    env.step()

