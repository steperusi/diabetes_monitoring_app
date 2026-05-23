"""
ORM Model — tutte le operazioni dati via PonyORM + SQLite
"""

import os
import pandas as pd
from enum import Enum
from datetime import datetime, date
from pony.orm import (Database, LongStr, Required, Optional, Set, PrimaryKey, db_session, select, commit, desc)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

diabete_db = Database()


class FarmacoEnum(str, Enum):
    METFORMINA      = "Metformina"
    INSULINA_RAPIDA = "Insulina rapida"
    INSULINA_LENTA  = "Insulina lenta"
    GLIPIZIDE       = "Glipizide"
    SITAGLIPTIN     = "Sitagliptin"
    EMPAGLIFLOZIN   = "Empagliflozin"
    ALTRO           = "Altro"


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
    messaggi_inviati = Set('Messaggio', reverse='mittente')
    messaggi_ricevuti = Set('Messaggio', reverse='destinatario')

    
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

    
class Terapia(diabete_db.Entity):
    id = PrimaryKey(int, auto=True)
    paziente = Required(Paziente)
    medico = Required(Medico)
    farmaco_nome = Required(str)
    data_inizio = Required(date)
    data_fine = Optional(date)
    assunzioni_giornaliere = Required(int)
    quantita_per_assunzione = Required(float)
    unita_misura = Required(str)
    indicazioni = Optional(LongStr)
    #attiva = Required(bool, default=True)
    #data_ultimo_alert = Optional(datetime)
    
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
    

class Messaggio(diabete_db.Entity):
    _table_ = 'messaggio'
    id = PrimaryKey(int, auto=True)
    mittente = Required(Utente, reverse='messaggi_inviati')
    destinatario = Required(Utente, reverse='messaggi_ricevuti')
    testo = Required(LongStr)
    timestamp = Required(datetime, default=datetime.now)
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
        #inserisci tre istanze utente e assegnale ciacuna a una delle tre tabelle specializzate (Segretario, Medico, Paziente)
        u_segr = Utente(email='segretario@telemedicina.it', nome='Carlo', cognome='Mazzini', password='Admin123', ruolo='segretario')
        Segretario(utente=u_segr)
        
        u_med = Utente(email='lucabianchi@medico.it', nome='Luca', cognome='Bianchi', password='LucaB123', ruolo='medico')
        Medico(utente=u_med, matricola='MED001')
        
        u_paz = Utente(email='marcoverdi@paziente.it', nome='Marco', cognome='Verdi', password='MarcoV123', ruolo='paziente')
        Paziente(utente=u_paz, medico_riferimento=Medico.get(utente=u_med), codice_fiscale='VRDMRC80A01H501A')
        
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

    @db_session #IN TEORIA NON SERVE PIù
    def get_medici(self):
        return [{'id': m.utente.email, 'nome': f"{m.utente.nome} {m.utente.cognome}"}
                for m in Medico.select()]
    #-----------------------------------------------------------------------------
    
    
    
    # ---- operazioni medico -----------------------------------------------------
    @db_session
    def crea_terapia(self, paziente_email, medico_email, farmaco_nome, data_inizio,
                    data_fine, assunzioni_giornaliere, quantita_per_assunzione,
                    unita_misura):#indicazioni d vedere se servono o le mettiamo in un secondo momento
        
        paziente = Paziente.get(utente=Utente.get(email=paziente_email))
        medico   = Medico.get(utente=Utente.get(email=medico_email))
        
        if farmaco_nome not in [f.value for f in FarmacoEnum]:
            raise ValueError(f"Farmaco '{farmaco_nome}' non valido")
        
        Terapia(
            paziente=paziente,
            medico=medico,
            farmaco_nome=farmaco_nome,
            data_inizio=data_inizio,
            data_fine=data_fine,
            assunzioni_giornaliere=assunzioni_giornaliere,
            quantita_per_assunzione=quantita_per_assunzione,
            unita_misura=unita_misura
        )
        commit()

    @db_session                
    def get_pazienti_medico(self, medico_email: str) -> list[dict]:
        u = Utente.get(email=medico_email)
        m = Medico.get(utente=u)
        if not m:
            return[]
        return[
            {
                'email': p.utente.email,
                'nome': p.utente.nome,
                'cognome': p.utente.cognome,
                'codice_fiscale': p.codice_fiscale,
                'fumatore': p.fumatore,
                'ex-fumatore': p.ex_fumatore,
                'obesita': p.obesita,
                'problemi_alcol': p.problemi_alcol,
                'problemi_stupefacenti': p.problemi_stupefacenti
            }
            for p in m.pazienti
        ]
    
    
    #-----------------------------------------------------------------------------
    
    
    
    # ---- operazioni Paziente ---------------------------------------------------

    @db_session
    def get_my_doctor(self, patient_email):
        p = Paziente.get(utente=Utente.get(email=patient_email))
        if p:
            m = p.medico_riferimento
            return {'email': m.utente.email, 'nome': f"{m.utente.nome} {m.utente.cognome}"}
        return None
    
    #------ Chat -----------------------------------------------------------------  
    @db_session
    def invia_messaggio(self, mittente_email: str, destinatario_email: str, testo: str):
        m = Utente.get(email=mittente_email)
        d = Utente.get(email=destinatario_email)
        if not m or not d:
            raise ValueError("Utente non trovato")
        Messaggio(mittente=m, destinatario=d, testo=testo)
        commit()

    @db_session
    def get_conversazione(self, email_a: str, email_b: str) -> list[dict]:
        a = Utente.get(email=email_a)
        b = Utente.get(email=email_b)
        if not a or not b:
            return []
        inviati = [m for m in a.messaggi_inviati if m.destinatario == b]
        ricevuti = [m for m in a.messaggi_ricevuti if m.mittente == b]
        messaggi = sorted(inviati + ricevuti, key=lambda m: m.timestamp)
        return[
            {
                'mittente': m.mittente.email,
                'testo': m.testo,
                'timestamp': m.timestamp.strftime('%H:%M'),
            }
            for m in messaggi
        ]

model = OrmModel()