# python -m pytest .\test\model.py -V --tb=short
# da directory telemedicina

import uuid
from models.model import model
from datetime import date, timedelta

from pony.orm import db_session

from models.model import (
    Utente,
    Medico,
    Paziente,
    Alert
)


# ==================================================
# HELPERS
# ==================================================

def unique():
    return uuid.uuid4().hex[:8]


# ==================================================
# AUTENTICAZIONE
# ==================================================

def test_authenticate_valid_user():

    user = model.authenticate(
        "segretario@telemedicina.it",
        "Admin123"
    )

    assert user is not None
    assert user["ruolo"] == "segretario"


def test_authenticate_invalid_user():

    user = model.authenticate(
        "fake@test.it",
        "wrong"
    )

    assert user is None


# ==================================================
# MEDICO
# ==================================================

def test_crea_medico(test_context):

    suffix = unique()

    email = f"medico_{suffix}@test.it"

    model.crea_medico(
        nome="Mario",
        cognome="Rossi",
        email=email,
        matricola=f"MAT{suffix}",
        password="Password123"
    )
    test_context.append(email)

    user = model.get_user(email)

    assert user is not None
    assert user["ruolo"] == "medico"


# ==================================================
# PAZIENTE
# ==================================================

def test_crea_paziente(test_context):

    suffix = unique()

    medico_email = f"medico_{suffix}@test.it"

    model.crea_medico(
        nome="Mario",
        cognome="Rossi",
        email=medico_email,
        matricola=f"MAT{suffix}",
        password="Password123"
    )
    test_context.append(medico_email)

    patient_email = f"patient_{suffix}@test.it"

    model.crea_paziente(
        nome="Luca",
        cognome="Verdi",
        email=patient_email,
        cf=f"CF{suffix}",
        medico_id=medico_email,
        password="Password123"
    )   
    test_context.append(patient_email)

    user = model.get_user(patient_email)

    assert user is not None
    assert user["ruolo"] == "paziente"


# ==================================================
# TERAPIA
# ==================================================

def test_crea_terapia(test_context):

    suffix = unique()

    medico_email = f"medico_{suffix}@test.it"

    model.crea_medico(
        "Mario",
        "Rossi",
        medico_email,
        f"MAT{suffix}",
        "Password123"
    )
    test_context.append(medico_email)

    paziente_email = f"patient_{suffix}@test.it"

    model.crea_paziente(
        "Luca",
        "Verdi",
        paziente_email,
        f"CF{suffix}",
        medico_email,
        "Password123"
    )
    test_context.append(paziente_email)


    model.crea_terapia(
        paziente_email=paziente_email,
        medico_email=medico_email,
        data_inizio=date.today(),
        data_fine=date.today() + timedelta(days=30),
        assunzioni=[
            {
                "orario": "colazione",
                "farmaco_nome": "Metmorfina",
                "quantita": 500
            }
        ]
    )

    terapie = model.get_terapie_paziente(
        paziente_email
    )

    assert len(terapie) >= 1


# ==================================================
# GLICEMIA
# ==================================================

@db_session
def test_alert_glicemia_critica(test_context):
    suffix = unique()

    medico_email = f"medico_{suffix}@test.it"

    model.crea_medico(
        nome="Mario",
        cognome="Rossi",
        email=medico_email,
        matricola=f"MAT{suffix}",
        password="Password123"
    )
    test_context.append(medico_email)


    patient_email = f"patient_{suffix}@test.it"

    model.crea_paziente(
        nome="Luca",
        cognome="Verdi",
        email=patient_email,
        cf=f"CF{suffix}",
        medico_id=medico_email,
        password="Password123"
    )
    test_context.append(patient_email)


    model.create_misurazione(
        patient_email,
        date.today(),
        "pre_colazione",
        350
    )

    medico = Utente.get(
        email=medico_email
    )

    critici = [
        a for a in medico.alert
        if "CRITICO" in a.informazioni
    ]

    assert len(critici) > 0


# ==================================================
# CREAZIONE MISURAZIONE
# ==================================================

@db_session
def test_crea_misurazione(test_context):
    suffix = unique()

    medico_email = f"medico_{suffix}@test.it"

    model.crea_medico(
        nome="Mario",
        cognome="Rossi",
        email=medico_email,
        matricola=f"MAT{suffix}",
        password="Password123"
    )
    test_context.append(medico_email)


    patient_email = f"patient_{suffix}@test.it"

    model.crea_paziente(
        nome="Luca",
        cognome="Verdi",
        email=patient_email,
        cf=f"CF{suffix}",
        medico_id=medico_email,
        password="Password123"
    )
    test_context.append(patient_email)


    model.create_misurazione(
        patient_email,
        date.today(),
        "pre_colazione",
        160
    )
    misurazione = model.get_misurazione(
        patient_email=patient_email,
        data_misurazione=date.today(),
        momento_misurazione="pre_colazione"
    )
    
    assert isinstance(misurazione, dict)



# ==================================================
# GESTIONE FARMACI
# ==================================================
def test_assunzione_farmaco(test_context):
    suffix = unique()

    medico_email = f"medico_{suffix}@test.it"

    model.crea_medico(
        "Mario",
        "Rossi",
        medico_email,
        f"MAT{suffix}",
        "Password123"
    )
    test_context.append(medico_email)

    paziente_email = f"patient_{suffix}@test.it"

    model.crea_paziente(
        "Luca",
        "Verdi",
        paziente_email,
        f"CF{suffix}",
        medico_email,
        "Password123"
    )
    
    test_context.append(paziente_email)

    model.crea_terapia(
        paziente_email=paziente_email,
        medico_email=medico_email,
        data_inizio=date.today(),
        data_fine=date.today() + timedelta(days=30),
        assunzioni=[
            {
                "orario": "colazione",
                "farmaco_nome": "Metmorfina",
                "quantita": 500
            }
        ]
    )
    model.create_assunzione(
        patient_email=paziente_email,
        data_assunzione=date.today(),
        ora_assunzione=9,
        minuto_assunzione=0,
        nome_farmaco="Metmorfina",
        quantita_assunta=500
    )    
    assunzione = model.get_assunzioni_by_date(patient_email=paziente_email, data_assunzione=date.today())
    assert len(assunzione) >= 1

def test_assunzione_farmaco_non_prescitto(test_context):
    suffix = unique()

    medico_email = f"medico_{suffix}@test.it"

    model.crea_medico(
        "Mario",
        "Rossi",
        medico_email,
        f"MAT{suffix}",
        "Password123"
    )
    test_context.append(medico_email)

    paziente_email = f"patient_{suffix}@test.it"

    model.crea_paziente(
        "Luca",
        "Verdi",
        paziente_email,
        f"CF{suffix}",
        medico_email,
        "Password123"
    )
    test_context.append(paziente_email)

    model.crea_terapia(
        paziente_email=paziente_email,
        medico_email=medico_email,
        data_inizio=date.today(),
        data_fine=date.today() + timedelta(days=30),
        assunzioni=[
            {
                "orario": "colazione",
                "farmaco_nome": "Metmorfina",
                "quantita": 500
            }
        ]
    )
    model.create_assunzione(
        patient_email=paziente_email,
        data_assunzione=date.today(),
        ora_assunzione=9,
        minuto_assunzione=0,
        nome_farmaco="Insulina_Rapida",
        quantita_assunta=500
    )
    alerts = model.get_alert_non_letti(
        medico_email
    )

    assert len(alerts) > 0   
    
    
# ==================================================
# SEGNALAZIONE
# ==================================================

def test_invia_segnalazione(test_context):
    suffix = unique()

    medico_email = f"medico_{suffix}@test.it"

    model.crea_medico(
        nome="Mario",
        cognome="Rossi",
        email=medico_email,
        matricola=f"MAT{suffix}",
        password="Password123"
    )
    test_context.append(medico_email)

    patient_email = f"patient_{suffix}@test.it"

    model.crea_paziente(
        nome="Luca",
        cognome="Verdi",
        email=patient_email,
        cf=f"CF{suffix}",
        medico_id=medico_email,
        password="Password123"
    )
    
    test_context.append(patient_email)
    
    model.create_segnalazione(
        patient_email=patient_email,
        title="Mal di denti persistente",
        description="Se mangio i sassi mi fanno male i denti"
    )
    segnalazioni = model.get_segnalazioni(patient_email=patient_email)
    
    assert len(segnalazioni) > 0

    
# ==================================================
# CHAT
# ==================================================

def test_invia_messaggio(test_context):
    suffix = unique()

    medico_email = f"medico_{suffix}@test.it"

    model.crea_medico(
        nome="Mario",
        cognome="Rossi",
        email=medico_email,
        matricola=f"MAT{suffix}",
        password="Password123"
    )
    test_context.append(medico_email)

    patient_email = f"patient_{suffix}@test.it"

    model.crea_paziente(
        nome="Luca",
        cognome="Verdi",
        email=patient_email,
        cf=f"CF{suffix}",
        medico_id=medico_email,
        password="Password123"
    )
    test_context.append(patient_email)

    model.invia_messaggio(
        patient_email,
        medico_email,
        "Messaggio test"
    )

    conv = model.get_conversazione(
        patient_email,
        medico_email
    )

    assert len(conv) > 0


# ==================================================
# ALERT
# ==================================================

def test_get_alert_non_letti(test_context):
    suffix = unique()

    medico_email = f"medico_{suffix}@test.it"

    model.crea_medico(
        nome="Mario",
        cognome="Rossi",
        email=medico_email,
        matricola=f"MAT{suffix}",
        password="Password123"
    )
    test_context.append(medico_email)

    alerts = model.get_alert_non_letti(
        medico_email
    )

    assert isinstance(alerts, list)


@db_session
def test_segna_alert_letto(test_context):
    suffix = unique()

    medico_email = f"medico_{suffix}@test.it"

    model.crea_medico(
        nome="Mario",
        cognome="Rossi",
        email=medico_email,
        matricola=f"MAT{suffix}",
        password="Password123"
    )
    test_context.append(medico_email)

    patient_email = f"patient_{suffix}@test.it"

    model.crea_paziente(
        nome="Luca",
        cognome="Verdi",
        email=patient_email,
        cf=f"CF{suffix}",
        medico_id=medico_email,
        password="Password123"
    )
    test_context.append(patient_email)
    
    model.create_misurazione(
        patient_email,
        date.today(),
        "pre_colazione",
        350
    )

    medico = Utente.get(
        email=medico_email
    )

    alert = next(iter(medico.alert), None)

    if alert:

        model.segna_alert_letto(alert.id)

        updated = Alert.get(id=alert.id)

        assert updated.letto is True