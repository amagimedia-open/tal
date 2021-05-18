import simpy

def resource_user(env, resource):
    with resource.request() as req:  # Generate a request event
        print('Waiting for resource at %d' % env.now)
        yield req                    # Wait for access
        print('Got resource at %d' % env.now)
        yield env.timeout(1)         # Do something
                                     # Resource released automatically
    print('Released resource via context manager at %d' % env.now)

env = simpy.Environment()
res = simpy.Resource(env, capacity=1)
user = env.process(resource_user(env, res))
env.run()
