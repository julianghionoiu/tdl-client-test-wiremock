
import urllib2
import subprocess
import os
import sys


def run(port):
    version = "2.12.0"
    url = "http://repo1.maven.org/maven2/com/github/tomakehurst/wiremock-standalone/" + version + "/wiremock-standalone-" + version + ".jar"
    file_name = url.split('/')[-1]

    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    if not os.path.isfile(file_name):
        download_and_show_progress(url, file_name)

    run_jar(file_name, port)


def run_jar(file_name, port):
    subprocess.call(["java", "-jar", file_name, "--port", str(port)])


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


if __name__ == "__main__":
    if len(sys.argv) > 1:
        run(int(sys.argv[1]))
    else:
        # server on 8222, recording system on 41375
        run(8222)
