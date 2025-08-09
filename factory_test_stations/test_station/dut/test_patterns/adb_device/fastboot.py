from adb import *



class fastboot_device(adb_device):
    def __init__(self, serial=None, remote=None, custom_fastboot_path="fastboot", timeout=90, verbose=False):
        adb_device.__init__(self, serial=serial, remote=remote, custom_adb_path=custom_fastboot_path, timeout=timeout, verbose=verbose)



    def reboot(self, bootloader=False, emergency=False):
        params = []
        params.append("reboot")
        if bootloader:
            params.append("bootloader")
        elif emergency:
            params.append("emergency")
        return self._do_adb(params, True)

    def flash_data(self, partition, data):
        tempfileloc = tempfile.mkstemp()[1]  # make a temp file to rx in the most secure way possible
        self.logger.info("SendingData:{}".format( tempfileloc ) )
        f = open(tempfileloc, "wb")
        f.write(data)
        f.close()
        f = None
        ret = self.flash_file(partition, tempfileloc)
        # os.remove(tempfileloc)
        return ret

    def flash_file(self, partition, fname):
        params = []
        params.append("flash")
        params.append(partition)
        params.append(fname)
        return self._do_adb(params, True)

    def erase(self, partition):
        params = []
        params.append("erase")
        params.append(partition)
        return self._do_adb(params, True)

    def list_devices(self):
        '''

        :return: list [] object of device serial numbers that are attached via usb
        '''
        try:
            code, output, err = self._do_adb(["devices"], True)
        except:
            return []
        devserial = []
        for i in range(len(output)):
            devserial.append(output[i].split("\t")[0] )
        return devserial

    def connect(self):
        assert "not used"

    def kill_server(self):
        assert "not used"

    def poll(self):
        assert "not used"

    def terminate(self):
        assert "not used"
