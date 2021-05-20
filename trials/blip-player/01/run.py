import simpy

def segment_dispatcher(env):
    global g_dispatch_event
    while True:
        yield env.timeout(2)
        print(f"@{env.now} : dispatching segment event")
        g_dispatch_event.succeed()
        g_dispatch_event = env.event()

def segment_receiver(env):
    while True:
        yield g_dispatch_event
        print(f"@{env.now} : received segment event")


env = simpy.Environment()

g_dispatch_event = env.event()

env.process(segment_dispatcher(env))
env.process(segment_receiver(env))

env.run(until=10)


