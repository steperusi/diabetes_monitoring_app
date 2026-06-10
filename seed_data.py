"""
seed_data.py — Script di popolamento del database con dati di test realistici.

Esegui dalla root del progetto:
    python seed_data.py

Il database deve già esistere (app.py lo crea al primo avvio).
Questo script aggiunge dati sopra quelli già presenti senza cancellare nulla.
Se vuoi ripartire da zero, elimina diabete.sqlite prima di eseguirlo.
"""

import os
import sys
import random
from datetime import date, datetime, timedelta
from pony.orm import db_session, commit
from models.model import model

# ── aggiunge la root al path in modo da trovare i moduli del progetto ────────
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from models.model import (
    diabete_db, Utente, Segretario, Medico, Paziente,
    Farmaco, Terapia, Assunzioni_terapia,
    Misurazione, Assunzione, Segnalazione, Alert, Messaggio,
)

# ---------------------------------------------------------------------------
# Costanti temporali
# ---------------------------------------------------------------------------
TODAY      = date.today()
MONTH_AGO  = TODAY - timedelta(days=30)
NOW        = datetime.now()

random.seed(67)


# ---------------------------------------------------------------------------
# Dati statici
# ---------------------------------------------------------------------------


# Chat simulate tra pazienti e medici


# ---------------------------------------------------------------------------
# Funzioni helper
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Seed principale
# ---------------------------------------------------------------------------

@db_session
def seed():
    print("=" * 60)
    print(" SEED — Diabetes Control Center")
    print("=" * 60)

    # ── 1. Segretari ─────────────────────────────────────────────
    print("\n[1/8] Segretari...")

    SEGRETARI = [
        dict(email='segretario@telemedicina.it',  nome='Carlo',    cognome='Mazzini',    password='Admin123'),
        dict(email='segretaria2@telemedicina.it', nome='Federica', cognome='Lombardi',   password='Fede456'),
    ]

    for s in SEGRETARI:
        if Utente.get(email=s['email']):
            print(f"      SKIP  {s['email']} (esiste già)")
            continue
        u = Utente(email=s['email'], nome=s['nome'], cognome=s['cognome'],
                   password=s['password'], ruolo='segretario')
        Segretario(utente=u)
        print(f"      OK    {s['email']}")
    commit()

    # ── 2. Medici ────────────────────────────────────────────────
    print("\n[2/8] Medici...")
    MEDICI = [
        dict(email='lucabianchi@medico.it',   nome='Luca',    cognome='Bianchi',   password='LucaB123',   matricola='MED001'),
        dict(email='annafontana@medico.it',   nome='Anna',    cognome='Fontana',   password='AnnaF456',   matricola='MED002'),
    ]
    
    for m in MEDICI:
        if Utente.get(email=m['email']):
            print(f"      SKIP  {m['email']} (esiste già)")
        else:
            model.crea_medico(email=m['email'], nome=m['nome'], cognome=m['cognome'], matricola=m['matricola'], password=m['password'])


    # ── 3. Pazienti ──────────────────────────────────────────────
    print("\n[3/8] Pazienti...")

    PAZIENTI = [
        dict(
            email='marcoverdi@paziente.it',   nome='Marco',    cognome='Verdi',
            password='MarcoV123',  cf='VRDMRC80A01H501A',
            medico_email='lucabianchi@medico.it',
            fumatore=False, ex_fumatore=True,  obesita=False, problemi_alcol=False, problemi_stupefacenti=False,
            comorbidita='Ipertensione lieve, dislipidemia',
        ),
        dict(
            email='giuliarossi@paziente.it',  nome='Giulia',   cognome='Rossi',
            password='GiulR789',   cf='RSSGLL85M41F205Z',
            medico_email='lucabianchi@medico.it',
            fumatore=True,  ex_fumatore=False, obesita=True,  problemi_alcol=False, problemi_stupefacenti=False,
            comorbidita='Neuropatia periferica',
        ),
        dict(
            email='robertoneri@paziente.it',  nome='Roberto',  cognome='Neri',
            password='RobeN321',   cf='NRERBT70C15L219X',
            medico_email='annafontana@medico.it',
            fumatore=False, ex_fumatore=False, obesita=False, problemi_alcol=True,  problemi_stupefacenti=False,
            comorbidita='Retinopatia diabetica iniziale',
        ),
        dict(
            email='sofiamarini@paziente.it',  nome='Sofia',    cognome='Marini',
            password='SofM654',    cf='MRNSFO92P58G224K',
            medico_email='annafontana@medico.it',
            fumatore=False, ex_fumatore=False, obesita=True,  problemi_alcol=False, problemi_stupefacenti=False,
            comorbidita='',
        ),
        dict(
            email='davideesposito@paziente.it', nome='Davide', cognome='Esposito',
            password='DavE987',    cf='SPSDVD88S10F839P',
            medico_email='lucabianchi@medico.it',
            fumatore=True,  ex_fumatore=False, obesita=False, problemi_alcol=False, problemi_stupefacenti=True,
            comorbidita='Nefropatia stadio 2',
        ),
    ]

    segr_utente = Utente.get(email=SEGRETARI[0]['email'])
    for p in PAZIENTI:
        if Utente.get(email=p['email']):
            print(f"      SKIP  {p['email']} (esiste già)")
        else:
            model.crea_paziente(
            nome=p['nome'],
            cognome=p['cognome'],
            email=p['email'],
            cf=p['cf'],
            medico_id=p['medico_email'],
            password=p['password'],
            fumatore=p['fumatore'],
            ex_fumatore=p['ex_fumatore'],
            obesita=p['obesita'],
            problemi_alcol=p['problemi_alcol'],
            problemi_stupefacenti=p['problemi_stupefacenti']
        )
        print(f"      OK    {p['email']}")
    commit()

    # ── 4. Terapie ───────────────────────────────────────────────
    print("\n[4/8] Terapie...")

    TERAPIE = [
        dict(
            mail='marcoverdi@paziente.it',
            medico='lucabianchi@medico.it',
            data_inizio=MONTH_AGO,
            data_fine=TODAY + timedelta(days=60),
            indicazioni='Assumere metformina durante i pasti principali. Monitorare glicemia 2 volte/die.',
            assunzioni=[
                dict(orario='08:00', farmaco_nome='Metmorfina', quantita=500.0, unita_misura='mg'),
                dict(orario='20:00', farmaco_nome='Metmorfina', quantita=500.0, unita_misura='mg'),
            ],
        ),
        dict(
            mail='giuliarossi@paziente.it',
            medico='lucabianchi@medico.it',
            data_inizio=MONTH_AGO - timedelta(days=15),
            data_fine=TODAY + timedelta(days=45),
            indicazioni='Schema basal-bolus. Insulina lenta la sera, rapida ai pasti solo se glicemia > 150 mg/dL.',
            assunzioni=[
                dict(orario='07:30', farmaco_nome='Insulina_Rapida', quantita=6.0, unita_misura='UI'),
                dict(orario='13:00', farmaco_nome='Insulina_Rapida', quantita=8.0, unita_misura='UI'),
                dict(orario='19:30', farmaco_nome='Insulina_Rapida', quantita=6.0, unita_misura='UI'),
                dict(orario='22:00', farmaco_nome='Insulina_Lenta', quantita=14.0, unita_misura='UI'),
            ],
        ),
        dict(
            mail='robertoneri@paziente.it',
            medico='annafontana@medico.it',
            data_inizio=MONTH_AGO - timedelta(days=5),
            data_fine=TODAY + timedelta(days=90),
            indicazioni='Glipizide a stomaco vuoto. Controllare glicemia a digiuno ogni mattina.',
            assunzioni=[
                dict(orario='07:00', farmaco_nome='Glipizide', quantita=5.0, unita_misura='mg'),
                dict(orario='19:00', farmaco_nome='Glipizide', quantita=5.0, unita_misura='mg'),
            ],
        ),
        dict(
            mail='sofiamarini@paziente.it',
            medico='annafontana@medico.it',
            data_inizio=MONTH_AGO,
            data_fine=TODAY + timedelta(days=30),
            indicazioni='Empagliflozin una volta al giorno. Aumentare apporto idrico.',
            assunzioni=[
                dict(orario='08:00', farmaco_nome='Empagliflozin', quantita=10.0, unita_misura='mg'),
            ],
        ),
        dict(
            mail='davideesposito@paziente.it',
            medico='lucabianchi@medico.it',
            data_inizio=MONTH_AGO - timedelta(days=10),
            data_fine=TODAY + timedelta(days=20),
            indicazioni='Sitagliptin mattino. Evitare alcol e stupefacenti. Follow-up renale mensile.',
            assunzioni=[
                dict(orario='08:00', farmaco_nome='Sitagliptin', quantita=100.0, unita_misura='mg'),
            ],
        ),
    ]

    for t in TERAPIE:
        model.crea_terapia(
            paziente_email=t['mail'],
            medico_email=t['medico'],
            data_inizio=t['data_inizio'],
            data_fine=t['data_fine'],
            assunzioni=t['assunzioni']
        )
        print(f"      OK    {t['mail']}: terapia")
    # ── 5. Misurazioni (ultimo mese) ─────────────────────────────
    print("\n[5/8] Misurazioni glicemiche...")

    # Momenti di misurazione
    MOMENTI = ['pre_colazione', 'post_colazione', 'pre_pranzo', 'post_pranzo', 'pre_cena', 'post_cena']

    # Range glicemici realistici per profilo (min, max) per ogni momento
    GLUCOSE_PROFILES = {
        'marcoverdi@paziente.it':    [85, 110, 130, 165, 95, 145],   # ben controllato
        'giuliarossi@paziente.it':   [140, 200, 155, 230, 130, 195], # difficile controllo
        'robertoneri@paziente.it':   [95, 135, 115, 170, 100, 160],  # medio
        'sofiamarini@paziente.it':   [110, 155, 125, 185, 115, 175], # leggermente alto
        'davideesposito@paziente.it':[165, 240, 170, 260, 150, 220], # scarsamente controllato
    }

    def days_in_range(start: date, end: date):
        """Genera tutte le date da start a end inclusi."""
        d = start
        while d <= end:
            yield d
            d += timedelta(days=1)


    def jitter(val: float, pct: float = 0.12) -> float:
        """Aggiunge rumore casuale ±pct% a un valore."""
        return round(val * (1 + random.uniform(-pct, pct)), 1)

    for paz_data in PAZIENTI:
        paz_email = paz_data['email']
        paz = Paziente.get(utente=Utente.get(email=paz_email))
        if not paz:
            continue
        profile = GLUCOSE_PROFILES[paz_email]
        count = 0
        for d in days_in_range(MONTH_AGO, TODAY):
            # I pazienti non misurano sempre tutti i momenti: simula aderenza
            num_misurazioni = random.choices([2, 3, 4, 5, 6], weights=[5, 20, 30, 30, 15])[0]
            momenti_oggi = random.sample(MOMENTI, num_misurazioni)
            for i, momento in enumerate(MOMENTI):
                if momento not in momenti_oggi:
                    continue
                # controlla duplicati
                exists = Misurazione.get(paziente=paz, date=d, momento=momento)
                if exists:
                    continue
                base = profile[i]
                model.create_misurazione(paz_email, d, momento, jitter(base))
                count += 1
        print(f"      OK    {paz_email}: {count} misurazioni")

    # ── 6. Assunzioni farmaci (ultimo mese) ──────────────────────
    print("\n[6/8] Assunzioni farmaci...")

    for t in TERAPIE:
        paz_email = t['mail']
        count = 0
        for d in days_in_range(MONTH_AGO, TODAY):
            # aderenza ~85%: ogni tanto il paziente salta una dose
            for a in t['assunzioni']:
                if random.random() < 0.15:   # 15% skip
                    continue
                farmaco = Farmaco.get(nome=a['farmaco_nome'])
                if not farmaco:
                    farmaco = Farmaco.get(nome='ALTRO')
                ora_str = a['orario']          # es. '08:00'
                h, m_ = map(int, ora_str.split(':'))
                m_ += random.randint(-10, 10)  # piccola variazione
                m_  = max(0, min(59, m_))

                model.create_assunzione(
                    patient_email=paz_email,
                    data_assunzione=d,
                    ora_assunzione=h,
                    minuto_assunzione=m_,
                    nome_farmaco=farmaco.nome,
                    quantita_assunta=a['quantita']
                )
                count += 1
        print(f"      OK    {paz_email}: {count} assunzioni")

    # ── 7. Segnalazioni ──────────────────────────────────────────
    print("\n[7/8] Segnalazioni pazienti...")

    SEGNALAZIONI = [
        ('giuliarossi@paziente.it',   'Ipoglicemia notturna',
        'Stanotte ho avuto sudorazione e tremori. Glicemia alle 3:00 era 54 mg/dL. Ho assunto zucchero. Ora sto bene.'),
        ('davideesposito@paziente.it','Glicemia molto alta',
        'Oggi pomeriggio ho misurato 310 mg/dL dopo pranzo. Non ho modificato la dieta ma ieri non ho dormito. Cosa faccio?'),
        ('robertoneri@paziente.it',   'Disturbi visivi ricorrenti',
        'Negli ultimi 5 giorni ho episodi di visione sfocata, soprattutto la mattina. Potrebbe essere legato alla glicemia?'),
        ('marcoverdi@paziente.it',    'Mal di testa post-prandiale',
        'Dopo i pasti abbondanti accuso cefalea. Ho correlato con le misurazioni: sembra comparire quando supero 170 mg/dL.'),
        ('sofiamarini@paziente.it',   'Sete intensa prima settimana',
        'Da quando ho iniziato Empagliflozin ho molta sete. Bevo circa 2.5L al giorno. È normale?'),
    ]

    for paz_email, titolo, descrizione in SEGNALAZIONI:
        paz = Paziente.get(utente=Utente.get(email=paz_email))
        if not paz:
            continue
        # evita duplicati per titolo
        existing = [s for s in paz.segnalazioni if s.titolo == titolo]
        if existing:
            print(f"      SKIP  '{titolo}' (già presente)")
            continue
        days_back = random.randint(1, 20)
        model.create_segnalazione(
            patient_email=paz_email,
            title=titolo,
            description=descrizione
        )
        print(f"      OK    '{titolo}' per {paz_email}")
    commit()


    # ── 8. Messaggi chat ────────────────────────────────────────
    print("\n[8/8] Chat...")

    CHATS = [
        # Marco ↔ Luca
        ('marcoverdi@paziente.it',    'lucabianchi@medico.it',   4, [
            ('paziente', 'Buongiorno Dottore, ho notato che la glicemia post-pranzo è spesso sopra 160. Devo preoccuparmi?'),
            ('medico',   'Buongiorno Marco. Se è un dato occasionale non c\'è allarme immediato, ma vediamo la serie storica. Sta seguendo la dieta?'),
            ('paziente', 'Sì, anche se il weekend è più difficile. Ieri sera ho mangiato fuori.'),
            ('medico',   'Capito. Provi a registrare anche il pasto: è utile correlarlo alla glicemia. Ci sentiamo a fine settimana.'),
        ]),
        # Giulia ↔ Luca
        ('giuliarossi@paziente.it',   'lucabianchi@medico.it',   7, [
            ('paziente', 'Dottore, ieri sera ho dimenticato l\'insulina lenta. Come mi devo regolare stamattina?'),
            ('medico',   'Non si preoccupi. Misuri la glicemia adesso: se è sotto 200 faccia la dose del mattino normalmente e salti la lenta di ieri.'),
            ('paziente', 'Ho 210 mg/dL. Procedo con la rapida?'),
            ('medico',   'Sì, proceda con 6 UI come da schema. Aggiunga 2 UI di correzione per la glicemia elevata. Monitori a pranzo.'),
            ('paziente', 'Ok, fatto. Grazie mille per la risposta rapida.'),
            ('medico',   'Prego. Ricordi: per dimenticanze notturne mi contatti subito, non aspetti la mattina.'),
            ('paziente', 'Capito, me ne scuso. Prenderò un promemoria sul telefono.'),
        ]),
        # Roberto ↔ Anna
        ('robertoneri@paziente.it',   'annafontana@medico.it',   5, [
            ('paziente', 'Dottoressa Fontana, negli ultimi giorni ho la vista un po\' offuscata al mattino.'),
            ('medico',   'Ciao Roberto. L\'offuscamento visivo può essere correlato a picchi glicemici notturni. Che valori registra a digiuno?'),
            ('paziente', 'Tra 140 e 165 mg/dL.'),
            ('medico',   'Sono valori un po\' alti per il digiuno. Valuterei di aggiungere Metformina serale. Venga in studio giovedì.'),
            ('paziente', 'Ci sarò. Ha orari liberi nel pomeriggio?'),
        ]),
        # Sofia ↔ Anna
        ('sofiamarini@paziente.it',   'annafontana@medico.it',   3, [
            ('paziente', 'Buongiorno! Ho iniziato Empagliflozin da una settimana. Ho un po\' più sete, è normale?'),
            ('medico',   'Sì, è un effetto atteso nei primi giorni. Aumenti l\'acqua a 2L/die. Dovrebbe normalizzarsi entro due settimane.'),
            ('paziente', 'Ok perfetto, grazie!'),
        ]),
        # Davide ↔ Luca
        ('davideesposito@paziente.it','lucabianchi@medico.it',   6, [
            ('paziente', 'Dottore, ho valori altissimi questa settimana. Ho ripreso a fumare.'),
            ('medico',   'Davide, l\'abbiamo discusso: il fumo peggiora significativamente la glicemia e la funzione renale. È urgente che smetta.'),
            ('paziente', 'Lo so, ma sono in un momento difficile.'),
            ('medico',   'Capisco. Parliamone. Posso indirizzarla al Centro Antifumo dell\'ASL, hanno ottimi risultati. Vuole che fissi un appuntamento?'),
            ('paziente', 'Forse sì, grazie. Anche i valori renali mi preoccupano.'),
            ('medico',   'Faremo un controllo creatinina e GFR entro fine mese. Intanto riduca il fumo il più possibile.'),
        ]),
    ]

    for paz_email, med_email, days_back_start, messaggi in CHATS:
        u_paz = Utente.get(email=paz_email)
        u_med = Utente.get(email=med_email)
        if not u_paz or not u_med:
            print(f"      SKIP  chat {paz_email} ↔ {med_email}")
            continue
        # evita duplicati: se già ci sono messaggi tra questi due, salta
        existing = (
            [m for m in u_paz.messaggi_inviati if m.destinatario == u_med] +
            [m for m in u_paz.messaggi_ricevuti if m.mittente == u_med]
        )
        if existing:
            print(f"      SKIP  chat {paz_email} ↔ {med_email} (già presente)")
            continue
        base_ts = NOW - timedelta(days=days_back_start)
        gap_minutes = 0
        for i, (ruolo, testo) in enumerate(messaggi):
            mittente    = u_paz if ruolo == 'paziente' else u_med
            destinatario= u_med if ruolo == 'paziente' else u_paz
            gap_minutes += random.randint(2, 15)   # sempre crescente
            ts = base_ts + timedelta(minutes=gap_minutes)

            model.invia_messaggio(mittente.email, destinatario.email, testo)
        print(f"      OK    chat {paz_email} ↔ {med_email} ({len(messaggi)} messaggi)")
    commit()

    # ── Riepilogo ────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(" SEED COMPLETATO")
    print("=" * 60)
    print(f"  Segretari  : {Segretario.select().count()}")
    print(f"  Medici     : {Medico.select().count()}")
    print(f"  Pazienti   : {Paziente.select().count()}")
    print(f"  Terapie    : {Terapia.select().count()}")
    print(f"  Misurazioni: {Misurazione.select().count()}")
    print(f"  Assunzioni : {Assunzione.select().count()}")
    print(f"  Segnalaz.  : {Segnalazione.select().count()}")
    print(f"  Alert      : {Alert.select().count()}")
    print(f"  Messaggi   : {Messaggio.select().count()}")
    print()
    print(" Credenziali di accesso:")
    print()
    print("  SEGRETARI")
    for s in SEGRETARI:
        print(f"    {s['email']}  /  {s['password']}")
    print()
    print("  MEDICI")
    for m in MEDICI:
        print(f"    {m['email']}  /  {m['password']}")
    print()
    print("  PAZIENTI")
    for p in PAZIENTI:
        print(f"    {p['email']}  /  {p['password']}")
    print()


# ---------------------------------------------------------------------------
if __name__ == '__main__':
    # Inizializza il DB se non esiste ancora (replica ciò che fa OrmModel.__init__)
    db_path = os.path.join(ROOT, 'diabete.sqlite')
    if not diabete_db.provider:          # non ancora bindato
        diabete_db.bind(provider='sqlite', filename=db_path, create_db=True)
        diabete_db.generate_mapping(create_tables=True)

    # Assicura che i farmaci base esistano
    @db_session
    def ensure_farmaci():
        if Farmaco.select().count() == 0:
            for nome, um in [('Metmorfina','mg'),('Insulina_Rapida','UI'),
                             ('Insulina_Lenta','UI'),('Glipizide','mg'),
                             ('Sitagliptin','mg'),('Empagliflozin','mg'),('ALTRO','N/D')]:
                Farmaco(nome=nome, unita_misura=um)
            commit()
    ensure_farmaci()

    seed()
