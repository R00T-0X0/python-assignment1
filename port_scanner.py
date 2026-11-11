import socket
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


def get_target_ip():
    return input("Enter target IP: ").strip()


def validate_ip(target_ip):
    try:
        socket.inet_aton(target_ip)
        return True
    except OSError:
        return False


def scan_port(target_ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)

    try:
        return sock.connect_ex((target_ip, port)) == 0
    except OSError:
        return False
    finally:
        sock.close()


def print_open_port(port):
    print(f"[OPEN] {port}")


def scan_ports(target_ip):
    open_ports = []
    closed_ports = 0

    with ThreadPoolExecutor(max_workers=50) as executor:
        tasks = {
            executor.submit(scan_port, target_ip, port): port
            for port in range(1, 1025)
        }

        for task in as_completed(tasks):
            port = tasks[task]

            try:
                if task.result():
                    open_ports.append(port)
                    print_open_port(port)
                else:
                    closed_ports += 1
            except OSError:
                closed_ports += 1

    open_ports.sort()
    return open_ports, closed_ports


def print_summary(target_ip, open_ports, closed_ports, elapsed_time):
    print("\nScan completed")
    print("-" * 30)
    print(f"Target       : {target_ip}")
    print(f"Open ports   : {len(open_ports)}")
    print(f"Closed ports : {closed_ports}")
    print(f"Open port list: {open_ports}")
    print(f"Elapsed time : {elapsed_time:.2f} seconds")


def main():
    target_ip = get_target_ip()

    if not validate_ip(target_ip):
        print("[!] Please enter a valid IPv4 address.")
        return

    print(f"\nScanning {target_ip} (ports 1-1024)")
    start_time = time.perf_counter()

    try:
        open_ports, closed_ports = scan_ports(target_ip)
    except KeyboardInterrupt:
        print("\n[!] Scan stopped.")
        return

    elapsed_time = time.perf_counter() - start_time
    print_summary(target_ip, open_ports, closed_ports, elapsed_time)


if __name__ == "__main__":
    main()
