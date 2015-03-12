#----------------------------------------------------
# Dateiname:  adminloesung2.py
# Administration eines Redaktionssystems.
#
# Funktionen:
# Datenbank-Dateien für User und Beiträge werden initialisiert
# Einrichtung eines neuen Benutzers
# Entfernen eines Benutzers aus der Datenbank
#
# Hinweis: Dieses Skript muss so gespeichert werden, dass nur
# der Administrator Zugriffsrechte hat 
# 
# Objektorientierte Programmierung mit Python
# Kap. 24  Lösung 2
# Michael Weigend 11.11.2009
#----------------------------------------------------

import sqlite3,hashlib

class Admin(object):
  def __init__(self, db_pfad):
    self.verbindung = sqlite3.connect(db_pfad)
    self.c = self.verbindung.cursor()
    try:
        self.c.execute("SELECT * FROM person")
        self.c.execute("SELECT * FROM beitrag")
    except:
        # Tabellen existieren noch nicht
        self.c.execute("""CREATE TABLE
                          person(name VARCHAR(50),
                          fingerprint BINARY(16))
                       """)
        self.c.execute("""CREATE TABLE
                          beitrag(titel VARCHAR(100),
                          text VARCHAR(1000),
                          verfallsdatum FLOAT,
                          autor VARCHAR(50))
                       """)
        self.verbindung.commit()
    self.__runMenue()

  def __runMenue(self):
    wahl = " "
    while wahl not in "eE":
      self.c.execute("SELECT * FROM person")
      print ("Liste der Redakteure:")
      for zeile in self.c: print (zeile[0])   
      print ("-----------------------------")
      print ("(n)eu    (l)öschen    (E)nde")
      wahl = input ("Wahl: ")
      if wahl in "nN": self.__neuerRedakteur()
      elif wahl in "lL": self.__redakteurLoeschen()
    print ("Auf Wiedersehen...")
    self.c.close()
    self.verbindung.close()

  def __neuerRedakteur(self):
    neu = input("Neuer Redakteur: ")
    if list(self.c.execute("""SELECT *
                              FROM person
                              WHERE name = ?;""", (neu,))):
        print('Name existiert bereits.')
    else:
        m = hashlib.md5(neu.encode("utf-8"))
        self.c.execute("""INSERT INTO person
                          VALUES(?, ?);""",
                      (neu, m.digest()))
        self.verbindung.commit()

  def __redakteurLoeschen(self):
    name = input('Name: ')
    try:
      self.c.execute("""DELETE FROM person
                        WHERE name = ?;""", (name,))
      print(name, "wurde aus der Datenbank entfernt.")
    except:
      print(name, "existiert nicht in der Datenbank.")
    self.verbindung.commit()
            
Admin('redaktion.db')
        
