"""
ORM Model — tutte le operazioni dati via PonyORM + SQLite
"""

import os
import pandas as pd
from datetime import datetime, date
from pony.orm import (Database, LongStr, Required, Optional, Set, PrimaryKey, db_session, select, commit, desc)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

diabete_db = Database()

class Utente(diabete_db.Entity):
    _table_ = 'utente'
    email = PrimaryKey(str)
    nome = Required(str)
    cognome = Required(str)
    password = Required(str)
    ruolo = Required(str) # 'paziente', 'medico', 'segretario'
    
    paziente = Optional('Paziente')
    medico = Optional('Medico')
    segretario = Optional('Segretario')
    
    alert = Set('Alert')

    
class Segretario(diabete_db.Entity):#serve solo per inserimento nuovi pazienti
    _table_ = 'segretario'
    utente = Required(Utente, unique=True) #specializzazione


class Medico(diabete_db.Entity):
    _table_ = 'medico'
    matricola = Required(str, unique=True)
    utente = Required(Utente, unique=True) #specializzazione
    
    pazienti = Set('Paziente')
    terapie = Set('Terapia')
    

class Paziente(diabete_db.Entity):
    _table_ = 'paziente'
    utente = Required(Utente, unique=True) #specializzazione
    medico_riferimento = Required(Medico)
    codice_fiscale = Required(str, unique=True)
    
    fumatore = Required(bool, default=False)
    ex_fumatore = Required(bool, default=False)
    obesita = Required(bool, default=False)
    problemi_alcol = Required(bool, default=False)
    problemi_stupefacenti = Required(bool, default=False)
    comorbidita = Optional(LongStr)
    
    misurazioni = Set('Misurazione')
    assunzioni = Set('Assunzione')
    segnalazioni = Set('Segnalazione')
    terapie = Set('Terapia')
    
    
class Farmaco(diabete_db.Entity):
    id = PrimaryKey(int, auto=True)
    nome = Required(str)

    terapie = Set('Terapia')
    assunzioni = Set('Assunzione')
    
class Terapia(diabete_db.Entity):
    id = PrimaryKey(int, auto=True)
    paziente = Required(Paziente)
    medico = Required(Medico)
    farmaco = Required(Farmaco)
    data_inizio = Required(date)
    data_fine = Optional(date)
    assunzioni_giornaliere = Required(int)
    quantita_per_assunzione = Required(float)
    unita_misura = Required(str)
    indicazioni = Optional(LongStr)
    attiva = Required(bool, default=True)
    data_ultimo_alert = Optional(datetime)
    
    assunzioni = Set('Assunzione')
    
class Misurazione(diabete_db.Entity):
    id = PrimaryKey(int, auto=True)
    paziente = Required(Paziente)
    timestamp = Required(datetime, default=datetime)
    valore_mg_dl = Required(float)
    momento = Required(str)
    
class Assunzione(diabete_db.Entity):
    id = PrimaryKey(int, auto=True)
    paziente = Required(Paziente)
    terapia = Required(Terapia)
    farmaco = Required(Farmaco)
    timestamp = Required(datetime, default=datetime)
    quantita_assunta = Required(float)
    conforme = Required(bool, default=True)
    
class Segnalazione(diabete_db.Entity):
    id = PrimaryKey(int, auto=True)
    paziente = Required(Paziente)
    tipo = Required(str)
    descrizione = Required(LongStr)
    data_inizio = Required(date)
    data_fine = Optional(date)
    
class Alert(diabete_db.Entity):
    id = PrimaryKey(int, auto=True)
    utente = Required(Utente)
    
    informazioni = Required(LongStr)
    timestamp = Required(datetime, default=datetime.utcnow)
    letto = Required(bool, default=False)
    
    
#---Model class---

class OrmModel:
    
    def __init__(self):
        diabete_db.bind(provider='sqlite', filename=os.path.join(BASE_DIR, 'diabete.sqlite'),  create_db=True)
        diabete_db.generate_mapping(create_tables=True)
        
        self._seed_users()

    
    @db_session
    def _seed_users(self):
        if Utente.select().count() > 0:#se è già stato minimamente popolato...
            return
        #inserisci un istanza utente e assegnalo a Segretario
        u_segr = Utente(email='segretario@telemedicina.it', nome='Carlo', cognome='Mazzini', password='Admin123', ruolo='segretario')
        Segretario(utente=u_segr)
        commit()
    
    # ---- autenticazione -----------------------------------------------------

    #serve quando sono in fase di login - verifica credenziali
    @db_session
    def authenticate(self, email, password):
        u = Utente.get(email=email, password=password)
        if u:
            return {'email': u.email, 'ruolo': u.ruolo, 'display_name': f"{u.nome} {u.cognome}"}
        return None

    #riceve solo l'email — serve per recuperare i dati di un utente già autenticato
    @db_session
    def get_user(self, email):
        u = Utente.get(email=email)
        if u:
            return {'email': u.email, 'ruolo': u.ruolo, 'display_name': f"{u.nome} {u.cognome}"}
        return None
    
    # ---- operazioni segretario ------------------------------------------------
    @db_session
    def crea_medico(self, nome, cognome, email, matricola, password):
        u = Utente(
            nome=nome,
            cognome=cognome,
            email=email,
            password=password,
            ruolo='medico'
        )
        Medico(utente=u, matricola=matricola.upper())
        commit()
        
    @db_session
    def crea_paziente(self, nome, cognome, email, cf, medico_id, password,
                    fumatore=False, ex_fumatore=False, obesita=False,
                    problemi_alcol=False, problemi_stupefacenti=False):
        u = Utente(
            nome=nome,
            cognome=cognome,
            email=email,
            password=password,
            ruolo='paziente'
        )
        medico = Medico.get(utente=Utente.get(email=medico_id))
        Paziente(
            utente=u,
            medico_riferimento=medico,
            codice_fiscale=cf.upper(),
            fumatore=fumatore,
            ex_fumatore=ex_fumatore,
            obesita=obesita,
            problemi_alcol=problemi_alcol,
            problemi_stupefacenti=problemi_stupefacenti,
        )
        commit()

    @db_session
    def get_medici(self):
        return [{'id': m.utente.email, 'nome': f"{m.utente.nome} {m.utente.cognome}"}
                for m in Medico.select()]
    #-----------------------------------------------------------------------------
    
    
    
    # ---- operazioni medico -----------------------------------------------------
    
    
    
    #-----------------------------------------------------------------------------
    
    
    
    # ---- operazioni Paziente ---------------------------------------------------

    def get_my_doctor(self, patient_email):
        p = Paziente.get(utente=patient_email)
        if p:
            m = p.medico_riferimento
            return {'email': m.utente.email, 'nome': f"{m.utente.nome} {m.utente.cognome}"}
        return None
    
    

model = OrmModel()