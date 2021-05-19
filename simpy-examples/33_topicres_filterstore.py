import simpy

from collections import namedtuple

def user(name, env, ms, size):
    print(name, 'requesting machine of size', size)
    machine = yield ms.get(lambda machine: machine.size == size)
                # FilterStore lets you use a custom function 
                # to filter the objects you get out of the store
    print('  ', name, 'got', machine, 'at', env.now)
    yield env.timeout(machine.duration)
    yield ms.put(machine)
    print('    ', name, 'released', machine, 'at', env.now)

env = simpy.Environment()

Machine = namedtuple('Machine', 'size, duration')
m1 = Machine(1, 2)  # Small and slow
m2 = Machine(2, 1)  # Big and fast

machine_shop = simpy.FilterStore(env, capacity=2)
machine_shop.items = [m1, m2]  # Pre-populate the machine shop

users = [env.process(user(i, env, machine_shop, (i % 2) + 1))
         for i in range(3)]

env.run()
