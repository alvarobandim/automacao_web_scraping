# Web Scraper de E-commerce - Pipeline ETL

Solução automatizada de engenharia de dados voltada para inteligência de mercado (Pricing Intelligence). O sistema executa requisições de rede agendadas, realiza o parse do DOM HTML de forma paginada, executa rotinas de sanitização de dados e aplica filtros baseados em regras de negócio predefinidas.

## Arquitetura do Sistema

O fluxo de processamento de dados foi construído seguindo o ciclo clássico de um pipeline ETL:

1. Extraction (Extração): Navegação sequencial parametrizada (Crawler) através de múltiplas páginas de catálogo utilizando requisições HTTP assíncronas. Inclui técnica de throttling para controle de taxa e prevenção de bloqueios por IP.
2. Transformation (Transformação): Varredura das tags estruturais do HTML, isolamento de atributos específicos, higienização de strings monetárias (limpeza de caracteres especiais) e coerção de tipos de dados (parsing de String para Float). Filtragem automatizada com base em regras de margem de preço.
3. Loading (Carga): Agregação de objetos estruturados em um DataFrame do Pandas e persistência dos dados purificados em formato openpyxl (Excel) para consumo analítico.

## Stack Tecnológica

- Linguagem: Python 3
- Camada de Rede: Requests (HTTP client)
- Camada de Parsing: BeautifulSoup4 (HTML parser)
- Camada de Análise e Carga: Pandas (Engine de manipulação tabular e I/O de dados)

## Instruções de Execução Local

1. Realize o clone do repositório em seu ambiente:
```bash
git clone [https://github.com/alvarobandim/automacao_web_scraping.git](https://github.com/alvarobandim/automacao_web_scraping.git)
```

2. Instale as dependências listadas no projeto via gerenciador de pacotes:
```bash
pip install requests beautifulsoup4 pandas openpyxl
```

3. Execute o script principal para inicializar a esteira de dados:
```bash
python scraper.py
```

4. Após a conclusão do processo, o dataset estruturado estará disponível no arquivo local `oportunidades_livros.xlsx`.