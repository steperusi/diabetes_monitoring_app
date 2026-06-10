import pytest

from pony.orm import db_session

from models.model import (
    Utente,
    Paziente,
    Medico,
    Alert,
    Terapia,
    Assunzione,
    Misurazione,
    Messaggio,
    Segnalazione
)    

#scope = function è equivalente a before/after each JUnit
#scope = session equivale invece a before/after all JUnit
@pytest.fixture(scope="function")
def test_context():

    created_emails = []

    yield created_emails

    with db_session:

        for email in created_emails:

            user = Utente.get(email=email)

            if not user:
                continue

            # elimina alert collegati
            for alert in list(user.alert):
                alert.delete()

            # elimina messaggi
            for msg in list(user.messaggi_inviati):
                msg.delete()

            for msg in list(user.messaggi_ricevuti):
                if msg.id:
                    msg.delete()

            paziente = Paziente.get(utente=user)

            if paziente:

                for seg in list(paziente.segnalazioni):
                    seg.delete()

                for mis in list(paziente.misurazioni):
                    mis.delete()

                for ass in list(paziente.assunzioni):
                    ass.delete()

                for terapia in list(paziente.terapie):
                    terapia.delete()

                paziente.delete()

            medico = Medico.get(utente=user)

            if medico:
                medico.delete()

            user.delete()
    