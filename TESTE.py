import sys
import os
import threading
import time
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QWidget, QTextEdit, QVBoxLayout, QPushButton, QLabel
)
from PyQt5.QtGui import QPixmap, QPalette, QBrush, QFont
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QFrame
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

# Configurações
pasta_destino_olos = r"C:\Users\nyrodrigues\Desktop\Nikolas Yan\Python\python\Olos"
pasta_destino_horus = r"C:\Users\nyrodrigues\Desktop\Nikolas Yan\Python\python\teste"
pasta_destino_salesforce = r"C:\Users\nyrodrigues\Desktop\Nikolas Yan\Python\python\Salesforce"
caminho_sessao_whatsapp = r"C:\Users\nyrodrigues\AppData\Local\Google\Chrome\User Data\Default"
intervalo_minutos = 60

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("REPORT HORA X HORA")
        self.setGeometry(100, 100, 700, 480)
        #self.setWindowIcon(QIcon(r"C:\Users\nyrodrigues\Desktop\Teste_image\icone.png"))  # Adicione um ícone

        # --- IMAGEM DE FUNDO ---
        caminho_imagem = r"C:\Users\nyrodrigues\Desktop\Teste_image\imagem2.png"
        if os.path.exists(caminho_imagem):
            pixmap = QPixmap(caminho_imagem).scaled(700, 480, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            palette = QPalette()
            palette.setBrush(QPalette.Window, QBrush(pixmap))
            self.setPalette(palette)
        else:
            self.setStyleSheet("background-color: #23272A;")

        # --- Adicione os widgets ---
        self.lbl = QLabel("Monitoramento Olos, Horus & Salesforce")
        self.lbl.setStyleSheet("color: #00ff99; font-size: 20px; font-weight: bold;")
        self.lbl.setAlignment(Qt.AlignCenter)

        self.texto_log = QTextEdit()
        self.texto_log.setReadOnly(True)
        self.texto_log.setStyleSheet("background: #222; color: #00ff99; border-radius: 8px;")

        self.botao_iniciar = QPushButton("Iniciar Agendamento")
        self.botao_iniciar.setStyleSheet("background: #00ff99; color: #222; font-weight: bold; border-radius: 8px;")
        self.botao_iniciar.clicked.connect(self.agendador)

        # --- Layout ---
        layout = QVBoxLayout()
        layout.addWidget(self.lbl)
        layout.addWidget(self.texto_log)

        # Espaço extra antes do botão
        layout.addStretch(1)

        layout.addWidget(self.botao_iniciar)
        layout.setSpacing(16)
        layout.setContentsMargins(30, 30, 30, 50)  # Aumente o bottom para 50
        self.setLayout(layout)

        # Variáveis de controle
        self.agendamento_iniciado = False

    def log_mensagem(self, mensagem):
        data = datetime.now().strftime("[%H:%M:%S] ")
        self.texto_log.append(data + mensagem)

    def enviar_mensagem_whatsapp(self, caminho_imagem, mensagem_texto="Resultado até o momento"):
        driver = None
        try:
            if not os.path.exists(caminho_imagem):
                self.log_mensagem("❌ Caminho da imagem não encontrado.")
                return

            chrome_options = ChromeOptions()
            chrome_options.add_argument(f"--user-data-dir={caminho_sessao_whatsapp}")
            chrome_service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

            nome_grupo = "Report Diário CNC"  # Troque pelo nome exato do seu grupo
            driver.get("https://web.whatsapp.com")
            wait = WebDriverWait(driver, 60)
            wait.until(EC.presence_of_element_located((By.ID, 'side')))
            self.log_mensagem("WhatsApp Web carregado com sucesso.")
            
            # Seleciona o grupo (fixado ou via busca)
            grupo_selecionado = False
            try:
                grupo_fixado = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, f'//span[@title="{nome_grupo}"]'))
                )
                grupo_fixado.click()
                self.log_mensagem(f"✅ Grupo fixado '{nome_grupo}' encontrado e selecionado.")
                time.sleep(1)
                grupo_selecionado = True
            except Exception:
                try:
                    caixa_pesquisa = wait.until(EC.presence_of_element_located(
                        (By.XPATH, '//div[@title="Caixa de texto de pesquisa"]')))
                except:
                    caixa_pesquisa = wait.until(EC.presence_of_element_located(
                        (By.XPATH, '//div[@contenteditable="true" and @data-tab="3"]')))
                caixa_pesquisa.click()
                caixa_pesquisa.clear()
                caixa_pesquisa.send_keys(nome_grupo)
                time.sleep(2)
                try:
                    grupo = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, f'//span[@title="{nome_grupo}"]'))
                    )
                    grupo.click()
                    self.log_mensagem(f"✅ Grupo '{nome_grupo}' encontrado e selecionado via busca.")
                    time.sleep(1)
                    grupo_selecionado = True
                except Exception as e:
                    self.log_mensagem(f"[ERRO] Não encontrou o grupo '{nome_grupo}': {e}")
                    driver.quit()
                    return
            
            if not grupo_selecionado:
                self.log_mensagem(f"[ERRO] Não foi possível selecionar o grupo '{nome_grupo}'.")
                driver.quit()
                return
            
            # --- Daqui para baixo segue normalmente o envio da imagem ---
            try:
                botao_anexo = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div/div[1]/button')))
                botao_anexo.click()
                time.sleep(1)
            
                botao_imagem = wait.until(EC.presence_of_element_located(
                    (By.XPATH, '//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]')))
                botao_imagem.send_keys(caminho_imagem)
                self.log_mensagem("🖼️ Imagem anexada com sucesso.")
                time.sleep(3)
            
                campo_legenda = wait.until(EC.presence_of_element_located(
                    (By.XPATH, '//div[@role="textbox"]')))
                campo_legenda.click()
                campo_legenda.send_keys(mensagem_texto)
                time.sleep(1)
            
                ActionChains(driver).send_keys(Keys.ENTER).perform()
                time.sleep(5)
            
                try:
                    wait.until(EC.presence_of_element_located(
                        (By.XPATH, '//span[@data-icon="msg-dblcheck"]')), timeout=180)
                    self.log_mensagem("✅ Imagem e mensagem enviadas com sucesso!")
                except:
                    # Tenta reenviar se aparecer o ícone de erro
                    try:
                        erro_envio = driver.find_element(By.XPATH, '//span[@data-icon="alert-phone"]')
                        if erro_envio.is_displayed():
                            self.log_mensagem("❌ Falha no envio detectada, tentando reenviar...")
                            erro_envio.click()
                            time.sleep(10)
                            wait.until(EC.presence_of_element_located(
                                (By.XPATH, '//span[@data-icon="msg-dblcheck"]')), timeout=60)
                            self.log_mensagem("✅ Reenvio realizado com sucesso!")
                    except:
                        self.log_mensagem("⚠️ Não foi possível confirmar visualmente o envio, pode ter falhado.")
                    time.sleep(7)
            except Exception as e:
                self.log_mensagem(f"[ERRO] Falha ao anexar/enviar imagem: {e}")
            # ...existing code...

        finally:
            if driver:
                self.log_mensagem("🛑 Finalizando o driver do WhatsApp com sucesso.")
                time.sleep(2)               
                driver.quit()
            

    def ciclo(self):
        self.capturar_print_olos()
        time.sleep(10)
        self.capturar_print_horus()
        time.sleep(10)
        self.capturar_print_salesforce()
        # O agendamento do próximo ciclo agora é feito ao final do capturar_print_olos

    def capturar_print_olos(self):
        os.makedirs(pasta_destino_olos, exist_ok=True)
        chrome_options = ChromeOptions()
        chrome_options.add_argument("--window-size=1920,1200")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--window-position=-32000,-32000")

        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

        try:
            self.log_mensagem("Acessando Olos...")
            driver.get("http://10.195.226.6/Olos/Login.aspx?logout=true")
            wait = WebDriverWait(driver, 40)

            # Login
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="UserTxt"]')))
            input_usuario = driver.find_element(By.XPATH, '//*[@id="UserTxt"]')
            input_usuario.clear()
            input_usuario.send_keys("5693")
            self.log_mensagem("Usuário preenchido.")

            input_senha = driver.find_element(By.XPATH, '//*[@id="Password"]')
            input_senha.clear()
            input_senha.send_keys("1234")
            self.log_mensagem("Senha preenchida.")

            try:
                btn_login = driver.find_element(By.XPATH, '//*[@id="LoginBtn"]')
            except:
                btn_login = driver.find_element(By.XPATH, '//input[@type="submit"]')
            btn_login.click()
            self.log_mensagem("Login realizado.")

            # Monitoramento
            wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="ctl00_PageMenu_LinkButton1"]')))
            driver.find_element(By.XPATH, '//*[@id="ctl00_PageMenu_LinkButton1"]').click()
            self.log_mensagem("Acessando Monitoramento...")
            time.sleep(5)

            # Troca para a aba correta (OlosMonitor)
            encontrou = False
            for handle in driver.window_handles:
                driver.switch_to.window(handle)
                self.log_mensagem(f"Verificando aba: {driver.current_url}")
                if "/OlosMonitor/" in driver.current_url:
                    self.log_mensagem(f"Trocou para a aba correta: {driver.current_url}")
                    encontrou = True
                    break
            if not encontrou:
                self.log_mensagem("❌ Não encontrou a aba do Monitoramento correta!")
                return

            if "/OlosMonitor/" not in driver.current_url or "?access_token=" not in driver.current_url:
                self.log_mensagem("❌ Não está na aba do Monitoramento correta com access_token. Abortando passo a passo.")
                return

            # Aguarda o elemento 'app' aparecer na nova aba (até 60s)
            try:
                wait_nova_aba = WebDriverWait(driver, 60)
                wait_nova_aba.until(EC.presence_of_element_located((By.XPATH, '//*[@id="app"]')))
                self.log_mensagem("Elemento 'app' encontrado na nova aba.")
            except Exception as e:
                self.log_mensagem(f"[ERRO] Elemento 'app' não encontrado na nova aba: {e}")
                return

            # Campanhas
            try:
                wait_nova_aba.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/aside/div/div[2]/div/div/div[1]/div/div[2]/a/div[2]')))
                driver.find_element(By.XPATH, '//*[@id="app"]/div/aside/div/div[2]/div/div/div[1]/div/div[2]/a/div[2]').click()
                self.log_mensagem("Acessando Campanhas...")
                time.sleep(3)
            except Exception as e:
                self.log_mensagem(f"[ERRO] Não foi possível acessar Campanhas: {e}")
                return

            # Mais filtros
            try:
                xpath_mais_filtros = '//*[@id="app"]/div/div[2]/div/div[1]/div[2]/header/div[2]/div/a/div[1]'
                wait_nova_aba.until(EC.presence_of_element_located((By.XPATH, xpath_mais_filtros)))
                mais_filtros = driver.find_element(By.XPATH, xpath_mais_filtros)
                driver.execute_script("arguments[0].scrollIntoView(true);", mais_filtros)
                time.sleep(1)
                try:
                    mais_filtros.click()
                except Exception:
                    driver.execute_script("arguments[0].click();", mais_filtros)
                self.log_mensagem("Clicando em Mais filtros...")
                time.sleep(2)
            except Exception as e:
                self.log_mensagem(f"[ERRO] Não foi possível clicar em Mais filtros: {e}")
                return

            # Marcar "Somente com agentes"
            try:
                xpath_checkbox_label = "//label[contains(., 'Somente com agentes')]"
                wait_nova_aba.until(EC.element_to_be_clickable((By.XPATH, xpath_checkbox_label)))
                checkbox_label = driver.find_element(By.XPATH, xpath_checkbox_label)
                driver.execute_script("arguments[0].scrollIntoView(true);", checkbox_label)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", checkbox_label)
                self.log_mensagem("Marcando Somente com agentes (via label).")
                time.sleep(2)
            except Exception as e:
                self.log_mensagem(f"[ERRO] Não foi possível marcar Somente com agentes: {e}")
                return

            # Expandir o painel Receptivo
            try:
                xpath_receptivo = '//*[@id="app"]/div/div[2]/div/div[1]/div[2]/div[2]/div/div[2]/div/div/header/div[2]/a[1]/div[1]'
                wait_nova_aba.until(EC.element_to_be_clickable((By.XPATH, xpath_receptivo)))
                btn_receptivo = driver.find_element(By.XPATH, xpath_receptivo)
                driver.execute_script("arguments[0].scrollIntoView(true);", btn_receptivo)
                time.sleep(1)
                btn_receptivo.click()
                self.log_mensagem("Expandindo painel Receptivo...")
                time.sleep(3)
            except Exception as e:
                self.log_mensagem(f"[ERRO] Não foi possível expandir o painel Receptivo: {e}")
                return

            # Screenshot do painel correto
            try:
                painel = wait_nova_aba.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]')))
                driver.execute_script("arguments[0].scrollIntoView();", painel)
                time.sleep(2)
                nome_arquivo = f"olos_result_{datetime.now().strftime('%d_%H_%M_%S')}.png"
                caminho_final = os.path.join(pasta_destino_olos, nome_arquivo)
                painel.screenshot(caminho_final)
                msg = f"✅ Print importado para pasta: {nome_arquivo}"
                self.log_mensagem(msg)
                self.enviar_mensagem_whatsapp(caminho_final, "Cenário RC atual")
                time.sleep(3)
                # Agendamento do próximo ciclo aqui!
                self.log_mensagem(f"⏳ Próxima execução em {intervalo_minutos} minuto(s)...")
                threading.Timer(intervalo_minutos * 60, self.ciclo).start()
            except Exception as e:
                self.log_mensagem(f"[ERRO] Não foi possível capturar o print: {e}")
                return

        except Exception as e:
            self.log_mensagem(f"[ERRO] {e}")
        finally:
            driver.quit()

    def capturar_print_horus(self):
        os.makedirs(pasta_destino_horus, exist_ok=True)
        chrome_options = ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--window-position=-32000,-32000")

        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

        try:
            driver.get("https://horus.hiplatform.com/")
            wait = WebDriverWait(driver, 20)

            driver.find_element(By.XPATH, '//*[@id="new-access-page"]/input').click()
            self.log_mensagem("Acessando a página de login...")
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="login_login"]')))
            self.log_mensagem("Página de login carregada com sucesso.")
            time.sleep(1)

            input_login = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="login_login"]')))
            input_login.clear()
            input_login.send_keys("nikolas@cruzeirodosul.edu.br")
            self.log_mensagem("Preenchendo o campo de login...")
            time.sleep(1)

            input_senha = driver.find_element(By.XPATH, '//*[@id="login_password"]')
            input_senha.clear()
            input_senha.send_keys("NYR@2025")
            time.sleep(1)
            self.log_mensagem("Preenchendo o campo de senha...")
            self.log_mensagem("Tentando fazer login...")

            driver.find_element(By.XPATH, '//*[@id="login"]/form/div[3]/input').click()
            time.sleep(1)

            botao_produto = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="list-products"]/a/span[2]')))
            botao_produto.click()
            self.log_mensagem("Acessando o produto Horus...")
            time.sleep(30)

            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="#"]/ul/li[2]/span/a')))
            novo_elemento = driver.find_element(By.XPATH, '//*[@id="#"]/ul/li[2]/span/a')
            novo_elemento.click()
            self.log_mensagem("Novo XPath clicado com sucesso.")
            time.sleep(1)

            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="#"]/ul/li[2]/span/ul/li/a[2]')))
            segundo_elemento = driver.find_element(By.XPATH, '//*[@id="#"]/ul/li[2]/span/ul/li/a[2]')
            segundo_elemento.click()
            self.log_mensagem("Segundo botão XPath clicado com sucesso.")
            time.sleep(1)

            self.log_mensagem("Aguardando o painel de situação ser carregado...")
            painel_xpath = '//*[@id="dt-style-content"]/div[2]/div[1]'
            wait.until(EC.visibility_of_element_located((By.XPATH, painel_xpath)))
            time.sleep(1)
            painel = driver.find_element(By.XPATH, painel_xpath)
            driver.execute_script("arguments[0].scrollIntoView();", painel)
            time.sleep(2)

            nome_arquivo = f"horus_result_{datetime.now().strftime('%d_%H_%M_%S')}.png"
            caminho_final = os.path.join(pasta_destino_horus, nome_arquivo)
            painel.screenshot(caminho_final)

            msg = f"✅ Print importado para pasta: {nome_arquivo}"
            self.log_mensagem(msg)

            self.enviar_mensagem_whatsapp(caminho_final, "Cenário HI atual")
            time.sleep(3)

        except Exception as e:
            self.log_mensagem(f"[ERRO] {e}")
        finally:
            driver.quit()

    def capturar_print_salesforce(self):
        os.makedirs(pasta_destino_salesforce, exist_ok=True)
        chrome_options = ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,2000")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--window-position=-32000,-32000")
    
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
        wait = WebDriverWait(driver, 60)
    
        try:
            driver.get("https://cruzeirodosul.lightning.force.com/lightning/r/Dashboard/01ZNp000004ds1RMAQ/view?queryScope=userFolders")
    
            # Botão Microsoft 365
            wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="idp_section_buttons"]/button')))
            btn_microsoft_login = driver.find_element(By.XPATH, '//*[@id="idp_section_buttons"]/button')
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_microsoft_login)
            btn_microsoft_login.click()
    
            self.log_mensagem("Preenchendo email...")
            wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="i0116"]')))
            input_email = driver.find_element(By.XPATH, '//*[@id="i0116"]')
            input_email.clear()
            input_email.send_keys("nikolas@cruzeirodosul.edu.br")
    
            # Avançar
            wait.until(EC.element_to_be_clickable((By.ID, "idSIButton9")))
            btn_next = driver.find_element(By.ID, "idSIButton9")
            btn_next.click()
            time.sleep(1)
            #Inserindo a senha
            wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="i0118"]')))
            input_password = driver.find_element(By.XPATH, '//*[@id="i0118"]')
            input_password.clear()
            input_password.send_keys("Cads@51351999!")
            wait.until(EC.element_to_be_clickable((By.ID, "idSIButton9")))
            btn_sign_in = driver.find_element(By.ID, "idSIButton9")
            btn_sign_in.click()
    
            wait.until(EC.element_to_be_clickable((By.ID, "idSIButton9")))
            btn_stay_signed_in = driver.find_element(By.ID, "idSIButton9")
            btn_stay_signed_in.click()
    
            self.log_mensagem("Aguardando painel do Salesforce carregar...")
            driver.refresh()
            time.sleep(10)  # Aguarde o recarregamento
            painel_xpath = '//*[@id="main"]/div/div[1]/div/div/div/div[1]/div[2]/div[2]'
            painel = None
    
            for _ in range(30):
                try:
                    painel = driver.find_element(By.XPATH, painel_xpath)
                    if painel.is_displayed():
                        break
                except:
                    painel = None
                if not painel:
                    iframes = driver.find_elements(By.TAG_NAME, "iframe")
                    achou = False
                    for iframe in iframes:
                        driver.switch_to.frame(iframe)
                        try:
                            painel = driver.find_element(By.XPATH, painel_xpath)
                            if painel.is_displayed():
                                achou = True
                                break
                        except:
                            painel = None
                        driver.switch_to.default_content()
                    if achou:
                        break
                time.sleep(2)
    
            if not painel:
                raise Exception("Painel do Salesforce não encontrado!")
    
            # Busca o painel de forma robusta para evitar stale element
            from selenium.common.exceptions import StaleElementReferenceException
    
            for tentativa in range(3):
                try:
                    painel = driver.find_element(By.XPATH, painel_xpath)
                    driver.execute_script("arguments[0].scrollIntoView();", painel)
                    time.sleep(2)
                    nome_arquivo = f"salesforce_result_{datetime.now().strftime('%d_%H_%M_%S')}.png"
                    caminho_final = os.path.join(pasta_destino_salesforce, nome_arquivo)
                    painel.screenshot(caminho_final)
                    break
                except StaleElementReferenceException:
                    self.log_mensagem("StaleElementReferenceException ao capturar o painel, tentando novamente...")
                    time.sleep(2)
    
            msg = f"✅ Print importado para pasta: {nome_arquivo}"
            self.log_mensagem(msg)
    
            # Busca o horário do painel de forma robusta
            horario_xpath = '//*[contains(text(), "A partir de")]'
            for tentativa in range(3):
                try:
                    horario_elemento = driver.find_element(By.XPATH, horario_xpath)
                    horario_painel = horario_elemento.text
                    break
                except StaleElementReferenceException:
                    self.log_mensagem("StaleElementReferenceException ao buscar o horário do painel, tentando novamente...")
                    time.sleep(2)
            else:
                horario_painel = ""
    
            import re
            match = re.search(r'(\d{2}:\d{2})', horario_painel)
            if match:
                horario_final = match.group(1)
            else:
                horario_final = datetime.now().strftime('%H:%M')
    
            mensagem = f"Resultado hora x hora ({horario_final})"
            self.enviar_mensagem_whatsapp(caminho_final, mensagem)
            time.sleep(3)
    
        except Exception as e:
            self.log_mensagem(f"[ERRO] {e}")
        finally:
            driver.quit()

    def agendador(self):
        if self.agendamento_iniciado:
            self.log_mensagem("⚠️ O agendamento já está em execução.")
            return

        self.agendamento_iniciado = True
        self.log_mensagem("⏱️ Agendamento iniciado para Olos, Horus e Salesforce.")
        threading.Thread(target=self.ciclo, daemon=True).start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())