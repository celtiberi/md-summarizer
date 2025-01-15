import pytest
from .utils.output_formatter import format_section, format_comparison
from .utils.assertions import assert_tokens_reduced
from md_summarizer import MarkdownSummarizer, ProgressStatus
import asyncio

@pytest.mark.asyncio
async def test_basic_summarization1(summarizer, setup_test_environment):
    """Test basic content summarization without sections."""  
    content = ASYNC_CALLBACK_SECTION_CONTENT
    
    # Show input
    format_section("INPUT", content)
    
    # Process content
    result = await summarizer.summarize(content)
    
    # Show output
    format_section("OUTPUT", result)
    
    
    format_comparison(content, result, summarizer.agent)
    # Run assertions
    assert result  # Result should not be empty
    assert_tokens_reduced(summarizer)

@pytest.mark.asyncio
async def test_basic_summarization2(summarizer, setup_test_environment):
    """Test basic content summarization without sections."""  
    content = NODE_GYP_CONTENT
    
    # Show input
    format_section("INPUT", content)
    
    # Process content
    result = await summarizer.summarize(content)
    
    # Show output
    format_section("OUTPUT", result)
    
    format_comparison(content, result, summarizer.agent)
    # Run assertions
    assert result  # Result should not be empty
    assert_tokens_reduced(summarizer)



@pytest.mark.asyncio
async def test_empty_content(summarizer):
    """Test handling of empty content."""
    content = ""
    
    # Process content
    result = await summarizer.summarize(content)
    
    assert result == ""

@pytest.mark.skip
@pytest.mark.asyncio
async def test_example_doc_summarization(summarizer, setup_test_environment):
    """Test summarization of example_doc.md."""
    # Read example doc
    with open('tests/example_doc.md', 'r') as f:
        content = f.read()

    # Show input
    format_section("INPUT", content)

    # Process content
    result = await summarizer.summarize(content)

    # Show output 
    format_section("OUTPUT", result)

    # Write output to file
    with open('tests/example_doc_out.md', 'w') as f:
        f.write(result)

    # Run assertions
    assert result  # Result should not be empty
    assert_tokens_reduced(summarizer)
    
    # Calculate and display reductions
    format_comparison(content, result, summarizer.agent)

@pytest.mark.asyncio
async def test_streaming_updates():
    """Test streaming updates from summarizer."""
    content = NODE_GYP_CONTENT
    summarizer = MarkdownSummarizer()
    
    # Track updates
    updates = []
    section_count = 0
    total_sections = None
    
    print("\n🔄 Streaming Updates:")
    print("-" * 50)
    
    async for update in summarizer.stream(content):
        updates.append(update)
        if update.status == ProgressStatus.STARTING:
            print(f"\nStatus: {update.status}, Total Sections: {update.total_sections}")
            # Verify we got total sections count
            total_sections = update.total_sections
            assert total_sections > 0
        elif update.status == ProgressStatus.SECTION_COMPLETE:
            print(f"\nStatus: {update.status}, Section: {update.section_title}")
            # Verify section title exists
            assert update.section_title is not None
            section_count += 1
        elif update.status == ProgressStatus.COMPLETE:
            print(f"\nStatus: {update.status}")
            print(update.content)
            # Verify final content
            assert update.content is not None
            assert len(update.content) > 0
            # Verify we processed all sections
            assert section_count == total_sections
        elif update.status == ProgressStatus.ERROR:
            print(f"\nStatus: {update.status}")
            pytest.fail(f"Unexpected error: {update.error}")
    
    # Verify update sequence
    assert len(updates) > 0
    assert updates[0].status == ProgressStatus.STARTING
    assert updates[-1].status == ProgressStatus.COMPLETE
    
    # Verify token reduction
    assert_tokens_reduced(summarizer)




################################################################################################



ASYNC_CALLBACK_SECTION_CONTENT = """

#### <a name="async"></a> Using async callbacks

If you are using Python 3.7 or later, you can use `AsyncMachine` to work with asynchronous callbacks.
You can mix synchronous and asynchronous callbacks if you like but this may have undesired side effects.
Note that events need to be awaited and the event loop must also be handled by you.

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
                  after="after_change")  # execute before function in asynchronously 5 times
model = AsyncModel()
machine = AsyncMachine(model, states=["Start", "Done"], transitions=[transition], initial='Start')

asyncio.get_event_loop().run_until_complete(model.start())
# >>> I am synchronous.
#     I am asynchronous and will block now for 100 milliseconds.
#     I am asynchronous and will block now for 100 milliseconds.
#     I am asynchronous and will block now for 100 milliseconds.
#     I am asynchronous and will block now for 100 milliseconds.
#     I am asynchronous and will block now for 100 milliseconds.
#     I am synchronous and will block the event loop (what I probably shouldn't)
#     I am done waiting synchronously.
#     I am done waiting.
#     I am done waiting.
#     I am done waiting.
#     I am done waiting.
#     I am done waiting.
#     I am synchronous again. Execution took 101 ms.
assert model.is_Done()
```

So, why do you need to use Python 3.7 or later you may ask.
Async support has been introduced earlier.
`AsyncMachine` makes use of `contextvars` to handle running callbacks when new events arrive before a transition
has been finished:

```python
async def await_never_return():
    await asyncio.sleep(100)
    raise ValueError("That took too long!")

async def fix():
    await m2.fix()

m1 = AsyncMachine(states=['A', 'B', 'C'], initial='A', name="m1")
m2 = AsyncMachine(states=['A', 'B', 'C'], initial='A', name="m2")
m2.add_transition(trigger='go', source='A', dest='B', before=await_never_return)
m2.add_transition(trigger='fix', source='A', dest='C')
m1.add_transition(trigger='go', source='A', dest='B', after='go')
m1.add_transition(trigger='go', source='B', dest='C', after=fix)
asyncio.get_event_loop().run_until_complete(asyncio.gather(m2.go(), m1.go()))

assert m1.state == m2.state
```

This example actually illustrates two things:
First, that 'go' called in m1's transition from `A` to be `B` is not cancelled and second, calling `m2.fix()` will
halt the transition attempt of m2 from `A` to `B` by executing 'fix' from `A` to `C`.
This separation would not be possible without `contextvars`.
Note that `prepare` and `conditions` are NOT treated as ongoing transitions.
This means that after `conditions` have been evaluated, a transition is executed even though another event already happened.
Tasks will only be cancelled when run as a `before` callback or later.

`AsyncMachine` features a model-special queue mode which can be used when `queued='model'` is passed to the constructor.
With a model-specific queue, events will only be queued when they belong to the same model.
Furthermore, a raised exception will only clear the event queue of the model that raised that exception.
For the sake of simplicity, let's assume that every event in `asyncio.gather` below is not triggered at the same time but slightly delayed:

```python
asyncio.gather(model1.event1(), model1.event2(), model2.event1())
# execution order with AsyncMachine(queued=True)
# model1.event1 -> model1.event2 -> model2.event1
# execution order with AsyncMachine(queued='model')
# (model1.event1, model2.event1) -> model1.event2

asyncio.gather(model1.event1(), model1.error(), model1.event3(), model2.event1(), model2.event2(), model2.event3())
# execution order with AsyncMachine(queued=True)
# model1.event1 -> model1.error
# execution order with AsyncMachine(queued='model')
# (model1.event1, model2.event1) -> (model1.error, model2.event2) -> model2.event3
```

Note that queue modes must not be changed after machine construction.
"""

NODE_GYP_CONTENT = """
# `node-gyp` - Node.js native addon build tool

[![Build Status](https://github.com/nodejs/node-gyp/workflows/Tests/badge.svg?branch=main)](https://github.com/nodejs/node-gyp/actions?query=workflow%3ATests+branch%3Amain)
![npm](https://img.shields.io/npm/dm/node-gyp)

`node-gyp` is a cross-platform command-line tool written in Node.js for
compiling native addon modules for Node.js. It contains a vendored copy of the
[gyp-next](https://github.com/nodejs/gyp-next) project that was previously used
by the Chromium team and extended to support the development of Node.js native
addons.

Note that `node-gyp` is _not_ used to build Node.js itself.

All current and LTS target versions of Node.js are supported. Depending on what version of Node.js is actually installed on your system
`node-gyp` downloads the necessary development files or headers for the target version. List of stable Node.js versions can be found on [Node.js website](https://nodejs.org/en/about/previous-releases).

## Features

 * The same build commands work on any of the supported platforms
 * Supports the targeting of different versions of Node.js

## Installation

> [!Important]
> Python >= v3.12 requires `node-gyp` >= v10

You can install `node-gyp` using `npm`:

``` bash
npm install -g node-gyp
```

Depending on your operating system, you will need to install:

### On Unix

   * [A supported version of Python](https://devguide.python.org/versions/)
   * `make`
   * A proper C/C++ compiler toolchain, like [GCC](https://gcc.gnu.org)

### On macOS

   * [A supported version of Python](https://devguide.python.org/versions/)
   * `Xcode Command Line Tools` which will install `clang`, `clang++`, and `make`.
     * Install the `Xcode Command Line Tools` standalone by running `xcode-select --install`. -- OR --
     * Alternatively, if you already have the [full Xcode installed](https://developer.apple.com/xcode/download/), you can install the Command Line Tools under the menu `Xcode -> Open Developer Tool -> More Developer Tools...`.


### On Windows

Install tools with [Chocolatey](https://chocolatey.org):
``` bash
choco install python visualstudio2022-workload-vctools -y
```

Or install and configure Python and Visual Studio tools manually:

  * Install the current [version of Python](https://devguide.python.org/versions/) from the
  [Microsoft Store](https://apps.microsoft.com/store/search?publisher=Python+Software+Foundation).

   * Install Visual C++ Build Environment: For Visual Studio 2019 or later, use the `Desktop development with C++` workload from [Visual Studio Community](https://visualstudio.microsoft.com/thank-you-downloading-visual-studio/?sku=Community).  For a version older than Visual Studio 2019, install [Visual Studio Build Tools](https://visualstudio.microsoft.com/thank-you-downloading-visual-studio/?sku=BuildTools) with the `Visual C++ build tools` option.

   If the above steps didn't work for you, please visit [Microsoft's Node.js Guidelines for Windows](https://github.com/Microsoft/nodejs-guidelines/blob/master/windows-environment.md#compiling-native-addon-modules) for additional tips.

   To target native ARM64 Node.js on Windows on ARM, add the components "Visual C++ compilers and libraries for ARM64" and "Visual C++ ATL for ARM64".

   To use the native ARM64 C++ compiler on Windows on ARM, ensure that you have Visual Studio 2022 [17.4 or later](https://devblogs.microsoft.com/visualstudio/arm64-visual-studio-is-officially-here/) installed.

It's advised to install following Powershell module: [VSSetup](https://github.com/microsoft/vssetup.powershell) using `Install-Module VSSetup -Scope CurrentUser`.
This will make Visual Studio detection logic to use more flexible and accessible method, avoiding Powershell's `ConstrainedLanguage` mode.

### Configuring Python Dependency

`node-gyp` requires that you have installed a [supported version of Python](https://devguide.python.org/versions/).
If you have multiple versions of Python installed, you can identify which version
`node-gyp` should use in one of the following ways:

1. by setting the `--python` command-line option, e.g.:

``` bash
node-gyp <command> --python /path/to/executable/python
```

2. If `node-gyp` is called by way of `npm`, *and* you have multiple versions of
Python installed, then you can set the `npm_config_python` environment variable
to the appropriate path:
``` bash
export npm_config_python=/path/to/executable/python
```
&nbsp;&nbsp;&nbsp;&nbsp;Or on Windows:
```console
py --list-paths  # To see the installed Python versions
set npm_config_python=C:\path\to\python.exe  # CMD
$Env:npm_config_python="C:\path\to\python.exe"  # PowerShell
```

3. If the `PYTHON` environment variable is set to the path of a Python executable,
then that version will be used if it is a supported version.

4. If the `NODE_GYP_FORCE_PYTHON` environment variable is set to the path of a
Python executable, it will be used instead of any of the other configured or
built-in Python search paths. If it's not a compatible version, no further
searching will be done.

### Build for Third Party Node.js Runtimes

When building modules for third-party Node.js runtimes like Electron, which have
different build configurations from the official Node.js distribution, you
should use `--dist-url` or `--nodedir` flags to specify the headers of the
runtime to build for.

Also when `--dist-url` or `--nodedir` flags are passed, node-gyp will use the
`config.gypi`"""