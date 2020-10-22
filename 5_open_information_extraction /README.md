# TLN1920

## Consegna

Implementazione di un sistema di OIE

### Svolgimento

Le triple sono estratte da frasi che contengo almeno un soggetto, un verbo e un complemento oggetto.

Il sistema implementato è in grado di estrarre delle triplette della forma **(Soggetto, Verbo, Oggetto)** da un insieme di frasi.

Data in input una frase il sistema esegue:
 1. **Pos Tagging e Dependency Parsing** con l'ausiolio di **spaCy** che per ogni token allegata la rispettiva dipendenza sintattica (**dep_**)
 2. Vengono scansionate le dipendenze trovate e costruiti gli argomenti della tripletta
 
La scelta la l'algoritmo deve fare è in quale dei 3 argomenti mappare i token della frase in analisi.

## Mapping
 
Per poter fare questo è necessario categorizzare la **dep_** in modo da restringere le associazioni possibili tra **dep_** e argomento e delle triple.

I soggetti, complementi oggetti e oggetto diretto e le relazioni vengono riconosciuti in quanto la loro dipendenza sintattica ricade:
 - [nsubj, nsubjpass] per i soggetti 
 - [dobj, obj] per i complementi oggetti e oggetto diretti
 - ["ROOT", "adj", "attr", "agent", "amod"] per le relazioni
    - adj è stato inserito perchè se presente, legato al verbo apporta maggiore significativià delle triple.       
    
Le relazioni e le entità possono essere costruite usando più di una parola, infatti il Soggetto, Predicato e Oggetto da inserire nelle triple sono realizzati come concatenzioni di più parole.

Dopo aver individuato l'elemento centrale di uno degli argomenti della tripla vengono aggiunte informazioni aggiuntive, concatenando altri token successivi se la loro dipendenza sintattica appartenenza a questo insieme:
 - ["compound", "prep", "conj", "mod"] 
 
Dopo aver valutato il token `x` se appartiene ad uno dei 3 insiemi indicati sopra il suo testo viene salvato in una variabile temporale concatenando i testi dei token successivi, con il criterio sopra citato, fino a quando non si trovo un token appartenente ad un insieme diverso da quello a cui appartenga il token `x`.

##Result 

Sono state prese circa 15 frasi da wikipedia di diversa complessità, come si può vedere se la frase è semplice il sistema riesce a mappare il suo significato in una tripla, ma quando la complessità aumente le triple divetano poco consistenti o non riescono a mappare il significato della frase.

Sentence : London is the capital and largest city of England and the United Kingdom.
- **( London, be capital large, England )**

Sentence : Roma is the capital of Italy.
- **( Roma, be capital, Italy )**

Sentence : Londinium was founded by the Romans.
- **( Londinium, found by, Romans )**

Sentence : Italy is considered to be one of the world's most culturally and economically advanced countries.
- **( Italy, consider one culturally, countries )**

Sentence : The City of London, London's ancient core − an area of just 1.12 square miles (2.9 km2) and colloquially known as the Square Mile − retains boundaries that follow closely its medieval limits.
- **( City core that, ancient square retain medieval, London miles − boundaries limits )**

Sentence : The City of Westminster is also an Inner London borough holding city status.
- **( City, be hold status, Westminster )**

Sentence : Greater London is governed by the Mayor of London and the London Assembly.
- **( London, govern by, Mayor London )**

Sentence : London is located in the southeast of England.
- **( London, locate, southeast England )**

Sentence : Westminster is located in London.
- **( Westminster, locate, London )**

Sentence : The clause contains three arguments.
- **( clause, contain, arguments )**

Sentence : London is the biggest city in Britain.
- **( London, be big city, Britain )**

Sentence : London has a population of 7,172,036.
- **( London, have, population 7,172,036 )**

Sentence : Italy is a country consisting of a peninsula.
- **( Italy, be country, peninsula )**

Sentence : Italy is located in south-central Europe.
- **( Italy, locate south central, Europe )**

Sentence : The Roman Empire was among the most powerful economic, cultural, political and military forces in the world of its time.
- **( Empire, be powerful economic, forces world time )**