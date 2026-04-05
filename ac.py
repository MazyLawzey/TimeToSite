import webbrowser
import time
import os
import sys
from io import StringIO
from pynput import keyboard
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# Подавляем ошибки Chrome
devnull = open(os.devnull, 'w')
sys.stderr = devnull

# Set up the Chrome driver automatically with options to suppress errors
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--disable-logging')
chrome_options.add_argument('--disable-extensions')
chrome_options.add_argument('--disable-plugins')
chrome_options.add_argument('--disable-dev-shm-usage')  # Быстрая загрузка
chrome_options.add_argument('--disable-gpu')  # Отключаем GPU для стабильности
chrome_options.add_argument('--no-sandbox')  # Режим без sandbox для ускорения
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
chrome_options.add_experimental_option('useAutomationExtension', False)

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=chrome_options
)

# Восстанавливаем вывод ошибок
sys.stderr = sys.__stderr__

# Глобальный слушатель для клавиши '2'
def on_global_key_press(key):
    try:
        if hasattr(key, 'char') and key.char == '2':
            print("\n[!] Нажата клавиша 2! Пытаюсь нажать кнопку...")
            try:
                button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='orb-button']"))
                )
                original_window = driver.current_window_handle
                driver.execute_script("arguments[0].click();", button)
                time.sleep(2)
                
                if len(driver.window_handles) > 1:
                    for window in driver.window_handles:
                        if window != original_window:
                            driver.switch_to.window(window)
                            driver.close()
                    driver.switch_to.window(original_window)
                
                print("[+] Кнопка нажата успешно по команде!")
            except Exception as e:
                print(f"[-] Ошибка при нажатии кнопки: {e}")
    except AttributeError:
        pass

# Запускаем глобальный слушатель
global_listener = keyboard.Listener(on_press=on_global_key_press)
global_listener.start()

def setup():
    timeleft = input("Во сколько открыть URL? (в формате ЧЧ:ММ) ")
    url = "https://telemost.yandex.ru/j/XXXX"
    bootstrap(timeleft)
    return url

def bootstrap(timeleft):
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
        
        # Flag to track if Enter was pressed
        skip_wait = False
        
        def on_key_press(key):
            nonlocal skip_wait
            try:
                if key == keyboard.Key.enter:
                    skip_wait = True
                    return False  # Stop listener
            except AttributeError:
                pass
        
        # Start listening for key press in background
        listener = keyboard.Listener(on_press=on_key_press)
        listener.start()
        
        while wait_seconds > 0 and not skip_wait:
            mins, secs = divmod(int(wait_seconds), 60)
            hours, mins = divmod(mins, 60)
            print(f"Открытие через {hours:02}:{mins:02}:{secs:02}", end='\r')
            time.sleep(1)
            wait_seconds -= 1
        
        listener.stop()
        print("\nВремя ожидания истекло. Открываем URL...")
        if skip_wait:
            print("Клавиша Enter нажата. Открываем URL сразу.")
        after_connection()
    except ValueError:
        print("Некорректный ввод времени. Открываем URL сразу.")
        after_connection()


def after_connection():
    button = None
    try:
        # Ожидание загрузки страницы
        print("Ожидание загрузки страницы...")
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='orb-button']"))
        )
        
        # 5-секундный колдаун перед нажатием с возможностью пропустить клавишей 1
        print("Нажмите клавишу '1' чтобы нажать сразу, или ждите 5 секунд...")
        
        skip_wait = False
        
        def on_key_press(key):
            nonlocal skip_wait
            try:
                if hasattr(key, 'char') and key.char == '1':
                    skip_wait = True
                    return False  # Stop listener
            except AttributeError:
                pass
        
        # Запускаем слушатель клавиатуры
        listener = keyboard.Listener(on_press=on_key_press)
        listener.start()
        
        # Ожидаем 5 секунд или до нажатия кнопки 1
        countdown = 5
        while countdown > 0 and not skip_wait:
            print(f"Осталось {countdown} секунд...", end='\r')
            time.sleep(1)
            countdown -= 1
        
        listener.stop()
        
        if skip_wait:
            print("Клавиша 1 нажата! Нажимаю кнопку сразу.")
        else:
            print("5 секунд истекли. Нажимаю кнопку...")
        
        # Сохраняем текущую вкладку (окно)
        original_window = driver.current_window_handle
        
        # Нажимаем кнопку через JS скрипт
        driver.execute_script("arguments[0].click();", button)
        time.sleep(2)  # Даём время на открытие новой вкладки
        
        # Если открылась новая вкладка - закрываем её и возвращаемся
        if len(driver.window_handles) > 1:
            print(f"Открылась новая вкладка, закрываю её...")
            # Переходим на новую вкладку
            for window in driver.window_handles:
                if window != original_window:
                    driver.switch_to.window(window)
                    driver.close()
            # Возвращаемся на исходную вкладку
            driver.switch_to.window(original_window)
            print("Вернулся на исходную страницу.")
        
        print("Кнопка нажата успешно.")
    except Exception as e:
        print(f"Ошибка: {e}")
        print("Страница открыта, но возникла проблема с кликом или управлением вкладками.")


def main():
    url = setup()
    try:
        print(f"Открываем URL: {url}")
        driver.get(url)
        after_connection()
    except Exception as e:
        print(f"Ошибка при открытии URL или взаимодействии с элементами: {e}")

main()

try:
    while True:
        pass
except KeyboardInterrupt:
    print("\nScript stopped by user.")
    driver.quit()
