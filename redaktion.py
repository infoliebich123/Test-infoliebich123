#!C:\Python34\python.exe 
#----------------------------------------------------
# Dateiname:  redaktion.py
#
# CGI-Skript, das Teil eines online-Redaktionssystems ist.
# Das CGI-Skript verarbeitet folgende Variablen,
# die vom aufrufenden Client gesendet werden:
# name, passwort, neuespass, neupass1, neupass2
# titel, text, haltbar (Anzahl der Tage)
#
# Ermöglicht wird die Änderung des Passwortes des Redakteurs
# und /oder die Edition eines Beitrages für das Online-Journal.
# 
# Objektorientierte Programmierung mit Python
# Kap. 24
# Michael Weigend 11.11.09
#----------------------------------------------------

import sqlite3, cgi, hashlib, cgitb, time, logging
cgitb.enable()
logging.basicConfig(filename="tmp.txt",
                    format="%(funcName)s: %(message)s",
                    level=logging.DEBUG,
                    filemode="w")                          #2

# Schablone fuer HTTP-Paket
# Platzhalter {}: Name, Passwort, Text, Fehler im Beitrag,
# Fehler im Passwort

# Schablone für HTTP-Paket
SEITE1 = """Content-Type: text/html\n
<html>
<head>
<title>Python-Redaktionssystem</title>
<meta http-equiv="Content-Type" content="charset=utf-8" />
</head>
<body bgcolor=#C0C0C0>
<h2>Python-Redaktionssystem</h2>
<form action="redaktion.py"
method="POST" >
<input type="hidden" name="name" value="{}">     
<input type="hidden" name="passwort" value="{}">      <b>Titel: </b><input type="Text" name="titel"
size="50" maxlength="80"><br><br>
<textarea name="text" cols="50" rows="8" >{}
</textarea><br>
<h4>Haltbarkeit</h4>
<input type="Radio" name="haltbar" value="14"
checked="checked">
 2 Wochen <br>
<input type="Radio" name="haltbar" value="30">
 1 Monat <br>
<input type="Radio" name="haltbar" value="90">
 3 Monate <br>
<input type="Radio" name="haltbar" value="180">
 6 Monate <br>
<h4> Passwortverwaltung</h4>
 <input type="Checkbox" name="neuespass" value="1">
Passwort &auml;ndern<br>
<input type="Password" name="neupass1" > Neues Passwort<br>
<input type="Password" name="neupass2" > Passwort wiederholen<br>
<input type="Submit" value="Absenden">
</form>
<i>{}<br>{}<br></i>    
</body></html>"""

# HTTP-Paket mit Fehlermeldung bei falschem Login
SEITE2 = """Content-Type: text/html\n
<html>
<head><title>Rython-Redaktionssystem</title>
<meta http-equiv="Content-Type" content="charset=utf-8" />
</head>
<body bgcolor=#C0C0C0>
<h2> Python-Redaktionssystem</h2>
<form action="redaktion.py" 
method="POST">
Name: <input type="Text" name="name" >&nbsp;
Passwort: <input type="Password"
name="passwort"><br><br>
<input type="Submit" value="Login">
</form>
<b> Login gescheitert! &Uuml;berpr&uuml;fen Sie Name und
Passwort.<b>
</body></html>"""

# Schablone für Webseite (Publikation)
# Platzhalter {}: Zeit und Beiträge
WEBSEITE = """<html>
<head><title>Python-News</title></head>
<body>
<h1>Python-News</h1>
Letzte &Auml;nderung: {}
{} 
</body></html>"""

# Schablone für Beitrag
# Platzhalter {}: Titel, Autor und Text
BEITRAG = """<h3>{}</h3>
<h4>von {}</h4>
<p>{}</p>"""

HTML = {ord("ä"): "&auml;", ord("ö"): "&ouml;",
        ord("ü"): "&uuml;", ord("Ä"): "&Auml;",
        ord("Ö"): "&Ouml;", ord("Ü"): "&Uuml;",
        ord("ß"): "&szlig;"}                         #2
class Person(object):                                #3
  def __init__(self, form, db):
    self.name = form.getvalue("name")
    self.pw = form.getvalue("passwort")
    self.db = db

  def id_ok(self):                                   #4
    logging.debug("Name: {}, Passwort:{}".format(
                                     self.name,self.pw))
    try:
        logging.debug(self.db)
        verbindung = sqlite3.connect(self.db)
        c = verbindung.cursor()
        c.execute("""SELECT *
                     FROM person
                     WHERE name = ?;""", (self.name,))
        logging.debug("Mit Datenbank verbunden.")
        fingerprint_db = list(c)[0][1]               #5
        pw_bytes = self.pw.encode("utf-8")           #6 
        fingerprint_pw = hashlib.md5(pw_bytes).digest()
        c.close()
        verbindung.close()
        return fingerprint_db == fingerprint_pw      #7

    except:
        return False

  def aktualisiere_pw(self, form):                   #8
    neupw1 = form.getvalue("neupass1", "")
    neupw2 = form.getvalue("neupass2", "")
    if neupw1 == neupw2: 
        self.pw = neupw1
        verbindung = sqlite3.connect(self.db)
        c = verbindung.cursor()
        c.execute("""UPDATE person
                     SET fingerprint = ?
                     WHERE name = ?;
                 """,
                (hashlib.md5(self.pw.encode("utf-8")).digest(),
                 self.name))
        verbindung.commit()
        c.close()
        verbindung.close()
        return "Passwort ge&auml;ndert."
    else:
        return "Fehler! Passw&ouml;rter nicht gleich!"
    
class Beitrag(object):                               #9
    def __init__(self, form, autor, db):
      self.text = self.titel = ""
      self.db = db
      self.autor = autor
      if "titel" in form.keys():
        self.text = form.getvalue("text")
        self.titel = form.getvalue("titel")
        sekunden = float(form.getvalue("haltbar")) *24*3600
        self.verfallsdatum = sekunden + time.time()
        logging.debug("Verfallsdatum:" + str(self.verfallsdatum))

    def publiziere(self):
        if self.titel:                               #10
          logging.debug("Titel: " + self.titel)
          logging.debug("Text: " + self.text)
          verbindung = sqlite3.connect(self.db)
          c = verbindung.cursor()
          c.execute("""SELECT *
                       FROM beitrag
                       WHERE titel = ?;""",
                     (self.titel,))
          if not list(c):                           #11
            c.execute("""INSERT INTO beitrag
                         VALUES(?, ?, ?, ?);""",
                      (self.titel, self.text,
                       self.verfallsdatum,
                       self.autor.name))
            logging.debug("Gespeichert: " + self.titel)
            verbindung.commit()
            self.text = ""
            self.titel = ""
            meldung = "Beitrag wurde gespeichert."
          else:
            meldung = "Titel existiert bereits."
          c.close()
          verbindung.close()
        else: meldung = ""
        return meldung

    def aktualisiere_news(self, news_pfad):
        # HTML-Datei mit Journal aktualisieren
        verbindung = sqlite3.connect(self.db)
        c = verbindung.cursor()
        beitraege = list(
          c.execute("""select * FROM beitrag;"""))  
        pubtext ="" 
        for (titel, text,  verfallsdatum, 
             autor) in beitraege:                   #12
          if float(verfallsdatum) > time.time():    
            pubtext += BEITRAG.format(
                         titel.translate(HTML), 
                         autor.translate(HTML),
                         text.translate(HTML))
          else:                                     #13
            c.execute("""DELETE FROM beitrag
                         WHERE titel = ?;""", (titel,))
        logging.debug("Veröffentlichter Text:"+pubtext)
        verbindung.commit()
        c.close()
        verbindung.close()
        # Speichern
        f = open(news_pfad, "w")
        f.write(WEBSEITE.format(time.asctime(), pubtext))
        f.close()

DB = "redaktion.db"
NEWS_PFAD = "news.html"
form = cgi.FieldStorage()
redakteur = Person(form, DB)                        #14
beitrag = Beitrag(form, redakteur, DB)                         
beitragfehler = ""                                  #15
pwfehler = ""
if redakteur.id_ok():                               #16
  beitragfehler = beitrag.publiziere()
  beitrag.aktualisiere_news(NEWS_PFAD)
  if "neuespass" in form.keys():
    pwfehler = redakteur.aktualisiere_pw(form)
  print(SEITE1.format(redakteur.name,
                      redakteur.pw,
                      beitrag.text,
                      beitragfehler,
                      pwfehler))
else: print(SEITE2)

















                    
