#!C:\Python34\python.exe     
# -*- coding: utf-8 -*-
#----------------------------------------------------
# Dateiname:  admin.py
# Administration eines Redaktionssystems.
# Die Datenbank-Tabellen für User und Beiträge werden initialisiert
# (falls sie nich nicht existieren).  
# Ausserdem wird die Einrichtung neuer Benutzer ermöglicht.
#
# Dieses Skript muss so gespeichert werden, dass nur
# der Administrator Zugriffsrechte hat 
# 
# Objektorientierte Programmierung mit Python 3
# Kap. 24  
# Michael Weigend 29.1.2013
#----------------------------------------------------

import sqlite3,hashlib

class Admin(object):
  def __init__(self, db_pfad):
    verbindung = sqlite3.connect(db_pfad)
    c = verbindung.cursor()
    try:
        c.execute("SELECT * FROM person")
        c.execute("SELECT * FROM beitrag")
    except:
        # Tabellen existieren noch nicht
        c.execute("""CREATE TABLE
                       person(name VARCHAR(50),
                              fingerprint BINARY(16))
                  """)
        c.execute("""CREATE TABLE
                       beitrag(titel VARCHAR(100),
                               text VARCHAR(1000),
                               verfallsdatum FLOAT,
                               autor VARCHAR(50))
                  """)
        verbindung.commit()
    
    print('Liste der User-Namen:')
    c.execute("SELECT * FROM person")
    for zeile in c: print (zeile[0])
    print ("Neue User anlegen. (Name ist provisorisches Passwort)")
    neu = input('Neuer User (Ende mit RETURN): ')
    while neu:
      if list(c.execute("""SELECT *
                           FROM person
                           WHERE name = ?;""", (neu,))):
        print('Name existiert bereits.')
      else:
        m = hashlib.md5(neu.encode("utf-8"))
        c.execute("""INSERT INTO person
                    VALUES(?, ?);""",
                 (neu, m.digest()))
        verbindung.commit()
      neu = input('Neuer User: ') # Achtung, Einrückung!
    print("Datenbank wurde aktualisiert.")
    c.close()
    verbindung.close()

Admin('redaktion.db')

        
