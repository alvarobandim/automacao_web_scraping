"""
Module: Data Pipeline Extractor (ETL)
Description: Algoritmo de automação para extração paginada de catálogo de e-commerce,
             contendo processos de sanitização de strings, type casting e persistência local.
Author: Alvaro Bandim
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# --- Configurações de Escopo e Regras de Negócio ---
URL_TARGET_TEMPLATE = "https://books.toscrape.com/catalogue/page-{}.html"
OUTPUT_FILE_PATH = "oportunidades_livros.xlsx"
MAX_PAGES = 5
PRICE_THRESHOLD = 20.00  # Critério de corte para filtragem de registros

print(f"[INFO] Inicializando pipeline ETL. Target: {MAX_PAGES} páginas.")
print(f"[INFO] Aplicando threshold de negócios: valores inferiores a £{PRICE_THRESHOLD}\n")

processed_dataset = []

# --- Loop Principal: Navegação Dinâmica (Crawler) ---
for current_page in range(1, MAX_PAGES + 1):
    
    target_url = URL_TARGET_TEMPLATE.format(current_page)
    print(f"[FETCH] Requisitando payload de: {target_url}")
    
    response = requests.get(target_url)
    
    if response.status_code == 200:
        # Inicialização do parser do DOM HTML
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Mapeamento e captura dos nós correspondentes aos produtos
        product_nodes = soup.find_all("article", class_="product_pod")
        
        # --- Loop Secundário: Extração de Atributos por Nó ---
        for node in product_nodes:
            raw_title = node.h3.a["title"]
            raw_price = node.find("p", class_="price_color").text
            
            # Data Cleaning: Sanitização da string monetária e Type Casting para Float
            sanitized_price = float(raw_price.replace("£", ""))
            
            # Aplicação da Regra de Negócio (Filtro de Ingestão)
            if sanitized_price < PRICE_THRESHOLD:
                processed_dataset.append({
                    "product_title": raw_title,
                    "price_currency_pounds": sanitized_price,
                    "source_page": current_page
                })
                print(f"   [MATCH] Registro capturado: {raw_title} | £{sanitized_price}")
                
        # Throttling: Delay estratégico para controle de taxa de requisições (boas práticas de rede)
        time.sleep(1)
        
    else:
        print(f"[ERROR] Falha na requisição da página {current_page}. HTTP Status: {response.status_code}")

# --- Fase de Carga (Load / Persistência) ---
total_records = len(processed_dataset)
print(f"\n[INFO] Execução do crawler finalizada. Total de registros validados: {total_records}")

if total_records > 0:
    print(f"[INFO] Instanciando DataFrame e exportando dados para {OUTPUT_FILE_PATH}...")
    
    # Estruturação e persistência de dados em formato tabular
    df = pd.DataFrame(processed_dataset)
    df.to_excel(OUTPUT_FILE_PATH, index=False)
    
    print("[SUCCESS] Pipeline de dados concluído com sucesso.")
else:
    print("[INFO] Pipeline encerrado sem registros correspondentes ao filtro. Nenhuma planilha gerada.")