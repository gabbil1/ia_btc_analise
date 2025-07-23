import requests
from textblob import TextBlob
from bs4 import BeautifulSoup

def buscar_manchetes_google_news(query="bitcoin", num=10):
    url = f"https://news.google.com/rss/search?q={query}+when:7d&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    resp = requests.get(url)
    soup = BeautifulSoup(resp.content, features="xml")
    titulos = [item.title.text for item in soup.findAll('item')][:num]
    return titulos

def analisar_sentimento_manchetes(manchetes):
    scores = []
    for texto in manchetes:
        blob = TextBlob(texto)
        scores.append(blob.sentiment.polarity)
    if scores:
        return sum(scores)/len(scores)
    return 0.0

def sentimento_bitcoin():
    manchetes = buscar_manchetes_google_news()
    return analisar_sentimento_manchetes(manchetes) 