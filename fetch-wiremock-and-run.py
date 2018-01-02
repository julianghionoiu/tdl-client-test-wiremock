import os
import signal
import socket
import subprocess
import sys
import time
import urllib2


def run(command, port):
    version = "2.12.0"
    url = "http://repo1.maven.org/maven2/com/github/tomakehurst/wiremock-standalone/" + version + "/wiremock-standalone-" + version + ".jar"
    file_name = url.split('/')[-1]

    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)
    pid_file = os.path.join(dir_path, "pid-" + str(port))

    if not os.path.isfile(file_name):
        download_and_show_progress(url, file_name)

    if command == "start":
        run_jar(file_name, port, pid_file)
        wait_until_port_is_open(port, 5)
    elif command == "stop":
        kill_wiremock_process(pid_file)


def run_jar(file_name, port, pid_file):
    proc = subprocess.Popen(["java", "-jar", file_name, "--port", str(port), "&", ])
    f = open(pid_file, "w")
    f.write(str(proc.pid))
    f.close()


def download_and_show_progress(url, file_name):
    u = urllib2.urlopen(url)
    f = open(file_name, 'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print "Downloading: %s Bytes: %s" % (file_name, file_size)

    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        f.write(buffer)
        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8) * (len(status) + 1)
        print status,

    f.close()


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


def kill_wiremock_process(pid_file):
    f = open(pid_file, "r")
    try:
        pid_str = f.read()
        print "Kill wiremock process with pid: " + pid_str
        os.kill(int(pid_str), signal.SIGTERM)
    except Exception:
        f.close()
        os.remove(pid_file)


if __name__ == "__main__":
    command = sys.argv[1]
    port = int(sys.argv[2])
    run(command, port)
