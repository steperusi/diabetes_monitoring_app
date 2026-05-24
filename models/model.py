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
    
class Misurazione(diabete_db.Entity):
    id = PrimaryKey(int, auto=True)
    paziente = Required(Paziente)
    date = Required(date)
    momento = Required(str) #pre_colazione, post_colazione, pre_pranzo, post_pranzo, pre_cena, post_cena
    valore_mg_dl = Required(float)
    
class Assunzione(diabete_db.Entity):
    id = PrimaryKey(int, auto=True)
    paziente = Required(Paziente)
    timestamp = Required(datetime, default=datetime)
    farmaco = Required(Farmaco)
    quantita_assunta = Required(float)
    
class Segnalazione(diabete_db.Entity):
    id = PrimaryKey(int, auto=True)
    paziente = Required(Paziente)
    data_ora = Required(datetime)
    titolo = Required(str)
    descrizione = Required(LongStr)
    
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
        medico = Medico[medico_id]
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
        return [{'id': m.email, 'nome': f"{m.utente.nome} {m.utente.cognome}"}
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
    
    # ---- operazioni Segnalazioni -----------------------------------------------
    @db_session
    def create_segnalazione(self, patient_email, title, description):
        p = Paziente.get(utente=patient_email)
        if not p:
            return False
        Segnalazione(
            paziente=p,
            titolo=title,
            descrizione=description,
            data_ora=datetime.now()
        )
        commit()
        return True
    
    @db_session
    def get_segnalazioni(self, patient_email):
        p = Paziente.get(utente=patient_email)
        if not p:
            return []
        return [{'id': s.id, 'titolo': s.titolo, 'descrizione': s.descrizione, 'data_ora': str(s.data_ora)}
                for s in sorted(p.segnalazioni, key=lambda x: x.data_ora, reverse=True)]

    # ---- operazioni Misurazioni ------------------------------------------------
    @db_session
    def create_misurazione(self, patient_email, measurement_date, momento, valore_mg_dl):
        p = Paziente.get(utente=patient_email)
        if not p:
            return False
        m = Misurazione.get(paziente=p, date=measurement_date, momento=momento)
        if m:
            m.valore_mg_dl = float(valore_mg_dl)
        else:
            Misurazione(
                paziente=p,
                date=measurement_date,
                momento=momento,
                valore_mg_dl=float(valore_mg_dl)
            )
            commit()
            return True
    
    @db_session
    def get_misurazione(self, patient_email, data_misurazione, momento_misurazione):
        p = Paziente.get(utente=patient_email)
        if not p:
            return None
        m = Misurazione.get(paziente=p, date=data_misurazione, momento=momento_misurazione)
        if m:
            return {'id': m.id, 'date': str(m.date), 'momento': m.momento, 'valore_mg_dl': m.valore_mg_dl}
        return None

    # ---- operazioni Assunzioni -------------------------------------------------
    @db_session
    def create_assunzione(self, patient_email, data_assunzione, ora_assunzione, minuto_assunzione, nome_farmaco, quantita_assunta):
        p = Paziente.get(utente=patient_email)
        if not p or not nome_farmaco:
            return False
        # Converte la stringa a date object se necessario (dalla date picker)
        if isinstance(data_assunzione, str):
            data_assunzione = date.fromisoformat(data_assunzione)
            
        # Crea o recupera il farmaco per nome
        farmaco = Farmaco.get(nome=nome_farmaco)
        if not farmaco:
            farmaco = Farmaco(nome=nome_farmaco)
            
        # Crea l'assunzione
        Assunzione(
            paziente=p,
            timestamp=datetime(data_assunzione.year, data_assunzione.month, data_assunzione.day, ora_assunzione, minuto_assunzione),
            farmaco=farmaco,
            quantita_assunta=float(quantita_assunta)
        )
        commit()
        return True
    
    @db_session
    def get_assunzioni_by_date(self, patient_email, data_assunzione):
        p = Paziente.get(utente=patient_email)
        if not p:
            return []
        # Converte la stringa a date object se necessario (dalla date picker)
        if isinstance(data_assunzione, str):
            data_assunzione = date.fromisoformat(data_assunzione)

        assunzioni = [a for a in p.assunzioni if a.timestamp.date() == data_assunzione]
        assunzioni_sorted = sorted(assunzioni, key=lambda x: x.timestamp, reverse=True)
        
        return [{'id': a.id,
                 'timestamp_hour': a.timestamp.hour,
                 'timestamp_minute': a.timestamp.minute,
                 'farmaco_nome': a.farmaco.nome,
                 'quantita_assunta': a.quantita_assunta}
                 for a in assunzioni_sorted]


model = OrmModel()