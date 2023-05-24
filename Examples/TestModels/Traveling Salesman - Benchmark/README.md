This AnyLogic model contains a benchmark test for the Traveling Salesman model under four cases:
1. Pypeline
2. Py4J
3. Commandline
4. Java (no Python)

## Context

The Traveling Salesman Problem is a classic optimization problem consisting of a set of cities, with the distances between each pair of cities is known. Given a starting location and a list of two or more of the other cities, the goal is to find the shortest route such that each city is visited exactly once and the origin city is returned to (in graph theory terms: a cycle).

In the case of the AnyLogic model, the default configuration has 16 cities - referred to as "facilities". The "Order" agent type holds the list of desination cities. There are two places in the model where Python is intended to be used:
1. In the Order agent; Python is expected to randomly pick a given number of random facilties to choose.
2. In optimizing the list of facilities to visit; this is accomplished using the OR-tools library.

Because the OR-tools library is available for both Python and Java, a natural comparison of pure Java versus Python-in-Java can be observed.

## Benchmark details

For all four cases, two metrics were timed:
1. How long it took to build the random array of facilities to visit in a cycle.
2. How long it took to optimize the random array of facilties.

As there are 16 facilities, all possible order size - from 3 to 15 - were tested, each 10 times. Order agents are scheduled to be created every 1 second and put through a dummy delay where the optimization occurs. 

At the end of the model, statistics related to the build and optimization times are printed to the console: the name of the test, the mean time taken, mean confidence, minimum time, and maximum time. These were then copy-pasted to the 'timings' Excel sheet. 

Four different "MainX" agents were created, where "X" is one of [Pypeline, Py4J, Commandline, Java]. Consequently, four Custom Experiments were created for each of the respective tests.

_Note: To run the Py4J test, you must first start the 'gateway.py' file_

## Directory details

* **Benchmark - Traveling Salesman.alp**: The source model
* **solver.py**: The Python file containing the optimization solver using the OR-tools library; used by all the tests except #4, pure Java.
* **gateway.py**: The Python file used for test #2, Py4J. It contains the Py4J JavaGateway Server (necessary to be run before and during the Py4J test itself). It has additional code to convert between the Java and Python objects.
* **solver_cmdline.py**: The Python file used for test #3, Commandline. It has an argument parser, allowing to call any of the functionalities in the solver.py file.
* **distanceData.json**: A "cache" of sorts, used to possibly save/retrieve data in use with test #3, Commandline.
* **timings.xlsx**: The output Excel file containing recorded timing information
* **py4j0.10.9.jar**: Required dependencies for test #2, Py4J
* **jna-.jar, ortools-.jar, protobuf-.jar**: Required dependencies for test #4, Java

## Results

The results of one set of runs can be found in the timings.xlsx file. They were made on a laptop with an Intel i7-7700HQ CPU @ 2.8GHz. 

The numbers indicate some expected results: the pure-Java approach executed between 1.5 to 12x faster than the Pypeline or Py4J code did. The areas where it had the most gains was in the random array building - this is the part that uses pure Java and no 3rd party libraries. Additionally, the commandline performed substantially worse than all the other three tests, upwards of 400x slower. 

Looking at the Python-in-Java libraries, Pypeline performed between 2 to 4.75x faster than Py4J. Similar to Java-versus-others, the most substantial gain was in buildling the random array. Py4J may be slower due to the need to manually convert between Java-based arrays and Python ones (in Python), and then back again, as the solver class required pure Python arrays. In contrast, Pypeline was able to utilize NumPy in its processing.

A summary of the mean times across all order sizes can be seen below, sorted by descending speed:

| Test        | Mean build times | Mean optimize times |
| ----------- | ---------------- | ------------------- |
| Java        | 0.000175         | 0.003526            |
| Pypeline    | 0.000468         | 0.004623            |
| Py4J        | 0.002224         | 0.008809            |
| Commandline | 0.932605         | 0.942739            |

This benchmark test is not perfectly designed and could use improvements. It also is not intended to be fully comprehensive and more tests are required to more accurately compare these cases.