"""
Test that 'stty -a' displays the same output before and after running the lldb command.
"""

import os
import unittest2
import lldb
import pexpect
from lldbtest import *

class CommandLineCompletionTestCase(TestBase):

    mydir = os.path.join("functionalities", "completion")

    @classmethod
    def classCleanup(cls):
        """Cleanup the test byproducts."""
        system(["/bin/sh", "-c", "rm -f child_send1.txt"])
        system(["/bin/sh", "-c", "rm -f child_read1.txt"])
        system(["/bin/sh", "-c", "rm -f child_send2.txt"])
        system(["/bin/sh", "-c", "rm -f child_read2.txt"])

    def test_stty_dash_a_before_and_afetr_invoking_lldb_command(self):
        """Test that 'stty -a' displays the same output before and after running the lldb command."""

        # The expect prompt.
        expect_prompt = "expect[0-9.]+> "
        # The default lldb prompt.
        lldb_prompt = "(lldb) "

        # So that the child gets torn down after the test.
        self.child = pexpect.spawn('expect')
        child = self.child

        child.expect(expect_prompt)
        child.setecho(True)
        if self.TraceOn():
            child.logfile = sys.stdout

        child.sendline('set env(TERM) xterm')
        child.expect(expect_prompt)
        child.sendline('puts $env(TERM)')
        child.expect(expect_prompt)

        # Turn on loggings for input/output to/from the child.
        with open('child_send1.txt', 'w') as f_send1:
            with open('child_read1.txt', 'w') as f_read1:
                child.logfile_send = f_send1
                child.logfile_read = f_read1

                child.sendline('stty -a')
                child.expect(expect_prompt)

        # Now that the stage1 logging is done, restore logfile to None to
        # stop further logging.
        child.logfile_send = None
        child.logfile_read = None

        # Invoke the lldb command.
        child.sendline('%s %s' % (self.lldbHere, self.lldbOption))
        child.expect_exact(lldb_prompt)

        # Immediately quit.
        child.sendline('quit')
        child.expect(expect_prompt)

        with open('child_send2.txt', 'w') as f_send2:
            with open('child_read2.txt', 'w') as f_read2:
                child.logfile_send = f_send2
                child.logfile_read = f_read2

                child.sendline('stty -a')
                child.expect(expect_prompt)

                child.sendline('exit')

        # Now that the stage2 logging is done, restore logfile to None to
        # stop further logging.
        child.logfile_send = None
        child.logfile_read = None

        with open('child_send1.txt', 'r') as fs:
            if self.TraceOn():
                print "\n\nContents of child_send1.txt:"
                print fs.read()
        with open('child_read1.txt', 'r') as fr:
            from_child1 = fr.read()
            if self.TraceOn():
                print "\n\nContents of child_read1.txt:"
                print from_child1

        with open('child_send2.txt', 'r') as fs:
            if self.TraceOn():
                print "\n\nContents of child_send2.txt:"
                print fs.read()
        with open('child_read2.txt', 'r') as fr:
            from_child2 = fr.read()
            if self.TraceOn():
                print "\n\nContents of child_read2.txt:"
                print from_child2

        stty_output1_lines = from_child1.splitlines()
        stty_output2_lines = from_child2.splitlines()
        zipped = zip(stty_output1_lines, stty_output2_lines)
        for tuple in zipped:
            if self.TraceOn():
                print "tuple->%s" % str(tuple)
            # Every line should compare equal until the first blank line.
            if len(tuple[0]) == 0:
                break
            self.assertTrue(tuple[0] == tuple[1])


if __name__ == '__main__':
    import atexit
    lldb.SBDebugger.Initialize()
    atexit.register(lambda: lldb.SBDebugger.Terminate())
    unittest2.main()
