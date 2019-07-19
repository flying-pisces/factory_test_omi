__author__ = 'kieranlevin'
import subprocess
import tempfile
import os
import time
import datetime
import logging
import StringIO

class adb_device():
    def __init__(self, serial=None, remote=None, custom_adb_path="adb", timeout=90, verbose=False):
        self.serial = serial
        # ip of remote device if not none
        self.remote = remote
        self.custom_adb_path = custom_adb_path
        self.ps = None
        self.verbose = verbose
        self.timeout = timeout
        self.stderr = ""
        self.stdout = ""
        self.logger = logging.getLogger("ADB")
        if verbose:
            self.logger.setLevel(logging.DEBUG)

    def initialize(self):
        self._do_adb(['start-server'], disconnect_when_complete=True)

    def _do_adb(self, commands, disconnect_when_complete=False):
        if disconnect_when_complete == False:
            assert self.ps == None, "Device already connected!"
            self.stderr = ""
            self.stdout = ""
        returncode = [None, [], []]
        cmds = []
        stderr = ""
        stdout = ""
        if self.custom_adb_path:
            cmds.append(self.custom_adb_path)
        else:
            cmds.append("adb")
        if self.remote:
            cmds.append("connect")
            cmds.append(self.remote)
        elif self.serial:
            cmds.append("-s")
            cmds.append(str(self.serial))
        for i in commands:
            cmds.append(i)

        ps = subprocess.Popen(cmds, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if disconnect_when_complete:
            stdout, stderr = ps.communicate()
            returncode = [ps.returncode, StringIO.StringIO(stdout).readlines(), StringIO.StringIO(stderr).readlines()]
            ps = None
        else:
            self.ps = ps
        return returncode

    def connect(self):
        '''
        Open an interactive shell session where you can send commands over to adb.
        :return:
        '''
        return self._do_adb(["shell"])

    def is_connected(self):
        return self.ps != None

    def disconnect(self):
        # assert self.ps != None, "Device not connected"
        if self.ps !=None:
            self.ps.stdin.write("exit\r\n")
            newstdout, newstderr = self.ps.communicate()
            self.stdout += newstdout
            self.stderr += newstderr
            returncode = [self.ps.returncode, StringIO.StringIO(self.stdout).readlines(), StringIO.StringIO(self.stderr).readlines()]
            self.ps = None
            return returncode
        else:
            pass

    def send_shell_command(self, command):
        assert self.ps != None, "shell not connected"
        try:
            self.ps.stdin.write(command + "\n")
        except IOError:
            self.logger.info("lost connection to adb shell. Retrying")
            self.ps = None
            self.connect()
            self.ps.stdin.write(command + "\n")
        return

    def communicate(self):
        if self.ps:
            #self.stderr += self.ps.stderr.readlines()
            self.stdout += self.ps.stdout.readlines()

    def cmd_and_quit(self, command):
        return self._do_adb(["shell", command], True)

    def send_data_as_file(self, data, remote_filename):
        tempfileloc = tempfile.mkstemp()[1]  # make a temp file to rx in the most secure way possible
        self.logger.info("SendingData:{}".format( tempfileloc ) )
        f = open(tempfileloc, "wb")
        f.write(data)
        f.close()
        f = None
        returnstruct, output, err = self._do_adb(["push", tempfileloc, remote_filename], True)
        #os.remove(tempfileloc)
        return returnstruct

    def send_file(self, local_file, device_file):
        self.logger.info("send_file:{} {}".format( device_file,  local_file) )
        returnstruct= self._do_adb(["push", local_file, device_file], True)
        return returnstruct

    def get_file_data(self, device_file):
        device_filedir, device_filename = os.path.split(device_file)
        tempdir = tempfile.gettempdir()
        tempfile_loc = os.path.join(tempdir, device_filename)
        returncode, stdout, stderr = self._do_adb( ["pull", device_file, tempfile_loc], True)

        if returncode == 0:
            # read the file copied over by adb into a buffer:
            f = open(tempfile_loc, "rb")
            data = f.read()
            f.close()

            # Clean up afterwards
            os.remove(tempfile_loc)

            returnstruct = [data, returncode]
        else:
            self.logger.warn("Failed to get %s - %s" % (device_filename, stdout))
            returnstruct = [None, returncode]

        return returnstruct

    def get_file(self, device_file, local_file):
        self.logger.info("get_file:{} {}".format( device_file,  local_file) )
        returncode, _a = self._do_adb( ["pull", device_file, local_file], True)
        return returncode

    def remount(self):
        return self._do_adb(["remount"], True)

    def root(self):
        return self._do_adb(["root"], True)

    def reboot(self, bootloader=False, edl=False):
        params = []
        params.append("reboot")
        if bootloader:
            params.append("bootloader")
        if edl:
            params.append("edl")
        return self._do_adb(params, True)

    def kill_server(self):
        return self._do_adb(["kill-server"], True)

    def list_devices(self):
        '''
        :return: list [] object of device serial numbers that are attached via usb
        '''
        try:
            code, output, err = self._do_adb(["devices"], True)
        except:
            return []
        devserial = []
        for i in range(1,len(output)-1):
            devserial.append(output[i].split("\t")[0] )
        return devserial

    def poll(self):
        if self.ps:
            return self.ps.poll()
        return None
    def terminate(self):
        if self.ps:
            self.ps.terminate()
        self.ps = None

    def get_build_fingerprint(self):
        try:
            code, output, err = self.cmd_and_quit("getprop ro.build.fingerprint")
        except:
            return "Build not detected"
        return output

    def screenshot(self):
        tempscreengrab = "/sdcard/Pictures/screen.png"
        self._do_adb(["screencap", tempscreengrab], True)
        screenshot= self.get_file_data(tempscreengrab)
        self._do_adb(["rm", tempscreengrab], True)
        return screenshot

    def reverse_port_forward(self, device, host):
        return self._do_adb(["reverse", "tcp:{}".format(int(device)), "tcp:{}".format(int(host))], True)

    def forward_port(self, device, host):
        return self._do_adb(["forward", "tcp:{}".format(int(device)), "tcp:{}".format(int(host))], True)

    def reverse_port_forward_remove(self):
        return self._do_adb(["reverse", "--remove-all"], True)

    def install_apk(self, local_path):
        return self._do_adb(["install", "-r", local_path], True)

    def remove_apk(self, apk_name):
        return self._do_adb(["uninstall", apk_name], True)

    def exists(self, filename, directory="/sdcard/Pictures/"):
        return self._do_adb(["shell","ls", os.path.join(directory, filename)], True)
