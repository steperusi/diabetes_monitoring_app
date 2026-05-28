"""Controller — callbacks del medico."""

from dash import Output, Input, State, ctx, no_update, html, ALL
from models.model import model, Terapia, Paziente, Medico
from pony.orm import db_session
from views.medic_view import my_patients_tab, manage_therapy_tab, add_therapy_tab, messages_tab, _render_chat, edit_patient_tab


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
                                   ('Data Inizio', data_inizio),
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
                data_fine=data_fine or None,
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
    
    # ----- modifica paziente -------------------------------------------------
    @app.callback(
        Output('m-tab-content', 'children', allow_duplicate=True),
        Input({'type': 'btn-edit-patient', 'index': ALL}, 'n_clicks'),
        prevent_initial_call=True,
    )
    def open_edit_form(n_clicks_list):
        #trova quale bottone è stato premuto
        triggered = ctx.triggered_id
        if not triggered or not any(n for n in n_clicks_list if n):
            return no_update
        cf = triggered['index']
        paziente = model.get_paziente_by_cf(cf)
        if not paziente:
            return no_update
        return edit_patient_tab(paziente)
    

    # ----- salva modifiche paziente -----------------------------------------
    @app.callback(
        Output('msg-edit-patient', 'children'),
        Output('msg-edit-patient', 'style'),
        Input('btn-save-edit-patient', 'n_clicks'),
        State('editing-patient-cf', 'data'),
        State('edit-p-nome', 'value'),
        State('edit-p-cognome', 'value'),
        State('edit-p-comorbidita', 'value'),
        State('edit-p-flags', 'value'),
        prevent_initial_call=True,
    )
    def save_edit_patient(n, cf, nome, cognome, comorbidita, flags):
        if not n or not cf:
            return '', {}
        flags = flags or []
        missing = [f for f, v in [('Nome', nome), ('Cognome', cognome),] if not v]
        if missing:
            return (f'⚠️ Campi obbligatori mancanti: {", ".join(missing)}.',{'color': '#dc2626', 'fontSize': '13px'})
        try:
            model.modifica_paziente(
                codice_fiscale = cf,
                nome=nome,
                cognome=cognome,
                fumatore='fumatore' in flags,
                ex_fumatore='ex_fumatore' in flags,
                obesita='obesita' in flags,
                problemi_alcol='problemi_alcol' in flags,
                problemi_stupefacenti='problemi_stupefacenti' in flags,
                comorbidita=comorbidita or '',
            )
            return ('✅ Modifiche salvate con successo.', {'color': '#16a34a', 'fontSize': '13px'})
        except Exception as e:
            return (f'❌ Errore: {str(e)}', {'color': '#dc2626', 'fontSize': '13px'})
        
    # ----- tasto indietro torna alla lista --------------------------------------------
    @app.callback(
        Output('m-tab-content', 'children', allow_duplicate=True),
        Output('m-main-tabs', 'value'),
        Input('btn-back-patients', 'n_clicks'),
        State('medic-email', 'data'),
        prevent_initial_call=True,
    )
    def back_to_patients(n,email):
        if not n:
            return no_update, no_update
        pazienti = model.get_pazienti_medico(email)
        return my_patients_tab(pazienti), 'patients'
    

    # ---- carica alert medico -------------------------------------------------
    @app.callback(
        Output('m-alert-badge', 'children'),
        Output('m-alert-badge', 'style'),
        Output('m-alert-panel', 'children'),
        Input('m-refresh', 'n_intervals'),
        State('medic-email', 'data'),
    )
    def refresh_alerts_medico(_, medic_email):
        if isinstance(medic_email, dict):
            medic_email = medic_email.get('email')
        if not medic_email:
            return '0', {'display': 'none'}, []

        alerts = model.get_alert_non_letti(medic_email)
        count = len(alerts)

        badge_style = {
            'background': '#ef4444', 'color': 'white',
            'borderRadius': '50%', 'fontSize': '11px',
            'padding': '1px 6px', 'marginLeft': '4px',
            'fontWeight': '700',
            'display': 'inline' if count > 0 else 'none',
        }

        if not alerts:
            pannello_content = [
                html.Div('Notifiche', style={
                    'padding': '12px 16px', 'fontWeight': '700',
                    'fontSize': '14px', 'borderBottom': '1px solid #e5e7eb',
                    'color': '#1f2937',
                }),
                html.Div('Nessuna notifica.', style={
                    'padding': '16px', 'color': '#9ca3af', 'fontSize': '14px',
                }),
            ]
        else:
            voci = []
            for a in alerts:
                voci.append(html.Div([
                    html.Div(a['informazioni'], style={
                        'fontSize': '13px', 'color': '#1f2937', 'marginBottom': '4px',
                    }),
                    html.Div([
                        html.Span(a['timestamp'], style={
                            'fontSize': '11px', 'color': '#9ca3af',
                        }),
                        html.Button('✓ Letto', id={'type': 'btn-mark-read-medic', 'index': a['id']},
                                    n_clicks=0, style={
                                        'background': 'none', 'border': 'none',
                                        'color': '#4748AC', 'fontSize': '12px',
                                        'cursor': 'pointer', 'fontWeight': '600',
                                        'padding': '0', 'marginLeft': '8px',
                                    }),
                    ], style={'display': 'flex', 'alignItems': 'center'}),
                ], style={
                    'padding': '12px 16px', 'borderBottom': '1px solid #f3f4f6',
                }))

            pannello_content = [
                html.Div('Notifiche', style={
                    'padding': '12px 16px', 'fontWeight': '700',
                    'fontSize': '14px', 'borderBottom': '1px solid #e5e7eb',
                    'color': '#1f2937',
                }),
                *voci,
            ]

        return str(count), badge_style, pannello_content


    # ---- apri/chiudi pannello alert medico -----------------------------------
    @app.callback(
        Output('m-alert-panel', 'style'),
        Input('m-alert-btn', 'n_clicks'),
        State('m-alert-panel', 'style'),
        prevent_initial_call=True,
    )
    def toggle_alert_panel_medico(n, current_style):
        is_open = current_style.get('display') == 'block'
        return {**current_style, 'display': 'none' if is_open else 'block'}


    # ---- segna alert medico come letto ---------------------------------------
    @app.callback(
        Output('m-refresh', 'n_intervals'),
        Input({'type': 'btn-mark-read-medic', 'index': ALL}, 'n_clicks'),
        State('m-refresh', 'n_intervals'),
        prevent_initial_call=True,
    )
    def mark_alert_read_medico(n_clicks_list, current_intervals):
        triggered = ctx.triggered_id
        if not triggered or not any(n for n in n_clicks_list if n):
            return no_update
        model.segna_alert_letto(triggered['index'])
        return (current_intervals or 0) + 1