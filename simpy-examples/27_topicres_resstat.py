import simpy

def print_stats(u,at,res):
    print(f'{u}/{at} : {res.count} of {res.capacity} slots are allocated.')
    print(f'  Users: {res.users}')
    print(f'  Queued events: {res.queue}')

def user(u, res):
    print_stats(u, "bgn", res)
    with res.request() as req:
        print_stats(u, "req", res)
        yield req
        print_stats(u, "acq", res)
    print_stats(u, "rel", res)

env = simpy.Environment()
res = simpy.Resource(env, capacity=1)
procs = [env.process(user("1", res)), 
         env.process(user("2", res))]
env.run()
