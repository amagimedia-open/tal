import simpy

'''
Process A requests the resource with priority 0. It immediately becomes a user.
Process B requests the resource with priority -2 but sets preempt to False. It will queue up and wait.
Process C requests the resource with priority -1 but leaves preempt True. Normally, it would preempt A but in this case, B is queued up before C and prevents C from preempting A. C can also not preempt B since its priority is not high enough.
'''

def user(name, env, res, prio, preempt):
    with res.request(priority=prio, preempt=preempt) as req:
        try:
            print(f'{name}/{prio}/{preempt} requesting resource at {env.now}')
            assert isinstance(env.now, int), type(env.now)
            yield req
            assert isinstance(env.now, int), type(env.now)
            print(f'{name}/{prio}/{preempt} got resource at {env.now}')
            yield env.timeout(3)
        except simpy.Interrupt:
            print(f'{name}/{prio}/{preempt} got preempted at {env.now}')
    print(f'{name}/{prio}/{preempt} released resource at {env.now}')

env = simpy.Environment()

res = simpy.PreemptiveResource(env, capacity=1)

A = env.process(user('A', env, res, prio=0, preempt=True))

env.run(until=1)  # Give A a head start

B = env.process(user('B', env, res, prio=-2, preempt=False))
C = env.process(user('C', env, res, prio=-1, preempt=True))

env.run()

