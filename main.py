import webbrowser
import time

def main():
    timeleft = input("во сколько открыть URL? ")
    url = input("Ссылка для открытия: ")
    try:
        time_struct = time.strptime(timeleft, "%H:%M")
        now = time.localtime()
        target_time = time.mktime((
            now.tm_year, now.tm_mon, now.tm_mday,
            time_struct.tm_hour, time_struct.tm_min, 0,
            now.tm_wday, now.tm_yday, now.tm_isdst
        ))
        if target_time < time.mktime(now):
            target_time += 86400
        wait_seconds = target_time - time.mktime(now)
        while wait_seconds > 0:
            mins, secs = divmod(int(wait_seconds), 60)
            hours, mins = divmod(mins, 60)
            print(f"Открытие через {hours:02}:{mins:02}:{secs:02}", end='\r')
            time.sleep(1)
            wait_seconds -= 1

        print(f"Ждем {int(wait_seconds)} секунд...")
        time.sleep(wait_seconds)
    except ValueError:
        print("Некорректный ввод времени. Открываем URL сразу.")
    print(f"Открываем {url}...")
    webbrowser.open(url)

main()
