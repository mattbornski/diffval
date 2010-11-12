diffval - a quick tutorial
==========================

There are several assumptions that underpin the default operation of diffval.  Let's start with one that will be useful later on: diffval assumes all of the relevant files for a given test have the same base name as the test itself.  Therefore, if your test is called "foo.py", your other test files (if any) should be called "foo.*".

The primary way for diffval to tell if your test succeeds or fails is to compare the output of the test on stdout and stderr and determine if they match.  Let's observe:

::

  user@machine$ echo "print 'foo'" >> foo.py
  user@machine$ echo "foo" >> foo.out
  user@machine$ diffval foo.py
  user@machine$ echo $?
  0

The test succeeds, because running foo.py produces exactly the output we expect to see in foo.out.  What if the output is difficult to predict?  Imagine we are testing something that outputs the current time, for instance.  One option we have is to ignore the output itself - it seems counterintuitive, but there are a lot of things that we can test without looking at the actual text generated.

::

  user@machine$ echo "import time" >> tricky.py
  user@machine$ echo "print time.time()" >> tricky.py
  user@machine$ diffval tricky.py
  user@machine$ echo $?
  0

The test succeeds, because diffval sees that there is no file tricky.out, and so it assumes you do not care about the stdout.  This is one way diffval's assumptions can make your life easier.  Note that the assumption is backwards for stderr, however:

::

  user@machine$ echo "import sys" >> error.py
  user@machine$ echo "print >> sys.stderr, 'foo'" >> error.py
  user@machine$ diffval error.py
  user@machine$ echo $?
  1

The test failed, because unexpected messages on stderr are assumed to be failures.  To tell diffval that this is okay, you would want to have a file called "error.err" which contained just the word "foo".

Up to now we have been telling diffval explicity which files to test.  In order to accommodate the large test suites that are needed for real-life products, diffval is designed to operate on "test trees".  A test tree is just a folder named "tests" which lives side-by-side with your code, but contains only test files.  diffval can then run all the tests in the entire folder without having to be told each individual filename.
