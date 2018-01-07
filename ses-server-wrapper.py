import os
import signal
import socket
import subprocess
import sys
import time

SCRIPT_FOLDER = os.path.dirname(os.path.realpath(__file__))
CACHE_FOLDER = os.path.join(SCRIPT_FOLDER, ".cache")

def run(command):
    if not os.path.exists(CACHE_FOLDER):
        os.mkdir(CACHE_FOLDER)

    port = 9555
    python_file = 'ses-server.py'
    pid_file = os.path.join(CACHE_FOLDER, "pid-" + str(port))

    if command == "start":
        pid = run_python(python_file, port, pid_file)
        wait_until_port_is_open(port, 5)
        print "Process running as pid: " + str(pid)
    elif command == "stop":
        kill_process(pid_file)


def run_python(python_path, port, pid_file):
    proc = subprocess.Popen(["python", python_path, str(port), "&",], cwd=SCRIPT_FOLDER)
    f = open(pid_file, "w")
    f.write(str(proc.pid))
    f.close()
    return proc.pid


def wait_until_port_is_open(port, delay):
    n = 0
    while n < 5:
        print "Is application listening on port " + str(port) + "? "
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        if result == 0:
            print "Yes"
            return
        print "No. Retrying in " + str(delay) + " seconds"
        n = n + 1
        time.sleep(delay)


def kill_process(pid_file):
    f = open(pid_file, "r")
    try:
        pid_str = f.read()
        print "Kill process with pid: " + pid_str
        os.kill(int(pid_str), signal.SIGTERM)
    except Exception:
        f.close()
        os.remove(pid_file)


if __name__ == "__main__":
    run(sys.argv[1])
