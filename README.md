# Pypeline
A custom library for AnyLogic that allows you to call Python within a running model. It connects to a local installation of Python, allowing you to make use of any Python library.

It can be used for cases such as:
* Utilizing code that was originally written in Python without having to port to Java
* Writing complex algorithms in Python that you can call in Java, optionally passing objects/data between the languages
* Being able to use any Python-exclusive library
* Using simulation as a testbed for testing trained artificial intelligence policies

## Getting Started
These instructions will get Pypeline integrated with AnyLogic. They are described more thoroughly in the provided wiki (which is what the user guide migrated to).

### Prerequisites
You need to have AnyLogic with any valid license (PLE, University, or Professional) and **any version of Python 3—except from the Windows Store—installed on your machine.

**_Note: Python from the Windows Store is not supported due to the inability to externally call its executable. Any other source is supported (e.g., official installer, anaconda, system package managers)._

### Installation

1. Download the `Pypeline.jar` file (from the [releases](https://github.com/t-wolfeadam/AnyLogic-Pypeline/releases)) and place it somewhere it won't be moved (or accidentally deleted).
2. Add it to your AnyLogic palette. A step-by-step explanation of how to do this is available in the AnyLogic help article ["Managing Libraries"](https://help.anylogic.com/topic/com.anylogic.help/html/libraries/managing-libraries.html?cp=3_5_4). 
3. You should see a new palette item for Pypeline with the custom Python Communicator agent.

## Quick Start Guide
This section goes over testing the connection works and a simple tutorial.

*For a full explanation of how to use it, including a deeper description of the available functions, please refer to the wiki.*

### Testing Connection
To ensure a proper connection is made, first run a simple test:
1. Create a new AnyLogic model
2. Drag in a Python Communicator from the Pypeline palette tab; keep its default name ("pyCommunicator")
3. Run the model
  1. In your running model, click the Communicator object
  2. The inspection window should show the version of Python and the path to the Python executable that's being used
> If you do not see this, or you receive an error, please refer to the troubleshooting section of the wiki.

### Basic Tutorial
Building on the model made in the previous section, try the following:
1. In the AnyLogic editor, drag in a new button from the **Controls** palette.  Set its label to "set x", and in its **Action** field, type the following code:
```java
pyCommunicator.run("x = 3.14");
```
> The `run` function is used to send statements to Python that expect no response (e.g., variable assignments or import statements).

> The passed string is what is sent to Python; it defines a new Python variable, `x`, which is set to the floating point number `3.14`

2. Drag in another button, set its label to "get x", and in its **Action** field, type the following code:
```java
double xValue = pyCommunicator.runResults(double.class, "x");
traceln(xValue);
```
> The `runResults` function is used when you want to retrieve a value from Python.

> The double class is passed to convert the desired variable ("x") to the expected Java type.

3. Run the model! You should first click the "set x" button, then press the "get x" button; afterward, the number specified should be printed to the console.

  > If you press the "get x" button first, an error will be thrown because you tried to get the value of a variable before you defined it!

There are demos and example models provided with the library. Please review them to get some inspiration of possible use cases and to better understand the workflow.

## Important disclaimers
* Pypeline is not part of the main AnyLogic product, and The AnyLogic Company is not obligated to provide support for users or to provide future support/updates
  * It's encouraged to make use of the community features available here or elsewhere online
* Using Pypeline is not a substitute for Java, which remains the only native scripting language of AnyLogic
  * You can (and should) build models in the AnyLogic GUI exactly as before, making full use of AnyLogic's extensive native capabilities
* Pypeline will also add some computational overhead to your model and therefore may not be the best option if computational efficiency is a priority in your models

## Contributing
Please feel free to contribute to Pypeline! For this purpose, pull requests are used; if you're not familiar with how to do this, consult GitHub Help for more information.

Any questions, issues, bug reports, or feature requests should be made on the "Issues" tab.
