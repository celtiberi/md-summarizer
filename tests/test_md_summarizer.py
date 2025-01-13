import pytest
from src.md_summarizer import MarkdownSummarizer, Section
from src.agent.document_agent import DocumentAgent
import os
from dotenv import load_dotenv
import logging
import time
from src.config.settings import get_settings, EnvironmentType
from .utils.output_formatter import format_section, format_comparison
from .utils.assertions import assert_tokens_reduced

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

@pytest.mark.asyncio
async def test_concurrent_processing(summarizer):
    """Test concurrent processing of multiple sections."""
    content = """# Section 1
    Content 1
    
    # Section 2
    Content 2
    
    # Section 3
    Content 3"""
    
    # Show input
    format_section("INPUT", content)
    
    start_time = time.time()
    result = await summarizer.summarize(content)
    duration = time.time() - start_time
    
    # Show output with timing
    format_section("OUTPUT", result)
    
    format_comparison(content, result, summarizer.agent)
    
    # Verify all sections processed
    assert "Content 1" in result
    assert "Content 2" in result
    assert "Content 3" in result
    assert duration < 4  # Should complete in less than 4 seconds

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
`config.gypi` shipped in the headers distribution to generate build
configurations, which is different from the default mode that would use the
`process.config` object of the running Node.js instance.

Some old versions of Electron shipped malformed `config.gypi` in their headers
distributions, and you might need to pass `--force-process-config` to node-gyp
to work around configuration errors.

## How to Use

To compile your native addon first go to its root directory:

``` bash
cd my_node_addon
```

The next step is to generate the appropriate project build files for the current
platform. Use `configure` for that:

``` bash
node-gyp configure
```

Auto-detection fails for Visual C++ Build Tools 2015, so `--msvs_version=2015`
needs to be added (not needed when run by npm as configured above):
``` bash
node-gyp configure --msvs_version=2015
```

__Note__: The `configure` step looks for a `binding.gyp` file in the current
directory to process. See below for instructions on creating a `binding.gyp` file.

Now you will have either a `Makefile` (on Unix platforms) or a `vcxproj` file
(on Windows) in the `build/` directory. Next, invoke the `build` command:

``` bash
node-gyp build
```

Now you have your compiled `.node` bindings file! The compiled bindings end up
in `build/Debug/` or `build/Release/`, depending on the build mode. At this point,
you can require the `.node` file with Node.js and run your tests!

__Note:__ To create a _Debug_ build of the bindings file, pass the `--debug` (or
`-d`) switch when running either the `configure`, `build` or `rebuild` commands.

## The `binding.gyp` file

A `binding.gyp` file describes the configuration to build your module, in a
JSON-like format. This file gets placed in the root of your package, alongside
`package.json`.

A barebones `gyp` file appropriate for building a Node.js addon could look like:

```python
{
  "targets": [
    {
      "target_name": "binding",
      "sources": [ "src/binding.cc" ]
    }
  ]
}
```

## Further reading

The **[docs](./docs/)** directory contains additional documentation on specific node-gyp topics that may be useful if you are experiencing problems installing or building addons using node-gyp.

Some additional resources for Node.js native addons and writing `gyp` configuration files:

 * ["Going Native" a nodeschool.io tutorial](http://nodeschool.io/#goingnative)
 * ["Hello World" node addon example](https://github.com/nodejs/node/tree/main/test/addons/hello-world)
 * [gyp user documentation](https://gyp.gsrc.io/docs/UserDocumentation.md)
 * [gyp input format reference](https://gyp.gsrc.io/docs/InputFormatReference.md)
 * [*"binding.gyp" files out in the wild* wiki page](./docs/binding.gyp-files-in-the-wild.md)

## Commands

`node-gyp` responds to the following commands:

| **Command**   | **Description**
|:--------------|:---------------------------------------------------------------
| `help`        | Shows the help dialog
| `build`       | Invokes `make`/`msbuild.exe` and builds the native addon
| `clean`       | Removes the `build` directory if it exists
| `configure`   | Generates project build files for the current platform
| `rebuild`     | Runs `clean`, `configure` and `build` all in a row
| `install`     | Installs Node.js header files for the given version
| `list`        | Lists the currently installed Node.js header versions
| `remove`      | Removes the Node.js header files for the given version


## Command Options

`node-gyp` accepts the following command options:

| **Command**                       | **Description**
|:----------------------------------|:------------------------------------------
| `-j n`, `--jobs n`                | Run `make` in parallel. The value `max` will use all available CPU cores
| `--target=v6.2.1`                 | Node.js version to build for (default is `process.version`)
| `--silly`, `--loglevel=silly`     | Log all progress to console
| `--verbose`, `--loglevel=verbose` | Log most progress to console
| `--silent`, `--loglevel=silent`   | Don't log anything to console
| `debug`, `--debug`                | Make Debug build (default is `Release`)
| `--release`, `--no-debug`         | Make Release build
| `-C $dir`, `--directory=$dir`     | Run command in different directory
| `--make=$make`                    | Override `make` command (e.g. `gmake`)
| `--thin=yes`                      | Enable thin static libraries
| `--arch=$arch`                    | Set target architecture (e.g. ia32)
| `--tarball=$path`                 | Get headers from a local tarball
| `--devdir=$path`                  | SDK download directory (default is OS cache directory)
| `--ensure`                        | Don't reinstall headers if already present
| `--dist-url=$url`                 | Download header tarball from custom URL
| `--proxy=$url`                    | Set HTTP(S) proxy for downloading header tarball
| `--noproxy=$urls`                 | Set urls to ignore proxies when downloading header tarball
| `--cafile=$cafile`                | Override default CA chain (to download tarball)
| `--nodedir=$path`                 | Set the path to the node source code
| `--python=$path`                  | Set path to the Python binary
| `--msvs_version=$version`         | Set Visual Studio version (Windows only)
| `--solution=$solution`            | Set Visual Studio Solution version (Windows only)
| `--force-process-config`          | Force using runtime's `process.config` object to generate `config.gypi` file

## Configuration

### Environment variables

Use the form `npm_config_OPTION_NAME` for any of the command options listed
above (dashes in option names should be replaced by underscores).

For example, to set `devdir` equal to `/tmp/.gyp`, you would:

Run this on Unix:

```bash
export npm_config_devdir=/tmp/.gyp
```

Or this on Windows:

```console
set npm_config_devdir=c:\temp\.gyp
```

### `npm` configuration for npm versions before v9

Use the form `OPTION_NAME` for any of the command options listed above.

For example, to set `devdir` equal to `/tmp/.gyp`, you would run:

```bash
npm config set [--global] devdir /tmp/.gyp
```

**Note:** Configuration set via `npm` will only be used when `node-gyp`
is run via `npm`, not when `node-gyp` is run directly.

## License

`node-gyp` is available under the MIT license. See the [LICENSE
file](LICENSE) for details.
"""