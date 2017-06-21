Java Dependency Analyzer
========================

This project is a bunch of hacked-together scripts that can analyze complex Java projects for their internal dependencies (who extends/implements/uses what) and produce graphviz DOT-formatted output graphs.

First, ``dumper.py`` is run on a bunch of Java code producing a sqlite3 database file containing information on all types from this code and their relations. The parsing of the Java code is done using the ``javalang`` module. This tool's understanding of Java is incomplete. In the name of simplicity several shortcuts have been taken that may lead to incomplete or wrong output in corner cases.

Second, ``grapher.py`` is run, producing a graphviz DOT file from the sqlite3 dependency database produced by ``dumper.py``. This DOT file can then be converted to something visual by running graphviz, e.g.: ``fdp -x -Tpng out.dot > out2.png``

If you want to customize the output's styling or layout, just edit the DOT template in ``dumper.py``.

