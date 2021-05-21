#+---------------------------------------+
#| multiple producers multiple consumers |
#+---------------------------------------+

import simpy

def producer(id, env, store):
        item = f"p-{id}-item"
        print(f'Producer {id} Producing {item} at', env.now)
        yield store.put(f'{item}')

def consumer(id, env, store):
    while True:
        item = yield store.get()
        print(f'Consumer {id} consuming {item} at', env.now)
        yield env.timeout(1)

env = simpy.Environment()
store = simpy.Store(env, capacity=1)

consumers = [env.process(consumer(i, env, store)) for i in ["X", "Y"]]
producers = [env.process(producer(i, env, store)) for i in ["A", "B", "C"]]

env.run(until=12)



