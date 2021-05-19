import simpy

def inspector(env, issues):
    for issue in [simpy.PriorityItem('P2', '#0000-P2'),
                  simpy.PriorityItem('P0', '#0001-P0'),
                  simpy.PriorityItem('P3', '#0002-P3'),
                  simpy.PriorityItem('P1', '#0003-P1')]:
        yield env.timeout(1)
        print(env.now, 'log', issue)
        yield issues.put(issue)

def maintainer(env, issues):
    while True:
        yield env.timeout(3)
        issue = yield issues.get()
        print('  ', env.now, 'repair', issue)

env = simpy.Environment()

issues = simpy.PriorityStore(env)

_ = env.process(inspector(env, issues))
_ = env.process(maintainer(env, issues))

env.run()
