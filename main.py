import streamlit as st
import datetime as dt
from datetime import datetime
import pandas as pd
import pandas_datareader
from pandas_datareader import data as pdr
import matplotlib.pyplot as plt
import matplotlib.cbook as cbook
import matplotlib.dates as mdates
from matplotlib import style
from matplotlib import ticker
from random import randint



import yfinance as yf
import numpy as np

import math

yf.pdr_override()
#-------------------
#-------------------
start = dt.datetime(2010,10,1)
end = dt.datetime(2023,12,31)
stock = "EURUSD=X"
period = 12

df = pdr.get_data_yahoo(stock, start, end)
df.drop(["Open", "High", "Low", "Close", "Volume"], axis = 1, inplace = True)
df["Year"] = df.index.year
df["Month"] = pd.to_datetime(df.index).strftime("%B")
df["Day"] = pd.to_datetime(df.index).strftime("%d-%B")
df["MVG"] = df["Adj Close"].ewm(span = period).mean()

elenco_anni = df["Year"].unique()


df = df.drop(df[df['Year'] == elenco_anni[0]].index)
df.reset_index(inplace = True)
df.set_index("Day", inplace = True)

elenco_anni = df["Year"].unique()
elenco_mesi = df["Month"].unique()

date_bisestile = pd.date_range('2020-01-01', '2020-12-31').strftime('%d-%B')

ritorni_df = pd.DataFrame()
ritorni_df["Data"] = date_bisestile

ritorni_df.reset_index(inplace = True)

ritorni_df.set_index("Data", inplace = True)

#ritorno giornaliero cumulato
for anno in elenco_anni:
  ritorni_df[anno] = ( df.loc[df["Year"] == anno, "MVG"] / df.loc[df["Year"] == anno, "MVG"].iloc[0] ) -1

ritorni_df.ffill(inplace = True)
ritorni_df.bfill(inplace = True)

ritorni_df.drop("index", axis = 1, inplace = True)

#----------------------------------------------------------------
correlazione_df = pd.DataFrame()
correlazione_df["Data"] = ritorni_df.index
correlazione_df.reset_index(inplace = True)
correlazione_df.set_index("Data", inplace = True)
correlazione_df.drop("index", axis = 1, inplace = True)

mese = "."

for x in correlazione_df.index:
  volatilita_mese = 0
  mese = x[3:]
  if x[3:] == mese:
    correlazione_mese = ritorni_df.loc[ritorni_df.index.str.slice(3) == mese].corr(numeric_only = True).iloc[0].mean()

  if x[0:2] == "31":
    print(x)
    temp =(ritorni_df.loc[ritorni_df.index.str.slice(3) == mese])
    volatilita_mese = temp.loc[temp.index.str.slice(0,2) == "31"].std(axis = 1)[0]
    correlazione_df.loc[correlazione_df.index.str.slice(3) == mese, "Dispersione"] = volatilita_mese


  if x[0:2]== "30" and (mese == "November" or mese == "April" or mese == "June" or mese == "September"):
    print(x)
    temp =(ritorni_df.loc[ritorni_df.index.str.slice(3) == mese])
    volatilita_mese = temp.loc[temp.index.str.slice(0,2) == "30"].std(axis = 1)[0]
    correlazione_df.loc[correlazione_df.index.str.slice(3) == mese, "Dispersione"] = volatilita_mese


  if x[0:2] == "28" and mese == "February":
    print(x)
    temp =(ritorni_df.loc[ritorni_df.index.str.slice(3) == mese])
    volatilita_mese = temp.loc[temp.index.str.slice(0,2) == "28"].std(axis = 1)[0]
    print(volatilita_mese)
    correlazione_df.loc[correlazione_df.index.str.slice(3) == mese, "Dispersione"] = volatilita_mese


  correlazione_df.loc[x, "Correlazione"] = correlazione_mese
  #correlazione_df.loc[correlazione_df.index.str.slice(3) == mese, "Dispersione"] = volatilita_mese

#normalize data
correlazione_df["Dispersione"] = correlazione_df["Dispersione"] / (correlazione_df["Dispersione"].max())




elenco_colori = []
for i in range(len(elenco_anni)):
    elenco_colori.append('#%06X' % randint(0, 0xFFFFFF))





fig = plt.figure(figsize=(10, 6), facecolor='white',
                 layout='constrained')
fig.suptitle(stock)
ax = fig.add_subplot()
plt.ylabel("% Return")
plt.rcParams["font.family"] = 'sans serif'
plt.rcParams["font.size"] = 15


ritorni_df["media"] = ritorni_df[elenco_anni].mean(axis = 1)

for anno in elenco_anni:
  colore = elenco_colori[elenco_anni.tolist().index(anno)]
  for mese in elenco_mesi:
    spessore =  (ritorni_df[[anno, "media"]].corr().iloc[0,1] + 1) / 2
    #trasparenza = (ritorni_df.loc[ritorni_df.index.str.slice(3) == mese][[anno, "media"]].corr().iloc[0,1] + 1) / 2
    trasparenza = 0.9


    ax.plot(ritorni_df.loc[ritorni_df.index.str.slice(3) == mese].index,
            ritorni_df.loc[ritorni_df.index.str.slice(3) == mese][anno]*100,
            linewidth = 4*(spessore), alpha = trasparenza, markersize = 1, color = colore)

ampiezza_stackplot = ritorni_df.loc[ritorni_df.index.str.slice(3) == mese].max().max()*100

ax.stackplot(ritorni_df.index, (1.2 - correlazione_df["Dispersione"])*ampiezza_stackplot, alpha = 0.6, color = "gray", labels = ["Dispersione"])
ax.plot(ritorni_df.index, ritorni_df["media"]*100, linewidth = 5, color = "black", label = "Media")

ax.legend(loc = "upper center")

positions = [0,31,59,90,120, 151, 182, 213, 243, 274, 305, 335]
labels = ['Jan', "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Ott", "Nov", "Dec"]
ax.xaxis.set_major_locator(ticker.FixedLocator(positions))
ax.xaxis.set_major_formatter(ticker.FixedFormatter(labels))

#-------------------
#-------------------

st.header("LA STAGIONALITA' SUI MERCATI FINANZIARI")
st.write("""La stagionalità si riferisce alla tendenza dei prezzi di alcuni titoli di seguire movimenti ricorrenti o cicli in un determinato periodo dell’anno.
Questo fenomeno è causato da molteplici fattori, tra i più impattanti risultano gli eventi politici ed economici (elezioni e trimestrali), i cicli di produzione e consumo e la stagionalità di alcuni beni o servizi (soprattutto per quanto riguarda il settore energetico e le commodities).

L’obiettivo di questo articolo è mostrare un metodo per analizzare e visualizzare i pattern ricorrenti di qualsiasi titolo quotato sui mercati; lo studio si concentra però su cinque di essi, proponendo uno studio di 10 anni passati e concentrandosi sulla correlazione statistica mese per mese.")
""")
st.markdown("""
La scelta dei titoli non è casuale, sono stati infatti selezionati i 5 riportati in seguito che, per diversi motivi; si prestano a essere soggetti di tale analisi.

- EUR/USD
- CORN FUTURES
- VOLATILITY INDEX
- NASDAQ 100
- MSFT 
            """)


#st.code()
#st.dataframe()
#st.pyplot()





#-------------------------------------------------
st.divider()
st.subheader("PROCEDIMENTO")
st.write("Per il primo titolo preso in considerazione è riportato parte del procedimento svolto per ottenere i grafici visualizzati in seguito, per i restanti vengono solo riportati i risultati e le conclusioni.")
st.subheader("IMPORTAZIONE E PULIZIA DEI DATI")
st.write("""
Con la libreria yahoofinance si importano in dataframe pandas tutto lo storico dei prezzi negli ultimi 10 anni.
Se non viene direttamente esplicitato, anche per i restanti titoli si analizza la stagionalità a partire dall'ultimo decennio.
Viene mantenuto solo l’Adj. Close (i restanti numeri sono inutili per i fini di questo studio) e ne viene calcolata la media mobile esponenziale a 12 giorni per ridurre l’influenza delle oscillazioni di prezzo.
         """)
st.code("""
start = dt.datetime(2010,10,1)
end = dt.datetime(2023,12,31)
df = pdr.get_data_yahoo(stock, start, end)
df.drop(["Open", "High", "Low", "Close", "Volume"], axis = 1, inplace = True)
df["MVG"] = df["Adj Close"].ewm(span = period).mean()

"""

)
st.subheader("MERGE DEI DATI")
st.write("""
Per ogni anno preso in condierazione si calcola il ritorno cumulato per ogni giorno dell’anno e si inseriscono i valori ottenuti in un nuovo dataframe **ritorni_df** avente sulle righe tutti i giorni di un anno e sulle colonne i ritorni giornalieri per ciascun anno (1).
         """
)
st.code(
  """
for anno in elenco_anni:
  ritorni_df[anno] = ( df.loc[df["Year"] == anno, "MVG"] / df.loc[df["Year"] == anno, "MVG"].iloc[0] ) -1

"""
)
st.write("Il dataframe ottenuto si presenta così:")
st.dataframe(ritorni_df)
st.subheader("CALCOLO DELLA STAGIONALITA'")
st.write(
"""
Si crea un dataframe vuoto avente come asse x tutti i giorni dell’anno (ugualmente a come si era fatto per **ritorni_df**) e la colonna “correlazione” in cui viene calcolata la correlazione dei ritorni mese per mese con il metodo pearson.
""")
st.code(
  """
correlazione_mese = ritorni_df.loc[ritorni_df.index.str.slice(3) == mese].corr(numeric_only = True).iloc[0].mean()

"""
)
st.write("""
Il dato ottenuto non è particolarmente significativo per lo studio della stagionalità: mette in mostra infatti come i prezzi si muovono coerentemente durante il mese e non si concentra su quanto i ritorni mensili siano effettivamente simili nel corso degli anni.
Per fare ciò si calcola, mese per mese, la deviazione standard del ritorno mensile nei diversi anni per mostrare quanto tali rendimenti si discostino, annata per annata, dalla media su 10 anni del mese in considerazione.
""")
st.code(
  """
volatilita_mese = temp.loc[temp.index.str.slice(0,2) == "31"].std(axis = 1)[0]
correlazione_df.loc[correlazione_df.index.str.slice(3) == mese, "Dispersione"] = volatilita_mese
"""
)
st.write("""
I risultati sono immagazzinati nel dataframe **correlazione_df.**
"""
)
st.dataframe(correlazione_df)
st.subheader("VISUALIZZAZIONE DEI DATI")
st.write(
  """
Per visualizzare il lavoro si è cercato di condensare in un unica immagino il maggior numero dei dati ottenuti precedentemente.

Il grafico infatti riporta gli andamenti dei ritorni giornalieri annata per annata calcolati in **ritorni_df**, si noti che in questo caso lo spessore varia (è direttamente proporzionale alla correlazione tra l’anno in questione e la media tra tutti gli 

E’ stata anche aggiunta una media arimetica dell’andamento dei rendimenti tra i 10 anni (in nero e con maggiore spessore).

L’istogramma infine cerca di rappresentare quanto il titolo in esame abbia un comportamento stagionale mese per mese partendo dalla variazione standard in correlazioni_df (maggiore è la deviazione standard in un mese e minore sarà l’altezza dell’istogramma dal momento che maggiore dispersione nei rendimenti mensili significa minor allineamento dei ritorni verso un valore simile).
"""
)
st.pyplot(fig)
st.write(""" 
Trattandosi di un titolo poco volatile, il grafico della media riporta piccole variazioni ed è poco leggibile, per visualizzare meglio la stagionalità dello strumento viene quindi proposto il grafico in cui compare esclusivamente la media:
         """)


fig2 = plt.figure(figsize=(10, 6), facecolor='white',
                 layout='constrained')
fig2.suptitle(stock)
ax2 = fig2.add_subplot()
plt.ylabel("% Return")
plt.rcParams["font.family"] = 'sans serif'
plt.rcParams["font.size"] = 15


ritorni_df["media"] = ritorni_df[elenco_anni].mean(axis = 1)


ampiezza_stackplot = ritorni_df["media"] .max()*100

ax2.plot(ritorni_df.index, ritorni_df["media"]*100, linewidth = 5, color = "black", label = "Media")

ax.legend(loc = "upper center")

positions = [0,31,59,90,120, 151, 182, 213, 243, 274, 305, 335]
labels = ['Jan', "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Ott", "Nov", "Dec"]
ax2.xaxis.set_major_locator(ticker.FixedLocator(positions))
ax2.xaxis.set_major_formatter(ticker.FixedFormatter(labels))


st.pyplot(fig2)
st.divider()
st.subheader("Note")
st.write("""
(1): Il dataframe contiene tutti i 366 giorni di un anno bisestile, i dati mancanti per i giorni di chiusura sono ottenuti a partire dall'ultimo prezzo disponibile.
         
(2): La variazione standard riportata nel dataframe è normalizzata tra 0 e 1 e nel grafico è scalata affinchè compaia leggibile.
         """)


#-------------------------------
st.divider()
st.header("CONFRONTO TRA TITOLI")

lista_titoli = ["EURUSD=X", "ZC=F", "^VIX", "NQ=F", "MSFT"]

start = dt.datetime(2010,10,1)
end = dt.datetime(2023,12,31)
period = 12

for titolo in lista_titoli:

  stock = titolo

  df = pdr.get_data_yahoo(stock, start, end)
  df.drop(["Open", "High", "Low", "Close", "Volume"], axis = 1, inplace = True)
  df["Year"] = df.index.year
  df["Month"] = pd.to_datetime(df.index).strftime("%B")
  df["Day"] = pd.to_datetime(df.index).strftime("%d-%B")
  df["MVG"] = df["Adj Close"].ewm(span = period).mean()

  elenco_anni = df["Year"].unique()


  df = df.drop(df[df['Year'] == elenco_anni[0]].index)
  df.reset_index(inplace = True)
  df.set_index("Day", inplace = True)

  elenco_anni = df["Year"].unique()
  elenco_mesi = df["Month"].unique()

  date_bisestile = pd.date_range('2020-01-01', '2020-12-31').strftime('%d-%B')

  ritorni_df = pd.DataFrame()
  ritorni_df["Data"] = date_bisestile

  ritorni_df.reset_index(inplace = True)

  ritorni_df.set_index("Data", inplace = True)

  #ritorno giornaliero cumulato
  for anno in elenco_anni:
    ritorni_df[anno] = ( df.loc[df["Year"] == anno, "MVG"] / df.loc[df["Year"] == anno, "MVG"].iloc[0] ) -1

  ritorni_df.ffill(inplace = True)
  ritorni_df.bfill(inplace = True)

  ritorni_df.drop("index", axis = 1, inplace = True)

  #----------------------------------------------------------------
  correlazione_df = pd.DataFrame()
  correlazione_df["Data"] = ritorni_df.index
  correlazione_df.reset_index(inplace = True)
  correlazione_df.set_index("Data", inplace = True)
  correlazione_df.drop("index", axis = 1, inplace = True)

  mese = "."

  for x in correlazione_df.index:
    volatilita_mese = 0
    mese = x[3:]
    if x[3:] == mese:
      correlazione_mese = ritorni_df.loc[ritorni_df.index.str.slice(3) == mese].corr(numeric_only = True).iloc[0].mean()

    if x[0:2] == "31":
      print(x)
      temp =(ritorni_df.loc[ritorni_df.index.str.slice(3) == mese])
      volatilita_mese = temp.loc[temp.index.str.slice(0,2) == "31"].std(axis = 1)[0]
      correlazione_df.loc[correlazione_df.index.str.slice(3) == mese, "Dispersione"] = volatilita_mese


    if x[0:2]== "30" and (mese == "November" or mese == "April" or mese == "June" or mese == "September"):
      print(x)
      temp =(ritorni_df.loc[ritorni_df.index.str.slice(3) == mese])
      volatilita_mese = temp.loc[temp.index.str.slice(0,2) == "30"].std(axis = 1)[0]
      correlazione_df.loc[correlazione_df.index.str.slice(3) == mese, "Dispersione"] = volatilita_mese


    if x[0:2] == "28" and mese == "February":
      print(x)
      temp =(ritorni_df.loc[ritorni_df.index.str.slice(3) == mese])
      volatilita_mese = temp.loc[temp.index.str.slice(0,2) == "28"].std(axis = 1)[0]
      print(volatilita_mese)
      correlazione_df.loc[correlazione_df.index.str.slice(3) == mese, "Dispersione"] = volatilita_mese


    correlazione_df.loc[x, "Correlazione"] = correlazione_mese
    #correlazione_df.loc[correlazione_df.index.str.slice(3) == mese, "Dispersione"] = volatilita_mese

  #normalize data
  correlazione_df["Dispersione"] = correlazione_df["Dispersione"] / (correlazione_df["Dispersione"].max())




  elenco_colori = []
  for i in range(len(elenco_anni)):
      elenco_colori.append('#%06X' % randint(0, 0xFFFFFF))





  fig = plt.figure(figsize=(10, 6), facecolor='white',
                  layout='constrained')
  fig.suptitle(stock)
  ax = fig.add_subplot()
  plt.ylabel("% Return")
  plt.rcParams["font.family"] = 'sans serif'
  plt.rcParams["font.size"] = 15


  ritorni_df["media"] = ritorni_df[elenco_anni].mean(axis = 1)

  for anno in elenco_anni:
    colore = elenco_colori[elenco_anni.tolist().index(anno)]
    for mese in elenco_mesi:
      spessore =  (ritorni_df[[anno, "media"]].corr().iloc[0,1] + 1) / 2
      #trasparenza = (ritorni_df.loc[ritorni_df.index.str.slice(3) == mese][[anno, "media"]].corr().iloc[0,1] + 1) / 2
      trasparenza = 0.9


      ax.plot(ritorni_df.loc[ritorni_df.index.str.slice(3) == mese].index,
              ritorni_df.loc[ritorni_df.index.str.slice(3) == mese][anno]*100,
              linewidth = 4*(spessore), alpha = trasparenza, markersize = 1, color = colore)

  ampiezza_stackplot = ritorni_df.loc[ritorni_df.index.str.slice(3) == mese].max().max()*100

  ax.stackplot(ritorni_df.index, (1.2 - correlazione_df["Dispersione"])*ampiezza_stackplot, alpha = 0.6, color = "gray", labels = ["Dispersione"])
  ax.plot(ritorni_df.index, ritorni_df["media"]*100, linewidth = 5, color = "black", label = "Media")

  ax.legend(loc = "upper center")

  positions = [0,31,59,90,120, 151, 182, 213, 243, 274, 305, 335]
  labels = ['Jan', "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Ott", "Nov", "Dec"]
  ax.xaxis.set_major_locator(ticker.FixedLocator(positions))
  ax.xaxis.set_major_formatter(ticker.FixedFormatter(labels))
  st.subheader(titolo)
  st.pyplot(fig)