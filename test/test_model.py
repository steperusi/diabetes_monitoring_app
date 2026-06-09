# python -m pytest .\test\test_model.py -v
# da directory telemedicina

import pytest
from datetime import date, timedelta

from models.model import (
    model,
    Utente,
    Paziente,
    Medico,
    Terapia,
    Alert,
    Messaggio
)
from pony.orm import db_session


# ============================================================
# AUTENTICAZIONE
# ============================================================

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


# ============================================================
# CREAZIONE MEDICO
# ============================================================

def test_crea_medico():
    email = "pytest_medico@test.it"
    try:
        model.crea_medico(
            nome="Mario",
            cognome="Rossi",
            email=email,
            matricola="PYTEST001",
            password="Password123"
        )
    except:
        pass
    user = model.get_user(email)
    assert user is not None
    assert user["ruolo"] == "medico"


# ============================================================
# CREAZIONE PAZIENTE
# ============================================================

def test_crea_paziente():
    email = "pytest_paziente@test.it"
    try:
        model.crea_paziente(
            nome="Luca",
            cognome="Verdi",
            email=email,
            cf="PYTESTCF12345",
            medico_id="lucabianchi@medico.it",
            password="Password123"
        )
    except:
        pass
    user = model.get_user(email)
    assert user is not None
    assert user["ruolo"] == "paziente"


# ============================================================
# TERAPIA
# ============================================================

def test_crea_terapia():
    assunzioni = [
        {
            "orario": "colazione",
            "farmaco_nome": "Metmorfina",
            "quantita": 500
        }
    ]
    model.crea_terapia(
        paziente_email="marcoverdi@paziente.it",
        medico_email="lucabianchi@medico.it",
        data_inizio=date.today(),
        data_fine=date.today() + timedelta(days=30),
        assunzioni=assunzioni
    )
    terapie = model.get_terapie_paziente(
        "marcoverdi@paziente.it"
    )
    assert len(terapie) > 0


def test_crea_terapia_farmaco_non_esistente():
    assunzioni = [
        {
            "orario": "colazione",
            "farmaco_nome": "FARMACO_INESISTENTE",
            "quantita": 100
        }
    ]
    with pytest.raises(ValueError):
        model.crea_terapia(
            paziente_email="marcoverdi@paziente.it",
            medico_email="lucabianchi@medico.it",
            data_inizio=date.today(),
            data_fine=None,
            assunzioni=assunzioni
        )


# ============================================================
# MISURAZIONI
# ============================================================

def test_create_misurazione():
    result = model.create_misurazione(
        "marcoverdi@paziente.it",
        date.today(),
        "pre_colazione",
        110
    )
    assert result is True


@db_session
def test_misurazione_critica_generates_alert():
    model.create_misurazione(
        "marcoverdi@paziente.it",
        date.today(),
        "pre_colazione",
        350
    )
    medico = Utente.get(
        email="lucabianchi@medico.it"
    )
    alerts = [
        a for a in medico.alert
        if "CRITICO" in a.informazioni
    ]
    assert len(alerts) > 0


# ============================================================
# ASSUNZIONI
# ============================================================

def test_create_assunzione():
    result = model.create_assunzione(
        "marcoverdi@paziente.it",
        date.today(),
        8,
        30,
        "Metmorfina",
        500
    )
    assert result is True


@db_session
def test_farmaco_non_prescritto_alert():
    model.create_assunzione(
        "marcoverdi@paziente.it",
        date.today(),
        8,
        30,
        "FarmacoInventato",
        100
    )
    medico = Utente.get(
        email="lucabianchi@medico.it"
    )
    alerts = [
        a for a in medico.alert
        if "NON PRESCRITTO" in a.informazioni
    ]
    assert len(alerts) > 0


# ============================================================
# SEGNALAZIONI
# ============================================================

def test_create_segnalazione():
    result = model.create_segnalazione(
        "marcoverdi@paziente.it",
        "Mal di testa",
        "Sintomo comparso stamattina"
    )
    assert result is True


# ============================================================
# CHAT
# ============================================================

def test_invia_messaggio():
    model.invia_messaggio(
        "marcoverdi@paziente.it",
        "lucabianchi@medico.it",
        "Messaggio di test"
    )
    conv = model.get_conversazione(
        "marcoverdi@paziente.it",
        "lucabianchi@medico.it"
    )
    assert len(conv) > 0


# ============================================================
# VALIDAZIONI
# ============================================================

def test_validate_misurazione_ok():
    simbolo, colore = model.validate_misurazione(
        110,
        "pre_colazione"
    )
    assert simbolo == "✓"


def test_validate_misurazione_ko():
    simbolo, colore = model.validate_misurazione(
        250,
        "pre_colazione"
    )
    assert simbolo == "✗"


# ============================================================
# ALERT
# ============================================================

def test_get_alert_non_letti():
    alerts = model.get_alert_non_letti(
        "lucabianchi@medico.it"
    )
    assert isinstance(alerts, list)


@db_session
def test_segna_alert_letto():
    medico = Utente.get(
        email="lucabianchi@medico.it"
    )
    alert = next(iter(medico.alert), None)
    if alert is None:
        pytest.skip("Nessun alert presente")
    model.segna_alert_letto(alert.id)
    updated = Alert.get(id=alert.id)
    assert updated.letto is True