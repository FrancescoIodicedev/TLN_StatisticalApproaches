# TLN1920

## Consegna

Date 12 definizioni diverse per un singolo concetto inferirlo automaticamente.

1. Caricamento dei dati content-to-form 
2. Preprocessing (a vostra scelta)
3. Utilizzo di WordNet come sense inventory, per inferire il concetto descritto dalle
diverse definizioni
4. Definire ed implementare un algoritmo (efficace ma anche efficiente) di esplorazione
dei sensi di WordNet, usando concetti di similarità (tra gloss e definizioni, esempi d’uso,
rappresentazioni vettoriali, etc.)
 - Suggerimento A: sfruttare principi del genus-differentia
 - Suggerimento B: sfruttare tassonomia WordNet nell’esplorazione
 - Suggerimento C: pensare a meccanismi di backtracking

## Implementazione algoritmo

**Input** : Lista definizioni per il termine **w**

**Output**: **w** o un concetto semanticamente legato a w

1. Estrazione termini rilevanti e soggetti/aggettivi dalle definizioni
2. Estrazione dominio e contesto
    - **dominio**: possibili iperonimi usati per descrivere w con relativi aggettivi
    - **contesto**: termini rilevanti presenti nelle definizioni
3. Calcolo delle frequenze dei domini e contesti in modo da operare unicamente su quelli più frequenti
4. Ricerca in Wordnet su ogni termine presente nel **dominio**,dato un termine nel dominio si guardano tutti i sensi associati al synsets di wordnet e per ogni senso si valutano tutti gli iponimi
5. Viene calcolata la similarità tra la definizione del synset e la stringa ottenuta dalla concatenazione di tutti i termini nel **contesto**.
 Il synset con il valore massimo di similarità viene ritornato.

#### 1. Estrazione termini rilevanti 
Da ogni definizione vengono estratti:
- **Soggetti**: effettuando Pos Tagging + Parsing su ogni definizione
- **Termini rilevanti**: tutti i termini presenti nelle definizioni eliminando eventuali stopword e simboli di punteggiatura.

#### 2. Estrazione dominio e contesto 
Vengono costruite 2 liste:
 - `contex` = i termini rilevanti della definizione 
 - `domain` = soggetto e/o aggettivi relativi alla definizione corrente unito a tutti i domini (estratti da wordnet) legati ai termini presenti nell'insieme delle parole rilevanti.

I punti 1 e 2 vengono eseguiti su ogni definizione per il termine w. 
Gli insiemi `contex` e `domain` sono cumulativi, ad ogni iterazione su una definizione diversa vengono estesi con i nuovi termini rilevanti e i nuovi domini ottenuti dalla definizione corrente.

#### 3. Calcolo delle frequenze
 
Date le liste `contex` e `domain` vengono calcolati 2 insiemi:
 - `context` = i contesti più frequenti sulla frequenza dei termini in `contex` 
 - `candidate_genus` = i domini più frequenti sulla frequenza dei termini in `domain` 
 
Vengono mantenuti solo i domini e contesti più frequenti, in base ai seguenti parametri:
 - `max_term_in_context` 
 - `max_genus` 

#### 4 Ricerca in Wordnet

Viene costruita la stringa:
 - `s_context` = come la concatenazione dei lemma di ogni parola nell'insieme `context`. 
 
La ricerca è di tipo top-down, l'algoritmo itera su ogni termine **w** presente nell'insieme `candidate_genus`, si valutano tutti i sensi associati ad w e tutti gli iponimi di ogni senso.

#### 5 Similarità

La valutazione di ogni senso avviene calcolando la similarità tra la definizione del senso e la stringa `s_context`, la misura di similarità adottata utilizza la cosin similarity tra vettori embedding relativi ai termini.
 - Lo score associato a ciascun synset è il valore della similarità.

Durante la ricerca vengono aggiornati 2 valori:
- best_score = punteggio da 0 a 1 
- best_synset = synset relativo allo score

Dopo avere iterato su ogni termine nell'insieme `candidate_genus` viene ritornato il synset con lo score maggiore.

## Risultati
	
Target term | Obtained term | Definition term |
------------ | :------------: | :-------------:
| | 
politics | Synset('morality.n.01')  | concern with the distinction between good and evil or right and wrong; right or good conduct
patience | Synset('unresponsiveness.n.01')  | the quality of being unresponsive; not reacting; as a quality of people, it is marked by a failure to respond quickly or with emotion to people or events
greed | Synset('longer.n.01')  | a person with a strong desire for something
justice | Synset('law.n.02') | legal document setting forth rules governing a particular kind of activity
food | Synset('water.n.06')  | a liquid necessary for the life of most animals and plants
screw | Synset('piezoelectricity.n.01') | electricity produced by mechanical pressure on certain crystals (notably quartz or Rochelle salt); alternatively, electrostatic stress produces a change in the linear dimensions of the crystal
vehicle | Synset('transportation.n.02')  | the act of moving something from one location to another
radiator | Synset('transportation.n.02')   | the act of moving something from one location to another
 
 
Nel file `result.txt` sono presenti informazioni aggiuntive sui risultati, quali:
 - il contesto per ogni termine
 - i vari candidati genus esplorati nella ricerca