📈 Bitcoin Trading Bot com IA e Indicadores Técnicos
Este projeto implementa um bot de trading automatizado para Bitcoin, utilizando análise técnica e modelo de Machine Learning para tomada de decisões de compra e venda.

✅ Funcionalidades
Coleta histórica de dados do par BTC/USDT via Binance.

Cálculo automático de múltiplos indicadores técnicos:

RSI, MACD, EMA, ADX, OBV, Bollinger Bands, ATR, CCI, Stochastic, Williams %R.

Rotulagem automática de dados baseada no retorno futuro.

Treinamento de modelo de IA usando Gradient Boosting Classifier.

Execução automatizada de operações simuladas (buy/sell).

Controle e persistência do estado e histórico de operações.

Atualização automática do modelo a cada 24 horas.

Gravação de históricos em arquivos CSV.

🚀 Tecnologias utilizadas
Python (principal linguagem).

ccxt – coleta de dados de exchanges.

pandas, numpy – manipulação de dados.

scikit-learn – treinamento do modelo de IA.

ta-lib – indicadores técnicos.

joblib – serialização do modelo.

matplotlib – gráficos e visualizações.

zoneinfo – fuso horário.

csv – persistência de dados históricos.

🏗️ Arquitetura do Projeto
Coleta de dados: históricos de candles da Binance.

Adição de indicadores: cálculo automático de diversos indicadores técnicos.

Rotulagem: definição de sinais (compra, venda, neutro).

Treinamento: modelo supervisionado para prever sinais.

Execução: decisões de trading automatizadas com base na previsão do modelo.

Persistência: histórico de operações e capital atual gravados em CSV.

🔧 Como executar o projeto

1. Clone o repositório:
```bash
git clone https://github.com/seuusuario/seuprojeto.git
cd seuprojeto
```

2. Crie e ative um ambiente virtual (recomendado):
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure os parâmetros iniciais (opcional):
- Capital inicial (capital = 800.0)
- Par de trading (BTC/USDT)
- Timeframe (1h)
- Número de dias de histórico (dias = 365)

5. Execute o servidor:
```bash
# Navegue até o diretório do projeto
cd ia_btc_analise

# Inicie o servidor
python -m uvicorn backend:app --reload
```

6. Acesse a aplicação:
- Interface web: http://localhost:8000/static/index.html
- Documentação da API: http://localhost:8000/docs

📊 Arquivos gerados
historico_btc.csv → Histórico com indicadores.

dados_rotulados.csv → Dataset rotulado para treinamento.

modelo_ia_btc.pkl → Modelo de IA treinado.

rotulador_btc.pkl → Label encoder.

historico_operacoes.csv → Registro de operações realizadas.

📌 Como o bot decide operar?
Compra: se a previsão indicar compra e houver capital disponível.

Venda: se a previsão indicar venda e houver posição em BTC.

A cada ciclo (5 minutos), o bot:

Coleta o último candle.

Calcula indicadores.

Faz a previsão com IA.

Executa ou não uma operação.

Atualiza o histórico.

Treina novamente o modelo a cada 24h.

⚠️ Atenção
✅ Este projeto é educacional e não recomenda-se utilizar diretamente para operações financeiras reais sem ajustes e validações adicionais.

✅ O uso da API da Binance possui limites de requisição.

✅ Para uso real, considere adicionar:

Tratamento de exceções mais robusto.

Controle de risco mais refinado.

Mecanismos de autenticação para operações reais.

📝 Licença
Este projeto está licenciado sob a MIT License.

🤝 Contribuições
Contribuições são bem-vindas!
Para contribuir, abra uma issue ou envie um pull request.

