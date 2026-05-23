"""Controller — callbacks del medico."""

from dash import Output, Input, State
from models.model import model, Terapia, Paziente, Medico
from pony.orm import db_session
from views.medic_view import my_patients_tab, manage_therapy_tab, add_therapy_tab


def register_callbacks(app):

    #rendering delle tab principali
    @app.callback(
        Output('m-tab-content', 'children'),
        Input('m-main-tabs', 'value'),
        State('medic-email', 'data'),
    )
    def render_tab(tab, email):
        if tab == 'patients':
            return my_patients_tab(email)
        if tab == 'view-therapies':
            return manage_therapy_tab(email)
        return add_therapy_tab(email)

    #salvataggio terapia
    @app.callback(
        Output('msg-add-therapy', 'children'),
        Output('msg-add-therapy', 'style'),
        Input('btn-save-therapy', 'n_clicks'),
        State('inp-p-nome', 'value'), #email paziente dallo Store
        State('medic-email', 'data'), #email medico da sessione
        State('inp-f-nome', 'value'),
        State('inp-data-inizio', 'date'),
        State('inp-data-fine', 'date'),
        State('inp-assunzioni-giornaliere', 'value'),
        State('inp-quantita-per-assunzione', 'value'),
        State('inp-unita-misura', 'value'),
        prevent_initial_call=True,
    )
    def save_therapy(n, p_email, m_email, f_nome, data_inizio, data_fine, assunzioni_giornaliere, quantita_per_assunzione, unita_misura):
        if not n:
            return '', {}
        missing = [f for f, v in [('Paziente', p_email), ('Nome Farmaco', f_nome),
                                   ('Data Inizio', data_inizio), ('Data Fine', data_fine),
                                   ('Assunzioni Giornaliere', assunzioni_giornaliere),
                                   ('Quantità per Assunzione', quantita_per_assunzione),
                                   ('Unità di Misura', unita_misura)] if not v]
        if missing:
            return (f'⚠️ Campi obbligatori mancanti: {", ".join(missing)}.',
                    {'color': '#dc2626', 'fontSize': '13px'})
        try:
            model.crea_terapia(
                paziente_email=p_email,
                medico_email=m_email,
                farmaco_nome=f_nome,
                data_inizio=data_inizio,
                data_fine=data_fine,
                assunzioni_giornaliere=assunzioni_giornaliere,
                quantita_per_assunzione=quantita_per_assunzione,
                unita_misura=unita_misura
            )
            return ('✅ Terapia aggiunta con successo', 
                    {'color': '#16a34a', 'fontSize': '13px'})
        except Exception as e:
            return (f'❌ Errore durante l\'aggiunta della terapia: {str(e)}', 
                    {'color': '#dc2626', 'fontSize': '13px'})