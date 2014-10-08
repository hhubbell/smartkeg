# ----------------------------------------------------------------------------
# Filename:     process.py
# Author:       Harrison Hubbell
# Date:         10/05/2014
# Description:  Parent and Child processes which can be inherited by objects
#               that require multiprocessing functionality as either a parent
#               or child process.
# ----------------------------------------------------------------------------

from multiprocessing import Process, Pipe

class ParentProcess(object):
    def __init__(self):
        self.procs = {}
        self.pipes = {}

    def proc_add(self, proc_name, target=None, pipe=None):
        """
        @Author:        Harrison Hubbell
        @Created:       10/05/2014
        @Description:   Adds a process and manages creating the pipes 
                        between both nodes.
        """
        args = None

        if pipe:
            self.pipes[proc_name] = {'TO': None, 'FROM': None}
            self.pipes[proc_name]['TO'], self.pipes[proc_name]['FROM'] = Pipe()
            args = (self.pipes[proc_name]['FROM'],)

        self.procs[proc_name] = Process(name=proc_name, target=target, args=args)
   
    def proc_poll_recv(self, proc_name):
        """
        @Author:        Harrison Hubbell
        @created:       10/05/2014
        @Description:   Receives data from a process via its pipe without
                        blocking processing, by polling first.
        """
        node = self.pipes[proc_name]['TO']
        if node.poll():
            return node.recv()

    def proc_recv(self, proc_name):
        """
        @Author:        Harrison Hubbell
        @created:       10/05/2014
        @Description:   Receives data from a process via its pipe with
                        blocking.
        """
        return self.pipes[proc_name]['TO'].recv()

    def proc_send(self, proc_name, payload):
        """
        @Author:        Harrison Hubbell
        @created:       10/05/2014
        @Description:   Sends data to an arbitrary process via its pipe.
        """
        self.pipes[proc_name]['TO'].send(payload)

    def proc_start_all(self):
        """
        @Author:        Harrison Hubbell
        @Created:       10/05/2014
        @Description:   Starts all processes in the procs dict.
        """
        for proc in self.procs:
            self.procs[proc].start()


class ChildProcess(object):
    def __init__(self, pipe):
        self.pipe = pipe

    def proc_poll_recv(self):
        """
        @Author:        Harrison Hubbell
        @created:       10/05/2014
        @Description:   Receives data from the parent via its pipe without
                        blocking processing, by polling first.
        """
        if self.pipe.poll():
            return self.pipe.recv()

    def proc_recv(self):
        """
        @Author:        Harrison Hubbell
        @created:       10/05/2014
        @Description:   Receives data from the parent via its pipe with
                        blocking.
        """
        return self.pipe.recv()

    def proc_send(self, payload):
        """
        @Author:        Harrison Hubbell
        @created:       10/05/2014
        @Description:   Sends data to parent process via its pipe.
        """
        self.pipe.send(payload)
