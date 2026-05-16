# Market Intelligence Pipeline - Web Scraper & Event-Driven Alerts

Sistema avançado de Engenharia de Dados focado em inteligência de mercado (Pricing). A solução atua como um robô autônomo que realiza o scraping de catálogos de e-commerce, higieniza os dados capturados, aplica lógica de validação via Banco de Dados Relacional e dispara notificações ativas em tempo real para equipes operacionais.

## Arquitetura do Sistema

O projeto integra padrões de ETL com Arquitetura Baseada em Eventos (Event-Driven):

1. Extraction & Parsing: Crawler paginado assíncrono varre o catálogo alvo simulando requisições controladas (`throttling`), transformando o DOM HTML em objetos manipuláveis.
2. Transform (Data Cleaning): Sanitização de strings monetárias e casting para dados numéricos.
3. Load & Validation (SQL): Os dados aprovados pelos filtros de negócios tentam ser persistidos em um banco de dados relacional (`SQLite`). Constraints de unicidade (UNIQUE) bloqueiam duplicações.
4. Messaging (Push Notifications): Caso um registro novo seja efetivado no SQL, o sistema engatilha um webhook para a API do Telegram, entregando alertas formatados para grupos de resposta rápida.

## Stack Tecnológica

- Core: Python 3
- Data Extractor: `requests` & `BeautifulSoup4`
- Database: `sqlite3` (Manipulação DDL e DML com mitigação de injeção SQL)
- Integration: `pyTelegramBotAPI` (Mensageria e Alertas)
- Security: `python-dotenv` (Gestão de segredos e isolamento de ambiente)

## Instruções de Execução Local

1. Realize o clone do repositório:
```bash
git clone https://github.com/alvarobandim/automacao_web_scraping.git
```

2. Instale as dependências:
```bash
pip install requests beautifulsoup4 pyTelegramBotAPI python-dotenv
```

3. Configure o ambiente seguro:
Crie um arquivo chamado `.env` na raiz do projeto e insira as suas credenciais do Telegram:
```text
TELEGRAM_TOKEN=seu_token_aqui
ID_GRUPO_NOTIFICACAO=seu_id_aqui
```

4. Execute o robô de extração:
```bash
python scraper.py
```