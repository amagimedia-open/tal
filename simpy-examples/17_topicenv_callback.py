import simpy

def my_callback(event):
    print('Called back from', event)

def my_callback_2(event):
    print('Called back from', event)


env = simpy.Environment()

event = env.event()

event.callbacks.append(my_callback)
event.callbacks.append(my_callback_2)
print(event.callbacks)

