import psutil
import time

def monitorar():
    while True:
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        disco = psutil.disk_usage('/').percent

        print(f"CPU: {cpu}% | RAM: {ram}% | Disco: {disco}%")

        if cpu > 80 or ram > 80 or disco > 90:
            print("Uso alto detectado!")

        time.sleep(5)

if __name__ == "__main__":
    monitorar()
