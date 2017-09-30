import time, os, sys
import subprocess


def find_process(ps_name):
    p1=subprocess.Popen(['ps','-ef'],stdout=subprocess.PIPE)
    p2=subprocess.Popen(['grep','python3'],stdin=p1.stdout,stdout=subprocess.PIPE)
    p3=subprocess.Popen(['grep','-i',ps_name],stdin=p2.stdout,stdout=subprocess.PIPE)
    p4=subprocess.Popen(['wc','-l'],stdin=p3.stdout,stdout=subprocess.PIPE)
    output = p4.communicate()[0].decode('utf-8').strip()

    return int(output)

def spawn_tracker():
    for p in form_pair():
        if not find_process(p):
            pid=os.fork()
            if pid==0:
                ppid = os.getpid()
                os.system("nohup python3 track_pair.py %s %s >/dev/null 2>&1 &" % (p, ppid))
                os._exit(0)
        else:
            print("%s is running..." % p)


def form_pair():
    base = ['USD', 'BTC', 'ETH']

    new_pair = ['BTCUSD','ETHUSD']

    for b in base:
        p = "%s%s" % (symbol, b)

        new_pair.append(p)

    return new_pair


def main():
    global symbol

    symbol = str(sys.argv[1]).upper()
    pid = int(sys.argv[2]) if len(sys.argv) == 3 else 0    

    print("Start tracking...")
    while(1):
        spawn_tracker()
        if pid:
            try:
                os.kill(pid, 0)
            except:
                sys.exit()
                
        time.sleep(20)
        os.system("clear")



if __name__== "__main__":
    if len(sys.argv) > 1:
        main()

    print("Error: param 1 coin input needed! E.g. IOT / BCH / BCC")
