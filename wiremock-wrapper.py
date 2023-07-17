import os
import signal
import socket
import subprocess
import sys
import time
import urllib.request, urllib.error, urllib.parse
import ssl

SCRIPT_FOLDER = os.path.dirname(os.path.realpath(__file__))
CACHE_FOLDER = os.path.join(SCRIPT_FOLDER, ".cache")


def run(command, port):
    if not os.path.exists(CACHE_FOLDER):
        os.mkdir(CACHE_FOLDER)

    version = "2.12.0"
    url = "https://repo1.maven.org/maven2/com/github/tomakehurst/wiremock-standalone/" + version + "/wiremock-standalone-" + version + ".jar"
    jar_file = os.path.join(CACHE_FOLDER, url.split('/')[-1])
    pid_file = os.path.join(CACHE_FOLDER, "pid-" + str(port))

    if not os.path.isfile(jar_file):
        download_and_show_progress(url, jar_file)

    if command == "start":
        print("Will run and detach from CLI and return to prompt...")
        run_jar(jar_file, port, pid_file, False)
        wait_until_port_is_open(port, 5, 5)

    if command == "status":
        wait_until_port_is_open(port, 1, 0)

    if command == "stop":
        kill_process(pid_file)
        wait_until_port_is_closed(port, 5, 5)

    if command == "console":
        print("Entered console mode (blocking, Ctrl-C to breakout)...")
        run_jar(jar_file, port, pid_file, True)


def run_jar(jar_path, port, pid_file, console_mode):
    JAVA_HOME=os.environ['JAVA_HOME']
    if console_mode:
        proc = subprocess.call([JAVA_HOME+"/bin/java", "-jar", jar_path, "--port", str(port) ], cwd=SCRIPT_FOLDER)
    else:
        proc = subprocess.Popen([JAVA_HOME+"/bin/java", "-jar", jar_path, "--port", str(port), "&", ], cwd=SCRIPT_FOLDER)

    f = open(pid_file, "w")
    f.write(str(proc.pid))
    f.close()



def download_and_show_progress(url, file_name):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    u = urllib.request.urlopen(url, context=ctx)
    f = open(file_name, 'wb')
    meta = u.info()
    file_size = int(meta.get_all("Content-Length")[0])
    print("Downloading: %s Bytes: %s" % (file_name, file_size))

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
        print(status, end=' ')

    f.close()


def wait_until_port_is_open(port, count, delay):
    n = 0
    while True:
        print("Is application listening on port " + str(port) + "? ")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        if result == 0:
            print("Yes")
            return

        n = n + 1
        if n < count:
            print("No. Retrying in " + str(delay) + " seconds")
            time.sleep(delay)
        else:
            print("No.")
            return


def wait_until_port_is_closed(port, count, delay):
    n = 0
    while True:
        print("Is application listening on port " + str(port) + "? ")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', int(port)))
        if result != 0:
            print("No")
            return

        n = n + 1
        if n < count:
            print("Yes. Retrying in " + str(delay) + " seconds")
            time.sleep(delay)
        else:
            print("Yes.")
            return


def kill_process(pid_file):
    if not os.path.exists(pid_file):
        print("Already stopped.")
        return

    f = open(pid_file, "r")
    try:
        pid_str = f.read()
        print("Kill process with pid: " + pid_str)
        os.kill(int(pid_str), signal.SIGTERM)
    except Exception:
        f.close()
        os.remove(pid_file)


if __name__ == "__main__":
    _command = sys.argv[1]
    _port = int(sys.argv[2])
    run(_command, _port)
