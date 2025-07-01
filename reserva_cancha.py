from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import undetected_chromedriver as uc
from dotenv import load_dotenv
import os

load_dotenv()

def esperar_carga_horarios(driver, timeout=6):
    """
    Espera a que desaparezca el loader y a que:
    - Aparezcan más de 2 botones activos (horas disponibles)
    - O aparezca el mensaje de 'no hay horas disponibles'
    """
    try:
        print("⏳ Esperando que desaparezca el loader...")
        WebDriverWait(driver, timeout).until(
            EC.invisibility_of_element_located((By.XPATH, "//*[contains(text(), 'Cargando')]"))
        )
        print("✅ Loader desapareció.")

        print("⏳ Esperando a que carguen los horarios o mensaje de no disponibilidad...")

        WebDriverWait(driver, timeout).until(
            lambda d: (
                len(d.find_elements(By.XPATH, "//button[not(@disabled)]")) > 2 or
                len(d.find_elements(By.XPATH, "//*[contains(text(), 'no hay horas disponibles')]")) > 0
            )
        )
        print("✅ Horarios cargados o mensaje de no disponibilidad presente.")

    except TimeoutException:
        print("⚠️ Timeout esperando carga de horarios o mensaje de error.")


def esperar_campo_celular(driver, timeout=5):
    """
    Espera a que el <h1> dentro del botón 'Aceptar y finalizar' tenga color='grey.3',
    lo que indica que ya cargó la sección del celular.
    """
    try:
        print("⏳ Esperando a que el <h1> del botón 'Aceptar y finalizar' tenga color='grey.3'...")

        WebDriverWait(driver, timeout).until(
            lambda d: d.find_element(By.XPATH, "//button[contains(., 'Aceptar y finalizar')]/h1").get_attribute("color") == "grey.3"
        )

        print("✅ Campo celular disponible (color='grey.3').")
    except TimeoutException:
        print("⚠️ Timeout esperando que el campo celular esté disponible.")

def verificar_reserva(driver, timeout=5):
    """
    Espera hasta que aparezca el mensaje de éxito o se regrese a la pantalla de inicio.
    Retorna 'ok' si se agendó con éxito, 'inicio' si se volvió al principio, o 'timeout' si nada pasó.
    """
    print("⏳ Verificando si la reserva fue exitosa o se volvió al inicio...")

    fin = time.time() + timeout
    while time.time() < fin:
        try:
            exito = driver.find_element(By.XPATH, "//*[contains(text(), '¡SU HORA SE HA AGENDADO CON EXITO!')]")
            if exito.is_displayed():
                return "ok"
        except:
            pass

        try:
            campo_rut = driver.find_element(By.XPATH, "//input[@placeholder='Ejemplo: 11.111.111-1']")
            if campo_rut.is_displayed():
                return "inicio"
        except:
            pass

        time.sleep(0.5)  # Esperar medio segundo antes de volver a chequear

    return "timeout"

def simular_movimiento_humano(driver):
    import random

    print("🧍 Simulando movimientos humanos...")

    try:
        # Scroll hacia abajo y arriba de forma aleatoria
        for _ in range(random.randint(1, 3)):
            y = random.randint(100, 500)
            driver.execute_script(f"window.scrollBy(0, {y});")
            time.sleep(random.uniform(0.2, 0.6))
            driver.execute_script(f"window.scrollBy(0, {-y});")
            time.sleep(random.uniform(0.2, 0.6))

        # Mover el mouse aleatoriamente dentro de la página (no hace clics)
        body = driver.find_element(By.TAG_NAME, "body")
        webdriver.ActionChains(driver)\
            .move_to_element_with_offset(body, random.randint(10, 200), random.randint(10, 200))\
            .perform()

        print("✅ Simulación humana lista.")
    except Exception as e:
        print(f"⚠️ Error al simular movimiento humano: {e}")

# 🔧 Configura tus datos personales aquí
RUT = os.getenv("RUT")
CELULAR = os.getenv("CELULAR")
HORAS_DESEADAS = ["19:00", "20:00"]

# URL_AGENDAMIENTO = os.getenv("URL_AGENDAMIENTO_TEST")
URL_AGENDAMIENTO = os.getenv("URL_AGENDAMIENTO")

ES_LOCAL = not URL_AGENDAMIENTO.startswith("https://reservadehoras.lascondes.cl")

user_data_dir = os.getenv("CHROME_USER_DATA_DIR", "/tmp/chrome-profile")
os.makedirs(user_data_dir, exist_ok=True)

options = uc.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--headless=new")
# options.add_argument("--profile-directory=Profile 6")

driver = uc.Chrome(options=options, user_data_dir=user_data_dir)

try:
    encontrado = False
    intentos = 0

    while not encontrado and intentos < 400:
        print(f"\n🌀 Intento {intentos + 1}: buscando horas disponibles...")

        if intentos == 0 or ES_LOCAL:
            print(f"🔁 Cargando página desde URL: {URL_AGENDAMIENTO}")
            driver.get(URL_AGENDAMIENTO)
        else:
            print("🔄 Refrescando la página (entorno producción)...")
            driver.refresh()
        
        time.sleep(2)
        # simular_movimiento_humano(driver)

        # 2. Ingresar RUT
        try:
            rut_input = driver.find_element(By.XPATH, "//input[@placeholder='Ejemplo: 11.111.111-1']")
            rut_input.send_keys(RUT)
        except NoSuchElementException:
            print("⚠️ No se encontró el input del RUT. Probablemente la página no cargó bien. Reintentando...")
            intentos += 1
            continue

        # 3. Clic en "Continuar"
        continuar_button = driver.find_element(By.XPATH, "//button[contains(., 'Validar')]")
        continuar_button.click()

        # 4. Esperar a que cargue la sección de horarios
        esperar_carga_horarios(driver)
        time.sleep(random.uniform(0.3, 0.8))
        # simular_movimiento_humano(driver)

        try:
            # Verificar mensaje de no disponibilidad
            driver.find_element(By.XPATH, "//*[contains(text(), 'no hay horas disponibles')]")
            print("❌ No hay horas disponibles. Reintentando...")
            intentos += 1
            continue

        except NoSuchElementException:
            print("✅ Puede que haya horas disponibles")

            botones = driver.find_elements(By.XPATH, "//button[not(@disabled)]")

            if (len(botones) == 1):
                print("❌ Error, realmente no hay botones")
                intentos += 1
                continue

            if botones:
                print(f"🎯 Hay {len(botones)} botón(es) activo(s). Buscando alguna hora deseada: {HORAS_DESEADAS}")

                for hora_deseada in HORAS_DESEADAS:
                    for boton in botones:
                        texto = boton.text.strip()
                        print(texto);
                        if texto == hora_deseada:
                            print(f"✅ Encontrada hora deseada: {hora_deseada}. Haciendo clic...")
                            boton.click()

                            ass_button = driver.find_element(By.XPATH, "//button[contains(., 'Ok, programar')]")
                            ass_button.click()

                            esperar_campo_celular(driver)
                            time.sleep(random.uniform(0.3, 0.9))

                            # Ingresar número de celular
                            celular_input = driver.find_element(By.XPATH, "//input[@placeholder='Celular']")
                            celular_input.send_keys(CELULAR)

                            # Confirmar la reserva
                            finalizar_button = driver.find_element(By.XPATH, "//button[contains(., 'Aceptar y finalizar')]")
                            finalizar_button.click()

                            resultado = verificar_reserva(driver)
                            time.sleep(random.uniform(0.3, 0.9))
                            simular_movimiento_humano(driver)

                            if resultado == "ok":
                                intentos += 1
                                print("✅ Hora reservada con éxito.")
                                input("⏸️ Presiona Enter para cerrar el navegador...")
                                encontrado = True
                                break
                            elif resultado == "inicio":
                                print("⚠️ La hora ya no estaba disponible. Volviendo a intentar...")
                                intentos += 1
                                continue
                            else:
                                print("⚠️ Timeout esperando respuesta de reserva. Reintentando...")
                                intentos += 1
                                continue

                if not encontrado:
                    print("❌ Ninguna de las horas deseadas está disponible. Reintentando...")
                    intentos += 1
                    continue

            else:
                print("⚠️ No hay botones activos en este intento.")
                intentos += 1
                continue

        intentos += 1

except Exception as e:
    print(f"⚠️ Error durante el proceso: {e}")

finally:
    driver.quit()