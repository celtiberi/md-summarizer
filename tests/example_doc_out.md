# <a name="transitions-module"></a> transitions

## Installation

Install `transitions` via pip:

```
pip install transitions
```

Or, install from GitHub clone:

```
python setup.py install
```

---

## Table of Contents

- Quickstart: Provides a fast way to get started.
- Non-Quickstart: Detailed documentation including concepts, initialization, and advanced features.
  - Key Concepts: Fundamental ideas and principles.
  - Basic Initialization: How to set up the system.
    ```python
    machine = SomeMachine()
    ```
  - States: Define and manage states.
    - Callbacks: Functions called at state changes.
    - Checking State: Verify current state.
      ```python
      machine.is_state_A()
      ```
    - Enumerations: Use enums for states.
  - Transitions: Manage state changes.
    - Triggering: How to initiate a transition.
      ```python
      machine.trigger('event_name')
      ```
    - Automatic: Transitions that occur without external triggers.
    - Multiple States: Transition from several states using the same event.
    - Reflexive: Transition within the same state.
    - Internal: Changes within a state that don't trigger a transition.
    - Ordered: Sequential transitions.
    - Queued: Manage transitions in a queue.
    - Conditional: Transitions based on conditions.
    - Check: Verify if a transition can occur.
    - Callbacks: Functions executed during transitions.
  - Callable Resolution: How functions are resolved.
  - Callback Execution Order: Sequence of callback execution.
  - Passing Data: How to pass data between states.
  - Alternative Initialization Patterns: Different ways to initialize.
  - Logging: How to log state changes and events.
  - (Re-)Storing Machine Instances: Saving and restoring state machines.
  - Typing Support: Type annotations and checks.
  - Extensions: Additional features and integrations.
    - Hierarchical State Machine: Support for nested states.
    - Diagrams: Visual representation of state machines.
    - Threading: Multi-threading support.
    - Async: Asynchronous operations.
    - State Features: Enhanced state functionalities.
    - Django: Integration with Django framework.
  - Bug Reports: How to report issues.

---

## Quickstart

Example demonstrating a state machine in a `NarcolepticSuperhero` class using the `transitions` library. The class includes states like 'asleep', 'hanging out', and 'saving the world', with transitions such as waking up, working out, and saving kittens. The state machine is initialized with these states and transitions, allowing the superhero to change states based on actions like `wake_up`, `work_out`, and `distress_call`. The example also shows handling conditions with the `is_exhausted` method and updating a journal after completing missions.

```python
from transitions import Machine
import random

class NarcolepticSuperhero(object):
    states = ['asleep', 'hanging out', 'hungry', 'sweaty', 'saving the world']

    def __init__(self, name):
        self.name = name
        self.kittens_rescued = 0
        self.machine = Machine(model=self, states=NarcolepticSuperhero.states, initial='asleep')
        self.machine.add_transition(trigger='wake_up', source='asleep', dest='hanging out')
        self.machine.add_transition('work_out', 'hanging out', 'hungry')
        self.machine.add_transition('eat', 'hungry', 'hanging out')
        self.machine.add_transition('distress_call', '*', 'saving the world', before='change_into_super_secret_costume')
        self.machine.add_transition('complete_mission', 'saving the world', 'sweaty', after='update_journal')
        self.machine.add_transition('clean_up', 'sweaty', 'asleep', conditions=['is_exhausted'])
        self.machine.add_transition('clean_up', 'sweaty', 'hanging out')
        self.machine.add_transition('nap', '*', 'asleep')

    def update_journal(self):
        self.kittens_rescued += 1

    @property
    def is_exhausted(self):
        return random.random() < 0.5

    def change_into_super_secret_costume(self):
        print("Beauty, eh?")
```

Usage example:

```python
batman = NarcolepticSuperhero("Batman")
batman.state  # 'asleep'
batman.wake_up()
batman.state  # 'hanging out'
batman.nap()
batman.state  # 'asleep'
batman.clean_up()  # MachineError: "Can't trigger event clean_up from state asleep!"
batman.wake_up()
batman.work_out()
batman.state  # 'hungry'
batman.kittens_rescued  # 0
batman.distress_call()  # 'Beauty, eh?'
batman.state  # 'saving the world'
batman.complete_mission()
batman.state  # 'sweaty'
batman.clean_up()
batman.state  # 'asleep' (Too tired to shower)
batman.kittens_rescued  # 1
```

The example concludes with a visualization of the `NarcolepticSuperhero` state machine, suggesting the use of diagrams for better understanding.

---

## The non-quickstart

### Some key concepts

- **State**: Represents a condition or stage in the state machine, indicating behavior or process phase.

- **Transition**: The event causing the state machine to change states.

- **Model**: The structure that updates during transitions, may define actions for transitions or state changes.

- **Machine**: Manages the model, states, transitions, and actions, orchestrating the state machine process.

- **Trigger**: Event initiating a transition.

- **Action**: Operation performed during state changes or transitions, implemented via callbacks.

---

### Basic initialization

Initialize a state machine for an object `lump` of class `Matter` with states `solid`, `liquid`, `gas`, `plasma`, and set the initial state to `solid`:

```python
from transitions import Machine
class Matter(object):
    pass

lump = Matter()
machine = Machine(model=lump, states=['solid', 'liquid', 'gas', 'plasma'], initial='solid')
```

Alternatively, use the `Machine` instance itself as a model if no model is explicitly provided:

```python
machine = Machine(states=['solid', 'liquid', 'gas', 'plasma'], initial='solid')
```

To make the state machine functional, define transitions between states:

```python
states=['solid', 'liquid', 'gas', 'plasma']
transitions = [
    { 'trigger': 'melt', 'source': 'solid', 'dest': 'liquid' },
    { 'trigger': 'evaporate', 'source': 'liquid', 'dest': 'gas' },
    { 'trigger': 'sublimate', 'source': 'solid', 'dest': 'gas' },
    { 'trigger': 'ionize', 'source': 'gas', 'dest': 'plasma' }
]
machine = Machine(lump, states=states, transitions=transitions, initial='liquid')
```

Change the state by calling the generated methods or the `trigger()` method with the transition name:

```python
lump.evaporate()
lump.trigger('ionize')
```

---

#### <a name="state-callbacks"></a>Callbacks

States in a state machine can have `enter` and `exit` callbacks, specified during initialization or added later. These callbacks execute actions when entering or exiting states. Dynamically created methods `on_enter_«state name»` and `on_exit_«state name»` allow adding callbacks after initialization. Callbacks won't fire upon initial state entry unless explicitly triggered. Callbacks can also be defined within the model class for clarity. Additionally, `on_final` callbacks trigger when entering a final state.

```python
class Matter(object):
    def say_hello(self): print("hello, new state!")
    def say_goodbye(self): print("goodbye, old state!")

lump = Matter()

states = [
    State(name='solid', on_exit=['say_goodbye']),
    'liquid',
    { 'name': 'gas', 'on_exit': ['say_goodbye']}
]

machine = Machine(lump, states=states)
machine.add_transition('sublimate', 'solid', 'gas')
machine.on_enter_gas('say_hello')

machine.set_state('solid')
lump.sublimate()
#### >>> 'goodbye, old state!'
#### >>> 'hello, new state!'
```

```python
from transitions import Machine, State

states = [State(name='idling'),
          State(name='rescuing_kitten'),
          State(name='offender_gone', final=True),
          State(name='offender_caught', final=True)]

transitions = [["called", "idling", "rescuing_kitten"],
               {"trigger": "intervene", "source": "rescuing_kitten", "dest": "offender_gone", "conditions": "offender_is_faster"},
               ["intervene", "rescuing_kitten", "offender_caught"]]

class FinalSuperhero(object):
    def __init__(self, speed):
        self.machine = Machine(self, states=states, transitions=transitions, initial="idling", on_final="claim_success")
        self.speed = speed

    def offender_is_faster(self, offender_speed):
        return self.speed < offender_speed

    def claim_success(self, **kwargs):
        print("The kitten is safe.")

hero = FinalSuperhero(speed=10)
hero.called()
hero.intervene(offender_speed=15)
#### >>> 'The kitten is safe'
```

---

#### <a name="checking-state"></a>Checking state

To check a model's state, use `.state` or `is_«state name»()`. Retrieve the state object with `Machine.get_state()`. Customize the state attribute and related method names by specifying `model_attribute` during initialization, affecting `is_«model_attribute»_«state name»()` and `to_«model_attribute»_«state name»()` methods.

```python
lump.state
lump.is_gas()
lump.is_solid()
machine.get_state(lump.state).name

lump = Matter()
machine = Machine(lump, states=['solid', 'liquid', 'gas'], model_attribute='matter_state', initial='solid')
lump.matter_state
lump.is_matter_state_solid()
lump.to_matter_state_gas()
```

---

#### <a name="enum-state"></a>Enumerations

Using enumerations with the `transitions` library enhances type safety and IDE support, making state names more manageable. Install `enum34` for Python 2.7 compatibility. Enums and strings can be mixed in state definitions, but duplicate names are not allowed.

```python
import enum
from transitions import Machine

class States(enum.Enum):
    ERROR = 0
    RED = 1
    YELLOW = 2
    GREEN = 3

transitions = [['proceed', States.RED, States.YELLOW],
               ['proceed', States.YELLOW, States.GREEN],
               ['error', '*', States.ERROR]]

m = Machine(states=States, transitions=transitions, initial=States.RED)
assert m.is_RED()
assert m.state is States.RED
state = m.get_state(States.RED)
print(state.name)  # >>> RED
m.proceed()
m.proceed()
assert m.is_GREEN()
m.error()
assert m.state is States.ERROR
```

---

#### <a name="triggers"></a>Triggering a transition

To execute a transition, use one of two methods:

1. Call the transition directly using its name, which is automatically bound to the model:
```python
>>> lump.melt()
>>> lump.state
'liquid'
>>> lump.evaporate()
>>> lump.state
'gas'
```
Avoid naming conflicts between your model methods and transition names.

2. Use the `trigger` method with the transition name as an argument for dynamic triggering:
```python
>>> lump.trigger('melt')
>>> lump.state
'liquid'
>>> lump.trigger('evaporate')
>>> lump.state
'gas'
```

---

#### Triggering invalid transitions

Triggering an invalid transition in a state machine raises an exception by default. To prevent this, set `ignore_invalid_triggers=True` globally, for a group of states, or for a specific state:

```python
#### Globally
m = Machine(lump, states, initial='solid', ignore_invalid_triggers=True)
#### For a group of states
states = ['new_state1', 'new_state2']
m.add_states(states, ignore_invalid_triggers=True)
#### For a single state
states = [State('A', ignore_invalid_triggers=True), 'B', 'C']
m = Machine(lump, states)
#### Inverting behavior for a single state
states = ['A', 'B', State('C')]
m = Machine(lump, states, ignore_invalid_triggers=True)
```

To identify valid transitions from a state, use `get_triggers`:

```python
m.get_triggers('solid')
m.get_triggers('liquid')
m.get_triggers('plasma')
m.get_triggers('solid', 'liquid', 'gas', 'plasma')
```

`get_triggers` may return additional `auto-transitions` not explicitly defined, which are covered in the next section.

---

#### <a name="automatic-transitions-for-all-states"></a>Automatic transitions for all states

A `to_«state»()` method is auto-created for each state in a `Machine`, allowing transitions to that state from any other. Disable with `auto_transitions=False`.

```python
lump.to_liquid()
lump.state
>>> 'liquid'
lump.to_solid()
lump.state
>>> 'solid'
```

---

#### <a name="transitioning-from-multiple-states"></a>Transitioning from multiple states

A trigger can be linked to multiple transitions, including those starting or ending in the same state. For example, `transmogrify()` changes the model's state from `'plasma'` to `'solid'`, or to `'plasma'` from `'solid'`, `'liquid'`, or `'gas'`, with only the first matching transition executing.

```python
machine.add_transition('transmogrify', ['solid', 'liquid', 'gas'], 'plasma')
machine.add_transition('transmogrify', 'plasma', 'solid')
```

To transition from any state to a specific one, use the wildcard `'*'`:

```python
machine.add_transition('to_liquid', '*', 'liquid')
```

Wildcard transitions don't affect states added after the transition definition, resulting in an invalid transition message if attempted.

---

#### <a name="reflexive-from-multiple-states"></a>Reflexive transitions from multiple states

Add reflexive triggers to multiple states using `=` as the destination. Example:

```python
machine.add_transition('touch', ['liquid', 'gas', 'plasma'], '=', after='change_shape')
```

This adds `touch()` as a reflexive trigger for 'liquid', 'gas', and 'plasma' states, executing `change_shape` afterwards.

---

#### <a name="internal-transitions"></a>Internal transitions

Internal transitions remain within the same state, not triggering `exit` or `enter` callbacks, but still process `before` and `after` callbacks. Define an internal transition by setting the destination to `None`.

```python
machine.add_transition('internal', ['liquid', 'gas'], None, after='change_shape')
```

---

#### <a name="ordered-transitions"></a> Ordered transitions

To implement strict linear state transitions in Transitions, use the `add_ordered_transitions()` method of the `Machine` class. This method allows for specifying a sequence of states and optional conditions for transitions. By default, transitions loop from the last state back to the first. Conditions can be a single condition applied to all transitions or a list matching the number of transitions. Disabling looping is possible with `loop=False`, which requires one less condition if conditions are specified.

Examples:

```python
states = ['A', 'B', 'C']
machine = Machine(states=states, initial='A')
machine.add_ordered_transitions()
print(machine.state)  # 'B'

machine.add_ordered_transitions(['A', 'C', 'B'])
print(machine.state)  # 'C'

machine.add_ordered_transitions(conditions='check')
machine.add_ordered_transitions(conditions=['check_A2B', ..., 'check_X2A'])

machine.add_ordered_transitions(loop=False)
machine.next_state()
machine.next_state()
machine.next_state()  # MachineError: "Can't trigger event next_state from state C!"
```

---

#### <a name="queued-transitions"></a>Queued transitions

Transitions process events instantly by default, executing `on_enter` methods before `after` callbacks. This can lead to unexpected execution order:

```python
def go_to_C():
    global machine
    machine.to_C()

def after_advance():
    print("I am in state B now!")

def entering_C():
    print("I am in state C now!")

states = ['A', 'B', 'C']
machine = Machine(states=states, initial='A')
machine.add_transition('advance', 'A', 'B', after=after_advance)
machine.on_enter_B(go_to_C)
machine.on_enter_C(entering_C)
machine.advance()
```

Execution order without queued processing: `prepare -> before -> on_enter_B -> on_enter_C -> after`.

Enabling queued processing ensures a transition finishes before the next starts, correcting the execution order:

```python
machine = Machine(states=states, queued=True, initial='A')
machine.advance()
```

Execution order with queued processing: `prepare -> before -> on_enter_B -> queue(to_C) -> after -> on_enter_C`.

With queued processing, trigger calls always return `True`, regardless of transition success:

```python
machine.add_transition('jump', 'A', 'C', conditions='will_fail')
machine.jump()  # Returns False if queued=False, True if queued=True
```

Removing a model from the machine also clears related queued events:

```python
class Model:
    def on_enter_B(self):
        self.to_C()
        self.machine.remove_model(self)
```

---

#### <a name="conditional-transitions"></a>Conditional transitions

Use the `conditions` argument with methods to control transitions based on conditions. Combine methods in a list for multiple conditions.

```python
class Matter(object):
    def is_flammable(self): return False
    def is_really_hot(self): return True

machine.add_transition('heat', 'solid', 'gas', conditions='is_flammable')
machine.add_transition('heat', 'solid', 'liquid', conditions=['is_really_hot'])
```

Use the `unless` argument for inverted conditions.

```python
machine.add_transition('heat', 'solid', 'gas', unless=['is_flammable', 'is_really_hot'])
```

Condition methods can receive optional arguments from the triggering call.

```python
lump.heat(temp=74)
```

---

#### <a name="check-transitions"></a>Check transitions

Use `may_<trigger_name>` or `may_trigger("trigger_name")` to check if a transition can occur before executing it. This evaluates `prepare` callbacks and conditions for transitions.

```python
if lump.may_heat():
    lump.heat()
```

Transition checks are useful even if the transition's destination isn't set up yet.

```python
machine.add_transition('elevate', 'solid', 'spiritual')
assert not lump.may_elevate()
assert not lump.may_trigger("elevate")
```

---

#### <a name="transition-callbacks"></a>Callbacks

Callbacks can be attached to transitions in a state machine, allowing for methods to be called before (`'before'`), after (`'after'`), or during (`'prepare'`) a transition. The `'prepare'` callback occurs before conditions are checked. Callbacks can also be set to run before or after every transition using `before_state_change` and `after_state_change` during machine initialization. Additionally, `prepare_event` and `finalize_event` callbacks execute once before any transitions and regardless of their success, respectively. Errors during callbacks can be handled using `on_exception`.

```python
class Matter(object):
    def make_hissing_noises(self): print("HISSSSSSSSSSSSSSSS")
    def disappear(self): print("where'd all the liquid go?")
    def count_attempts(self): self.attempts += 1
    def heat_up(self): self.heat = random.random() < 0.25
    def stats(self): print('It took you %i attempts to melt the lump!' %self.attempts)
    def raise_error(self, event): raise ValueError("Oh no")
    def handle_error(self, event): print("Fixing things ...")
    def prepare(self, event): print("I am ready!")
    def finalize(self, event): print("Result: ", type(event.error), event.error)

transitions = [
    { 'trigger': 'melt', 'source': 'solid', 'dest': 'liquid', 'before': 'make_hissing_noises'},
    { 'trigger': 'evaporate', 'source': 'liquid', 'dest': 'gas', 'after': 'disappear' },
    { 'trigger': 'melt', 'source': 'solid', 'dest': 'liquid', 'prepare': ['heat_up', 'count_attempts'], 'conditions': 'is_really_hot', 'after': 'stats'},
]

lump = Matter()
machine = Machine(lump, states, transitions=transitions, initial='solid', before_state_change='make_hissing_noises', after_state_change='disappear', prepare_event='prepare', finalize_event='finalize', on_exception='handle_error', send_event=True)
```

---

### <a name="resolution"></a>Callable resolution

Pass callables to states, conditions, and transitions by name. `transitions` retrieves callables by name from the model or imports them if the name includes dots. Properties or attributes can also be used but won't receive event data. Directly passing callables or lists/tuples of callable names is supported. Callbacks execute in the order added.

```python
from transitions import Machine
from mod import imported_func
import random

class Model(object):
    def a_callback(self):
        imported_func()

    @property
    def a_property(self):
        return random.random() < 0.5

    an_attribute = False

model = Model()
machine = Machine(model=model, states=['A'], initial='A')
machine.add_transition('by_name', 'A', 'A', conditions='a_property', after='a_callback')
machine.add_transition('by_reference', 'A', 'A', unless=['a_property', 'an_attribute'], after=model.a_callback)
machine.add_transition('imported', 'A', 'A', after='mod.imported_func')

model.by_name()
model.by_reference()
model.imported()
```

Override `Machine.resolve_callable` for complex callable resolution strategies.

```python
class CustomMachine(Machine):
    @staticmethod
    def resolve_callable(func, event_data):
        super(CustomMachine, CustomMachine).resolve_callable(func, event_data)
```

---

### <a name="execution-order"></a>Callback execution order

Trigger events in three ways: `lump.melt()`, `lump.trigger("melt")`, and `machine.dispatch("melt")`. Callback execution order during transitions:

1. `'machine.prepare_event'` - Before transitions, once.
2. `'transition.prepare'` - At transition start.
3. `'transition.conditions'` and `'transition.unless'` - May halt transition.
4. `'machine.before_state_change'`, `'transition.before'`, `'state.on_exit'` - Before state change.
5. `<STATE CHANGE>`
6. `'state.on_enter'`, `'transition.after'`, `'machine.on_final'`, `'machine.after_state_change'` - After state change.
7. `'machine.on_exception'`, `'machine.finalize_event'` - On exceptions or after all transitions.

Exceptions during callbacks halt further processing. Callbacks in `'machine.finalize_event'` always execute unless the exception is within. Blocking callbacks halt execution; for parallel execution, consider `AsyncMachine` or `LockedMachine`.

---

### <a name="passing-data"></a>Passing data

Transitions allows passing data to callback functions in two ways. Directly pass positional or keyword arguments to trigger methods:

```python
class Matter(object):
    def __init__(self): self.set_environment()
    def set_environment(self, temp=0, pressure=101.325):
        self.temp = temp
        self.pressure = pressure
    def print_temperature(self): print("Current temperature is %d degrees celsius." % self.temp)
    def print_pressure(self): print("Current pressure is %.2f kPa." % self.pressure)

lump = Matter()
machine = Machine(lump, ['solid', 'liquid'], initial='solid')
machine.add_transition('melt', 'solid', 'liquid', before='set_environment')

lump.melt(45)  # positional arg
lump.print_temperature()
lump.melt(pressure=300.23)  # keyword arg
lump.print_pressure()
```

However, all callbacks must handle all arguments, which can be limiting. Alternatively, use `send_event=True` to wrap arguments in an `EventData` instance, providing access to event details and allowing callbacks to selectively access arguments:

```python
class Matter(object):
    def __init__(self): self.temp = 0; self.pressure = 101.325
    def set_environment(self, event):
        self.temp = event.kwargs.get('temp', 0)
        self.pressure = event.kwargs.get('pressure', 101.325)
    def print_pressure(self): print("Current pressure is %.2f kPa." % self.pressure)

lump = Matter()
machine = Machine(lump, ['solid', 'liquid'], send_event=True, initial='solid')
machine.add_transition('melt', 'solid', 'liquid', before='set_environment')

lump.melt(temp=45, pressure=1853.68)
lump.print_pressure()
```

---

### <a name="alternative-initialization-patterns"></a>Alternative initialization patterns

Transitions library supports various initialization patterns for state machines:

1. Standalone state machine without a separate model:
```python
machine = Machine(states=states, transitions=transitions, initial='solid')
machine.melt()
machine.state
>>> 'liquid'
```

2. Model inheriting from `Machine` class, allowing state logic to be part of the model:
```python
class Matter(Machine):
    def __init__(self):
        states = ['solid', 'liquid', 'gas']
        Machine.__init__(self, states=states, initial='solid')
        self.add_transition('melt', 'solid', 'liquid')

lump = Matter()
lump.melt()
lump.state
>>> 'liquid'
```

3. Handling multiple models by passing them as a list or dynamically adding/removing them:
```python
machine = Machine(model=None, states=states, transitions=transitions, initial='solid')
machine.add_model(lump1)
machine.add_model(lump2, initial='liquid')
machine.dispatch("to_plasma")
machine.remove_model([lump1, lump2])
```

4. If no initial state is provided, a default `'initial'` state is created. Use `initial=None` to avoid this and specify the initial state when adding a model:
```python
machine = Machine(model=None, states=states, transitions=transitions, initial=None)
machine.add_model(Matter(), initial='liquid')
```

5. Multiple machines can be attached to a single model using different `model_attribute` values for separate state fields:
```python
matter_machine = Machine(lump, states=['solid', 'liquid', 'gas'], initial='solid', model_attribute='state')
shipment_machine = Machine(lump, states=['delivered', 'shipping'], initial='delivered', model_attribute='shipping_state')
```

---

### Logging

Transitions library supports basic logging for events like state changes and transition triggers using Python's `logging` module. Configure logging to output at INFO level for transitions-specific events, excluding DEBUG messages:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('transitions').setLevel(logging.INFO)
```

---

### <a name="restoring"></a>(Re-)Storing machine instances

Machines can be serialized using `pickle`, but `dill` is needed for Python 3.3 or earlier.

```python
import dill as pickle # for Python 3.3 and earlier

m = Machine(states=['A', 'B', 'C'], initial='A')
m.to_B()

### Serialize
dump = pickle.dumps(m)

### Deserialize
m2 = pickle.loads(dump)
```

---

### <a name="typing-support"></a> Typing support

`transitions` allows dynamic model handling, but static type checkers may not recognize runtime attributes and methods. Use `model_override=True` in the machine constructor to prevent `transitions` from adding new methods or overriding existing ones unless explicitly allowed.

```python
from transitions import Machine

class Model:
    pass

model = Model()
default_machine = Machine(model, states=["A", "B"], transitions=[["go", "A", "B"]], initial="A")

class PredefinedModel:
    state: str

    def go(self) -> bool:
        raise RuntimeError("Should be overridden!")

    def trigger(self, trigger_name: str) -> bool:
        raise RuntimeError("Should be overridden!")

model = PredefinedModel()
override_machine = Machine(model, states=["A", "B"], transitions=[["go", "A", "B"]], initial="A", model_override=True)
```

For complex models with callbacks, use `generate_base_model` to create a base model from a machine configuration.

```python
from transitions.experimental.utils import generate_base_model

simple_config = {
    "states": ["A", "B"],
    "transitions": [["go", "A", "B"]],
    "initial": "A",
    "before_state_change": "call_this",
    "model_override": True,
} 

class_definition = generate_base_model(simple_config)
### Save class_definition to "base_model.py"

from transitions import Machine
from base_model import BaseModel

class Model(BaseModel):
    def call_this(self) -> None:
        pass

model = Model()
machine = Machine(model, **simple_config)
```

To simplify model and transition definitions, use enums for states and `add_transitions` or `event` decorators for transitions. A custom Machine class with `with_model_definitions` is required for transitions to recognize these definitions.

```python
from enum import Enum
from transitions.experimental.utils import with_model_definitions, event, add_transitions, transition
from transitions import Machine

class State(Enum):
    A = "A"
    B = "B"
    C = "C"

class Model:
    state: State = State.A

    @add_transitions(transition(source=State.A, dest=State.B), [State.C, State.A])
    @add_transitions({"source": State.B,  "dest": State.A})
    def foo(self): ...

    bar = event(
        {"source": State.B, "dest": State.A, "conditions": lambda: False},
        transition(source=State.B, dest=State.C)
    )

@with_model_definitions
class MyMachine(Machine):
    pass

model = Model()
machine = MyMachine(model, states=State, initial=model.state)
```

---

##### Reuse of previously created HSMs

Nested states in `HierarchicalMachine` are referenced since version 0.8.0, allowing shared changes across instances, but models and their states remain unshared. Events and transitions are also referenced, sharing them between instances unless `remap` is used to specify different behavior for shared states.

```python
count_states = ['1', '2', '3', 'done']
count_trans = [
    ['increase', '1', '2'],
    ['increase', '2', '3'],
    ['decrease', '3', '2'],
    ['decrease', '2', '1'],
    ['done', '3', 'done'],
    ['reset', '*', '1']
]

counter = HierarchicalMachine(states=count_states, transitions=count_trans, initial='1')
states = ['waiting', 'collecting', {'name': 'counting', 'children': counter}]
transitions = [
    ['collect', '*', 'collecting'],
    ['wait', '*', 'waiting'],
    ['count', 'collecting', 'counting']
]

collector = HierarchicalMachine(states=states, transitions=transitions, initial='waiting')
collector.collect()
collector.count()
collector.increase()
collector.increase()
collector.done()
collector.wait()
```

To change the initial state of a nested machine or to make it return to a super state after completion, use `initial` and `remap` respectively.

```python
states = ['waiting', 'collecting', {'name': 'counting', 'children': counter, 'remap': {'done': 'waiting'}}]
```

For pre-0.8.0 behavior or unique state instances, deep copies of states and events can be used with `NestedState`.

```python
from transitions.extensions.nesting import NestedState
from copy import deepcopy

counting_state = NestedState(name="counting", initial='1')
counting_state.states = deepcopy(counter.states)
counting_state.events = deepcopy(counter.events)

states = ['waiting', 'collecting', counting_state]
```

Configuration-based state machine definitions are recommended for complex setups, supporting JSON or YAML for storage and loading. `HierarchicalMachine` accepts `children` or `states` for defining substates, prioritizing `children`.

```python
counter_conf = {
    'name': 'counting',
    'states': ['1', '2', '3', 'done'],
    'transitions': [
        ['increase', '1', '2'],
        ['increase', '2', '3'],
        ['decrease', '3', '2'],
        ['decrease', '2', '1'],
        ['done', '3', 'done'],
        ['reset', '*', '1']
    ],
    'initial': '1'
}

collector_conf = {
    'name': 'collector',
    'states': ['waiting', 'collecting', counter_conf],
    'transitions': [
        ['collect', '*', 'collecting'],
        ['wait', '*', 'waiting'],
        ['count', 'collecting', 'counting']
    ],
    'initial': 'waiting'
}

collector = HierarchicalMachine(**collector_conf)
collector.collect()
collector.count()
collector.increase()
assert collector.is_counting_2()
```

---

#### <a name="diagrams"></a> Diagrams

Keywords:
- `title`: Optional image title.
- `show_conditions`: Shows conditions on transitions (False by default).
- `show_auto_transitions`: Includes auto transitions (False by default).
- `show_state_attributes`: Displays callbacks, tags, and timeouts (False by default).

Transitions can create state diagrams using mermaid syntax, compatible with mermaid's live editor and markdown in GitLab/GitHub. Example code:
```python
from transitions.extensions.diagrams import HierarchicalGraphMachine
import pyperclip

states = ['A', 'B', {'name': 'C', 'final': True, 'parallel': [{'name': '1', 'children': ['a', {"name": "b", "final": True}], 'initial': 'a', 'transitions': [['go', 'a', 'b']]}, {'name': '2', 'children': ['a', {"name": "b", "final": True}], 'initial': 'a', 'transitions': [['go', 'a', 'b']]}]}]
transitions = [['reset', 'C', 'A'], ["init", "A", "B"], ["do", "B", "C"]]

m = HierarchicalGraphMachine(states=states, transitions=transitions, initial="A", show_conditions=True, title="Mermaid", graph_engine="mermaid", auto_transitions=False)
m.init()

pyperclip.copy(m.get_graph().draw(None))
print("Graph copied to clipboard!")
```
Produces a mermaid diagram.

For advanced graphing, install `graphviz` and/or `pygraphviz`:
- Ubuntu/Debian: `sudo apt-get install graphviz graphviz-dev`
- MacOS: `brew install graphviz`
- (Ana)conda: `conda install graphviz python-graphviz`

Then, install Python packages:
```bash
pip install graphviz pygraphviz
pip install transitions[diagrams]
```

`GraphMachine` uses `pygraphviz` if available, otherwise `graphviz`, with a fallback to `mermaid`. Override with `graph_engine="graphviz"` or `"mermaid"`. Example usage:
```python
from transitions.extensions import GraphMachine
m = Model()
machine = GraphMachine(model=m, show_auto_transitions=True, ...)

m.get_graph().draw('my_state_diagram.png', prog='dot')
```

Drawing accepts file descriptors or binary streams:
```python
import io

with open('a_graph.png', 'bw') as f:
    m.get_graph().draw(f, format="png", prog='dot')

b = io.BytesIO()
m.get_graph().draw(b, format="png", prog='dot')

result = m.get_graph().draw(None, format="png", prog='dot')
```

References in callbacks are resolved as possible:
```python
from transitions.extensions import GraphMachine
from functools import partial

class Model:
    def clear_state(self, deep=False, force=False):
        return True

model = Model()
machine = GraphMachine(model=model, states=['A', 'B', 'C'], transitions=[{'trigger': 'clear', 'source': 'B', 'dest': 'A', 'conditions': model.clear_state}, {'trigger': 'clear', 'source': 'C', 'dest': 'A', 'conditions': partial(model.clear_state, False, force=True)}], initial='A', show_conditions=True)

model.get_graph().draw('my_state_diagram.png', prog='dot')
```

Override `GraphMachine.format_references` to customize or skip reference formatting. See IPython/Jupyter notebooks in examples for detailed usage.

---

#### <a name="threading"></a> Threadsafe(-ish) State Machine

Use `LockedMachine` or `LockedHierarchicalMachine` for thread-safe event dispatching, protecting function access with reentrant locks. Direct manipulation of member variables can still corrupt the state machine.

Example of thread-safe state transition:
```python
from transitions.extensions import LockedMachine
from threading import Thread
import time

states = ['A', 'B', 'C']
machine = LockedMachine(states=states, initial='A')

thread = Thread(target=machine.to_B)
thread.start()
time.sleep(0.01)
machine.to_C()
```
Direct attribute access is not thread-safe:
```python
thread = Thread(target=machine.to_B)
thread.start()
machine.new_attrib = 42
```
Custom context managers can be used with `machine_context` for `LockedMachine`:
```python
from transitions.extensions import LockedMachine
from threading import RLock

states = ['A', 'B', 'C']
lock1 = RLock()
lock2 = RLock()

machine = LockedMachine(states=states, initial='A', machine_context=[lock1, lock2])
```
Add per-model contexts using `model_context`:
```python
lock3 = RLock()
machine.add_model(model, model_context=lock3)
```
Ensure all custom context managers are re-entrant.

---

#### <a name="async"></a> Using async callbacks

`AsyncMachine` in Python 3.7+ allows mixing synchronous and asynchronous callbacks, requiring manual event loop management. It uses `contextvars` for handling callbacks during ongoing transitions, which is not possible in earlier Python versions. The example demonstrates asynchronous and synchronous callbacks within state transitions, emphasizing the need for awaiting events and handling the event loop.

```python
from transitions.extensions.asyncio import AsyncMachine
import asyncio
import time

class AsyncModel:
    def prepare_model(self):
        print("I am synchronous.")
        self.start_time = time.time()

    async def before_change(self):
        print("I am asynchronous and will block now for 100 milliseconds.")
        await asyncio.sleep(0.1)
        print("I am done waiting.")

    def sync_before_change(self):
        print("I am synchronous and will block the event loop (what I probably shouldn't)")
        time.sleep(0.1)
        print("I am done waiting synchronously.")

    def after_change(self):
        print(f"I am synchronous again. Execution took {int((time.time() - self.start_time) * 1000)} ms.")

transition = dict(trigger="start", source="Start", dest="Done", prepare="prepare_model",
                  before=["before_change"] * 5 + ["sync_before_change"],
                  after="after_change")
model = AsyncModel()
machine = AsyncMachine(model, states=["Start", "Done"], transitions=[transition], initial='Start')

asyncio.get_event_loop().run_until_complete(model.start())
assert model.is_Done()
```

`AsyncMachine` supports model-specific queue modes, affecting event processing order. Events are queued per model or globally, with exceptions clearing only the affected model's queue. Queue mode cannot be changed post-construction.

```python
asyncio.gather(model1.event1(), model1.event2(), model2.event1())
#### AsyncMachine(queued=True): model1.event1 -> model1.event2 -> model2.event1
#### AsyncMachine(queued='model'): (model1.event1, model2.event1) -> model1.event2

asyncio.gather(model1.event1(), model1.error(), model1.event3(), model2.event1(), model2.event2(), model2.event3())
#### AsyncMachine(queued=True): model1.event1 -> model1.error
#### AsyncMachine(queued='model'): (model1.event1, model2.event1) -> (model1.error, model2.event2) -> model2.event3
```

---

#### <a name="state-features"></a>Adding features to states

To add custom behavior to machine states, use decorators like `@add_state_features` with features such as `Tags` and `Timeout`. Here's an example with a custom state machine and a social superhero model:

```python
from time import sleep
from transitions import Machine
from transitions.extensions.states import add_state_features, Tags, Timeout

@add_state_features(Tags, Timeout)
class CustomStateMachine(Machine):
    pass

class SocialSuperhero(object):
    def __init__(self):
        self.entourage = 0

    def on_enter_waiting(self):
        self.entourage += 1

states = [{'name': 'preparing', 'tags': ['home', 'busy']},
          {'name': 'waiting', 'timeout': 1, 'on_timeout': 'go'},
          {'name': 'away'}]

transitions = [['done', 'preparing', 'waiting'],
               ['join', 'waiting', 'waiting'],
               ['go', 'waiting', 'away']]

hero = SocialSuperhero()
machine = CustomStateMachine(model=hero, states=states, transitions=transitions, initial='preparing')
sleep(0.7)
hero.join()
sleep(0.5)
hero.join()
sleep(2)
```

State features include:
- **Timeout**: Triggers an event after a set time. Use `timeout` for duration and `on_timeout` for the action.
- **Tags**: Adds tags to states, accessible via `State.is_<tag_name>`.
- **Error**: Raises a `MachineError` if a state can't be left, useful with `auto_transitions=False`.
- **Volatile**: Initializes an object each time a state is entered, with `volatile` for the class and `hook` for the attribute name.

Custom state classes can be created by inheriting from `State` and using them with `Machine` by setting `state_cls` or overriding `Machine.create_state`. For asynchronous machines, replace `Timeout` with `AsyncTimeout` to avoid threads:

```python
import asyncio
from transitions.extensions.states import add_state_features
from transitions.extensions.asyncio import AsyncTimeout, AsyncMachine

@add_state_features(AsyncTimeout)
class TimeoutMachine(AsyncMachine):
    pass

states = ['A', {'name': 'B', 'timeout': 0.2, 'on_timeout': 'to_C'}, 'C']
m = TimeoutMachine(states=states, initial='A', queued=True)
asyncio.run(asyncio.wait([m.to_B(), asyncio.sleep(0.1)]))
asyncio.run(asyncio.wait([m.to_B(), asyncio.sleep(0.3)]))
```

Use `queued=True` in `TimeoutMachine` to process events sequentially and avoid race conditions.

---

#### <a name="django-support"></a> Using transitions together with Django

For inspiration, see the [FAQ](examples/Frequently%20asked%20questions.ipynb) or explore `django-transitions` by Christian Ledermann on [Github](https://github.com/PrimarySite/django-transitions). Usage examples are available in [the documentation](https://django-transitions.readthedocs.io/en/latest/).

---

### <a name="bug-reports"></a>I have a [bug report/issue/question]...

Try `transitions` in a Jupyter notebook at [mybinder.org](https://mybinder.org/v2/gh/pytransitions/transitions/master?filepath=examples%2FPlayground.ipynb).

Report bugs on [GitHub](https://github.com/pytransitions/transitions).

Ask usage questions on Stack Overflow with the [`pytransitions` tag](https://stackoverflow.com/questions/tagged/pytransitions) and check the [extended examples](./examples).

Contact [Tal Yarkoni](mailto:tyarkoni@gmail.com) or [Alexander Neumann](mailto:aleneum@gmail.com) for other inquiries.

---