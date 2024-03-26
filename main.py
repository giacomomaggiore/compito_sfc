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
start = dt.datetime(2020,10,1)
end = dt.datetime(2023,12,31)
stock = "EUR/USD=X"
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


st.header("""
:red[LA STAGIONALITA' SUI MERCATI FINANZIARI]
"""
            
)

st.write("""La stagionalità si riferisce alla tendenza dei prezzi di alcuni titoli di seguire movimenti ricorrenti o cicli in un determinato periodo dell’anno.
Questo fenomeno è causato da molteplici fattori, tra i più impattanti risultano gli **eventi politici ed economici** (elezioni e trimestrali ad esempio), i **cicli di produzione e consumo** e la **stagionalità di alcuni beni o servizi** (soprattutto per quanto riguarda il settore energetico e le commodities).

L’obiettivo di questo articolo è mostrare un metodo per analizzare e visualizzare i pattern ricorrenti di qualsiasi titolo quotato sui mercati; lo studio si concentra però su cinque di essi, proponendo **uno studio di 10 anni passati** e concentrandosi sulla **correlazione statistica mese per mese**.
""")
st.markdown("""
La scelta dei titoli non è casuale, sono stati infatti selezionati i 5 riportati in seguito che, per diversi motivi; si prestano a essere soggetti di tale analisi.

- Cambio Euro Dollaro - **(EURUSD=X)**
- Futures sul Mais    - **(ZC=F)**
- Volatility Index -    **(^VIX)**
- NASDAQ 100        -    **(NQ=F)**
- Microsoft          -   **(MSFT)**
            
*[Per saltare il procedimento e visualizzare subito il confronto tra titoli clicca qui.](#confronto-tra-titoli)*
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
Con la libreria **yahoofinance** si importa in **dataframe pandas** tutto lo storico dei prezzi negli ultimi 10 anni.
Se non viene direttamente esplicitato, anche per i restanti titoli si analizza la stagionalità a partire dall'ultimo decennio.
Viene mantenuto solo **l’Adj. Close** (i restanti numeri sono inutili per i fini di questo studio) e ne viene calcolata la **media mobile esponenziale** a 12 giorni per ridurre l’influenza delle oscillazioni di prezzo.
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
Per ogni anno preso in considerazione si calcola il **ritorno cumulato** per ogni giorno dell’anno e si inseriscono i valori ottenuti in un nuovo dataframe **ritorni_df**, avente sulle righe tutti i giorni di un anno e sulle colonne i ritorni giornalieri per ciascun anno (1).

L'ultima colonna contiene la media aritmetica dei ritorni giornalieri tra tutti gli anni.
                 """
)
st.code(
  """
elenco_anni = df["Year"].unique()
for anno in elenco_anni:
  ritorni_df[anno] = ( df.loc[df["Year"] == anno, "MVG"] / df.loc[df["Year"] == anno, "MVG"].iloc[0] ) -1
ritorni_df["media"] = ritorni_df[elenco_anni].mean(axis = 1)

"""
)
st.write("Il dataframe ottenuto si presenta così: (2)")
st.dataframe(ritorni_df)
st.subheader("CALCOLO DELLA STAGIONALITA'")
st.write(
"""
Si crea un dataframe vuoto avente sull'asse x **tutti i giorni dell’anno** (ugualmente a come si era fatto per **ritorni_df**), una colonna “correlazione” in cui viene calcolata la **correlazione** dei ritorni mese per mese (3).
""")
st.code(
  """
correlazione_mese = ritorni_df.loc[ritorni_df.index.str.slice(3) == mese].corr(numeric_only = True).iloc[0].mean()

"""
)
st.write("""
Il dato ottenuto **non è particolarmente significativo per lo studio della stagionalità**: mette in mostra infatti come i prezzi si muovino coerentemente durante il mese e non si concentra su quanto i ritorni mensili siano effettivamente simili nel corso degli anni.
Per fare ciò si calcola, mese per mese, la **deviazione standard** del ritorno mensile nei diversi anni per mostrare quanto tali rendimenti si discostino, annata per annata, dalla media su 10 anni del mese in considerazione.

         Questo è risultato è inserito nel medesimo dataframe nella colonna **"Dispersione"**.
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
Per visualizzare il lavoro si è cercato di condensare in **un'unica immagine** il maggior numero dei dati ottenuti precedentemente.

Il grafico infatti riporta gli andamenti dei ritorni giornalieri annata per annata calcolati in **ritorni_df**, si noti che in questo caso lo **spessore varia** (**è direttamente proporzionale alla correlazione** tra l’anno in questione e la media tra tutti gli 

Viene anche visualizzata la **media arimetica** dell’andamento dei rendimenti nei i 10 anni (in nero e con maggiore spessore).

L’istogramma infine cerca di rappresentare quanto il titolo in esame abbia un **comportamento stagionale mese per mese** partendo dalla variazione standard in correlazioni_df (4) (**maggiore è la deviazione standard in un mese e minore sarà l’altezza dell’istogramma** dal momento che maggiore dispersione nei rendimenti mensili significa minor allineamento dei ritorni verso un valore simile).
"""
)
st.pyplot(fig)
st.write(""" 
**Trattandosi di un titolo poco volatile**, il grafico della media riporta piccole variazioni ed è poco leggibile, per visualizzare meglio la stagionalità dello strumento viene quindi proposto **il grafico in cui compare esclusivamente la media**:
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



#-------------------------------
st.divider()
st.header(":red[CONFRONTO TRA TITOLI]")
st.write("Come menzionato prima, lo stesso procedimento è iterato per **cinque titoli** diversi per vederne le differenze e i diversi pattern stagionali")
lista_titoli = [["EURUSD=X", "EUR/USD"],[ "ZC=F", "Corn Futures"],["^VIX", "Volatility index"],["NQ=F", "Nasdaq 100"],["MSFT", "Microsoft Co."] ]
testo_eur = ""
testo_corn = """La stagionalità di questa materia prima è dettata dalle stagioni di semina e raccolta. Durante il primo periodo (che per il mais si colloca nella prima metà dell'anno) l'offerta è ridotta e il mais presente sul mercato proviene solitamente dalle produzioni dell'anno passato e il prezzo riflette questo squilibrio tra domanda e offerta.
Durante i mesi finali dell'anno la materia prima diventa molto più disponibile e il prezzo subisce un brusco calo nei mesi centrali.
Per approfondire la stagionalità delle materie prime agricole si fa rimento a questo articolo:
"""
testo_vix = """La stagionalità del VIX negli ultimi anni è stata fortemente influenzata dal picco avvenuto nel marzo 2020 in seguito al crollo finanziario causato dalla pandemia.
Escludendo quest'anno dall'analisi risulta (5):
"""
testo_nq = """
Il nasdaq 100, composto dalle big tech americane e spinto da titoli growth, presenta un forte trend rialzista persistente durante tutti gli anni.
L'indice è fortemente influenzato dall'esito delle trimestrali pubblicate dalle aziende che ne fanno parte, motivo per cui nel grafico sono evidenziati i periodi in cui vengono pubblicati i bilanci.
"""
testo_msft = "Trattandosi di una big tech e così come è stato fatto per il nasdaq100, nel grafico sono evidenziati i periodi in cui Microsoft pubblica i bilanci trimestrali"
testi_titoli = [testo_eur, testo_corn, testo_vix, testo_nq, testo_msft]


start = dt.datetime(2010,10,1)
end = dt.datetime(2023,12,31)
period = 12

for titolo in lista_titoli:

  stock = titolo[0]

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
  fig.suptitle(stock+ " SEASONALITY")
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

  if titolo[0] == "NQ=F" or titolo[0] == "MSFT":
    plt.axvline(x = "20-January", ymin = 0.1, ymax= 0.9, linewidth=3, linestyle = "dashed")
    plt.axvline(x = "20-April", ymin = 0.1, ymax= 0.9, linewidth=3, linestyle = "dashed")
    plt.axvline(x = "20-July", ymin = 0.1, ymax= 0.9, linewidth=3, linestyle = "dashed")
    plt.axvline(x = "20-October", ymin = 0.1, ymax= 0.9, linewidth=3, linestyle = "dashed")

  if titolo[0] != "EURUSD=X":
    st.divider()
  st.subheader(titolo[1])
  


  st.pyplot(fig)
  fig2 = plt.figure(figsize=(10, 4), facecolor='white',
                 layout='constrained')
  fig2.suptitle(stock + " Media")
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
  st.markdown(testi_titoli[lista_titoli.index(titolo)])
  if titolo[0] == "ZC=F":
    st.page_link("https://www.cmegroup.com/education/courses/introduction-to-agriculture/grains-oilseeds/understanding-seasonality-in-grains.html", label= ":blue[Corn Seasonality]")


  #-------------------------
  if titolo[0] == "^VIX":
    fig3 = plt.figure(figsize=(10, 6), facecolor='white',
                  layout='constrained')
    fig3.suptitle(stock+ " SEASONALITY (NO 2020)")
    ax3 = fig3.add_subplot()
    plt.ylabel("% Return")
    plt.rcParams["font.family"] = 'sans serif'
    plt.rcParams["font.size"] = 15


    ritorni_df["media"] = ritorni_df[elenco_anni].mean(axis = 1)

    for anno in elenco_anni:
      print(type(anno))
      if anno != 2020:
        colore = elenco_colori[elenco_anni.tolist().index(anno)]
        for mese in elenco_mesi:
          spessore =  (ritorni_df[[anno, "media"]].corr().iloc[0,1] + 1) / 2
          #trasparenza = (ritorni_df.loc[ritorni_df.index.str.slice(3) == mese][[anno, "media"]].corr().iloc[0,1] + 1) / 2
          trasparenza = 0.9


          ax3.plot(ritorni_df.loc[ritorni_df.index.str.slice(3) == mese].index,
                  ritorni_df.loc[ritorni_df.index.str.slice(3) == mese][anno]*100,
                  linewidth = 4*(spessore), alpha = trasparenza, markersize = 1, color = colore)

        ampiezza_stackplot = ritorni_df.loc[ritorni_df.index.str.slice(3) == mese].max().max()*100

        ax3.stackplot(ritorni_df.index, (1.2 - correlazione_df["Dispersione"])*ampiezza_stackplot, alpha = 0.6, color = "gray", labels = ["Dispersione"])
        ax3.plot(ritorni_df.index, ritorni_df["media"]*100, linewidth = 5, color = "black", label = "Media")

      #ax3.legend(loc = "upper center")

      positions = [0,31,59,90,120, 151, 182, 213, 243, 274, 305, 335]
      labels = ['Jan', "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Ott", "Nov", "Dec"]
      ax3.xaxis.set_major_locator(ticker.FixedLocator(positions))
      ax3.xaxis.set_major_formatter(ticker.FixedFormatter(labels))
    st.pyplot(fig3)



st.divider()
st.subheader("Note")
st.write("""
(1): Il dataframe contiene tutti i 366 giorni di un anno bisestile, i dati mancanti per i giorni di chiusura sono ottenuti a partire dall'ultimo prezzo disponibile.

(2): I primi giorni dell'anno hanno quasi sempre ritorno nullo dato il ritorno è calcolato come variazione dal giorno iniziale dell'anno in questione.

(3): E' stato utilizzato il metodo pearson.
                      
(4): La variazione standard riportata nel dataframe è normalizzata entro il valore massimo e nel grafico è scalata affinchè compaia leggibile.
         
(5): Il grafico è visualizzato con un asse delle ordinate diverso.
         """)