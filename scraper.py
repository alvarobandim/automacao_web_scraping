"""
Module: Advanced ETL Data Pipeline & Event-Driven Alert System
Description: Crawler multipage com persistência relacional (SQLite), Data Cleaning,
             e disparos assíncronos de notificações via Telegram API.
             Arquitetura segura baseada em variáveis de ambiente (.env).
Author: Alvaro Bandim
"""

import os
import time
import sqlite3
import requests
from bs4 import BeautifulSoup
import telebot
from dotenv import load_dotenv

# --- Configurações de Infraestrutura e Segurança ---
# Carrega as credenciais do cofre local (.env)
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ID_GRUPO_NOTIFICACAO = os.getenv("ID_GRUPO_NOTIFICACAO")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
DB_NAME = "marketplace_intelligence.db"

# --- Parâmetros de Negócio ---
URL_TARGET_TEMPLATE = "https://books.toscrape.com/catalogue/page-{}.html"
MAX_PAGES = 5
PRICE_THRESHOLD = 20.00  # Cut-off de aprovação


def inicializar_banco_dados():
    """Conecta ao SQLite e aplica a DDL da tabela com constraint de unicidade."""
    conexao = sqlite3.connect(DB_NAME)
    cursor = conexao.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS promocoes_livros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT UNIQUE,
            preco REAL,
            pagina_origem INTEGER,
            timestamp_coleta DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conexao.commit()
    conexao.close()
    print("[DB] Infraestrutura relacional sincronizada.")


def processar_e_notificar_oportunidade(titulo, preco, pagina):
    """
    Tenta persistir o registro (Insert). Caso seja um novo registro (não fira o UNIQUE),
    dispara o gatilho de notificação para a mensageria (Event-Driven).
    """
    conexao = sqlite3.connect(DB_NAME)
    cursor = conexao.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO promocoes_livros (titulo, preco, pagina_origem) 
            VALUES (?, ?, ?)
        """, (titulo, preco, pagina))
        conexao.commit()
        
        print(f"   [DB] Registro persistido: {titulo}")
        
        # Payload do Push Notification
        alerta = (
            f"🚨 **ALERTA DE OPORTUNIDADE** 🚨\n\n"
            f"📘 Produto: {titulo}\n"
            f"💰 Valor: £{preco}\n"
            f"📍 Origem: Página {pagina}\n"
            f"🤖 Status: Salvo no SQL."
        )
        bot.send_message(ID_GRUPO_NOTIFICACAO, alerta, parse_mode="Markdown")
        
    except sqlite3.IntegrityError:
        print(f"   [SKIP] Registro já mapeado no SQL: {titulo}")
        
    finally:
        conexao.close()


if __name__ == "__main__":
    print("[INFO] Inicializando Data Pipeline V3.0...")
    inicializar_banco_dados()
    
    for current_page in range(1, MAX_PAGES + 1):
        target_url = URL_TARGET_TEMPLATE.format(current_page)
        print(f"[FETCH] Ingerindo dados: {target_url}")
        
        response = requests.get(target_url)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            product_nodes = soup.find_all("article", class_="product_pod")
            
            for node in product_nodes:
                raw_title = node.h3.a["title"]
                raw_price = node.find("p", class_="price_color").text
                
                # Data Cleaning
                sanitized_price = float(raw_price.replace("£", ""))
                
                # Aplicação da regra de negócio
                if sanitized_price < PRICE_THRESHOLD:
                    processar_e_notificar_oportunidade(raw_title, sanitized_price, current_page)
                    
            # Throttling
            time.sleep(1)
        else:
            print(f"[ERROR] Timeout/Block. HTTP Status: {response.status_code}")
            
    print("\n[SUCCESS] Varredura e mensageria concluídas.")