"""Controller — callbacks del medico."""

from dash import Output, Input, State, ctx, no_update, html
from models.model import model, Terapia, Paziente, Medico
from pony.orm import db_session
from views.medic_view import my_patients_tab, manage_therapy_tab, add_therapy_tab, messages_tab, _render_chat


def register_callbacks(app):

    #rendering delle tab principali
    @app.callback(
        Output('m-tab-content', 'children'),
        Input('m-main-tabs', 'value'),
        State('medic-email', 'data'),
    )
    def render_tab(tab, email):
        if tab == 'patients':
            pazienti = model.get_pazienti_medico(email)
            return my_patients_tab(pazienti)
        if tab == 'view-therapies':
            return manage_therapy_tab(email)
        if tab == 'add-therapy':
            return add_therapy_tab(email)
        if tab == 'messages':
            return messages_tab()

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
            pazienti = model.get_pazienti_medico(email)
            return my_patients_tab(pazienti)
        return my_patients_tab([])  # fallback, aggiungi altri tab qui


# ---- messaggi -----------------------------------------------------------
    @app.callback(
        Output('m-conv-select', 'options'),
        Output('m-chat-area', 'children'),
        Output('m-msg-input', 'value'),
        Output('m-send-status', 'children'),
        Input('m-btn-send', 'n_clicks'),
        Input('m-conv-select', 'value'),
        Input('m-refresh', 'n_intervals'),
        State('m-msg-input', 'value'),
        State('medic-email', 'data'),
        #prevent_initial_call = True,
    )
    def update_messages(send_n, conv, _, msg_text, medic_email):
        if isinstance(medic_email, dict):
            medic_email = medic_email.get('email')
        if not medic_email:
            return [], html.P('Caricamento...'), '', ''
        
        trigger = ctx.triggered_id
        status = ''

        # Solo i propri pazienti possono ricevere messaggi
        pazienti = model.get_pazienti_medico(medic_email)
        accepted = {p['codice_fiscale'] for p in pazienti}

        if trigger == 'm-btn-send' and conv and msg_text:
            try:
                model.invia_messaggio(medic_email, conv, msg_text)
                status='✅ Inviato.'
            except Exception as e:
                status = f'❌ Errore: {str(e)}'

        options = [
            {'label': f"{p['nome']} {p['cognome']}", 'value': p['email']}
            for p in pazienti
        ]
        if conv:
            msgs = model.get_conversazione(medic_email, conv)
            chat = _render_chat(msgs, medic_email)
        else:
            chat = html.P('Seleziona una conversazione.', style={'color': '#9ca3af'})

        new_input = '' if trigger == 'm-btn-send' else no_update
        return options, chat, new_input, status