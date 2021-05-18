import simpy

def resource_user(env, resource):
    request = resource.request()  # Generate a request event
    print('Waiting for resource at %d' % env.now)
    yield request                 # Wait for access
    print('Got resource at %d' % env.now)
    yield env.timeout(1)          # Do something
    print('Releasing resource at %d' % env.now)
    resource.release(request)     # Release the resource

env = simpy.Environment()
res = simpy.Resource(env, capacity=1)
user = env.process(resource_user(env, res))
env.run()
