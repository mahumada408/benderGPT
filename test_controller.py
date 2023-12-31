import collections
import evdev
from queue import Queue

dev = evdev.InputDevice('/dev/input/event0')
events = Queue()
event_deque = collections.deque()


print("in loop")
for event in dev.read_loop():
  if event.type == evdev.ecodes.EV_KEY:
    print(evdev.categorize(event))
