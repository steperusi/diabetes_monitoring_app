"""Controller — callbacks del medico."""

from dash import Output, Input, State, ctx, no_update, html, ALL, MATCH
from models.model import model, Terapia, Paziente, Medico
from pony.orm import db_session
from views.medic_view import my_patients_tab, manage_therapy_tab, add_therapy_tab, render_storico_assunzioni, render_storico_temp, messages_tab, _render_chat, edit_patient_tab


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


    
 # ---- TERAPIE -----------------------------------------------------------

    @app.callback(
        Output('store-assunzioni-temp', 'data'),
        Input({'type': 'btn-del-assunzione', 'index': ALL}, 'n_clicks'),
        State('store-assunzioni-temp', 'data'),
        prevent_initial_call=True,
    )
    def elimina_assunzione(n_del, store):
        if not any(n_del):
            return no_update
        triggered = ctx.triggered_id
        if not isinstance(triggered, dict) or triggered.get('type') != 'btn-del-assunzione':
            return no_update
        idx = triggered['index']
        items = (store or {}).get('items', [])
        return {'items': [a for i, a in enumerate(items) if i != idx], 'ts': 0}

    @app.callback(
        Output('store-assunzioni-temp', 'data', allow_duplicate=True),
        Output('store-reset-form', 'data'),
        Output('msg-add-assunzione', 'children'),
        Input('btn-add-assunzione', 'n_clicks'),
        State('store-assunzioni-temp', 'data'),
        State('inp-fascia', 'value'),
        State('inp-farmaco-row', 'value'),
        State('inp-quantita-row', 'value'),
        prevent_initial_call=True,
    )
    def aggiungi_assunzione(n, store, fascia, farmaco, quantita):
        if not fascia or not farmaco or quantita is None or quantita == '':
            return no_update, no_update, \
                html.Span('⚠️ Compila tutti i campi prima di aggiungere.', style={'color': '#dc2626'})
        items = (store or {}).get('items', [])
        nuova = {'orario': fascia, 'farmaco_nome': farmaco, 'quantita': float(quantita)}
        return {'items': items + [nuova], 'ts': n}, n, ''
    
    
    @app.callback(
        Output('inp-fascia', 'value'),
        Output('inp-farmaco-row', 'value'),
        Output('inp-quantita-row', 'value'),
        Input('store-reset-form', 'data'),
        prevent_initial_call=True,
    )
    def reset_form_assunzione(ts):
        return None, None, None
    

    @app.callback(
        Output('storico-temp-table', 'children'),
        Output('storico-temp-section', 'style'),
        Input('store-assunzioni-temp', 'data'),
        prevent_initial_call=True,
    )
    def aggiorna_storico_temp(store):
        items = (store or {}).get('items', [])
        if not items:
            return [], {'display': 'none'}
        return render_storico_temp(items), {'display': 'block'}


    #salvataggio terapia
    @app.callback(
        Output('msg-add-therapy', 'children'),
        Output('msg-add-therapy', 'style'),
        Input('btn-save-therapy', 'n_clicks'),
        State('inp-p-nome', 'value'),
        State('medic-email', 'data'),
        State('inp-data-inizio', 'date'),
        State('inp-data-fine', 'date'),
        State('store-assunzioni-temp', 'data'),
        prevent_initial_call=True,
    )
    def save_therapy(n, p_email, m_email, data_inizio, data_fine, store):
        assunzioni = (store or {}).get('items', [])

        missing = [f for f, v in [('Paziente', p_email), ('Data Inizio', data_inizio)] if not v]
        if missing:
            return (
                f'⚠️ Campi obbligatori mancanti: {", ".join(missing)}.',
                {'color': '#dc2626', 'fontSize': '13px'},
            )
        if not assunzioni:
            return (
                '⚠️ Aggiungi almeno un\'assunzione prima di salvare.',
                {'color': '#dc2626', 'fontSize': '13px'},
            )

        try:
            model.crea_terapia(
                paziente_email=p_email,
                medico_email=m_email,
                data_inizio=data_inizio,
                data_fine=data_fine or None,
                assunzioni=assunzioni,
            )
        except Exception as e:
            return (
                f'❌ Errore durante il salvataggio: {str(e)}',
                {'color': '#dc2626', 'fontSize': '13px'},
            )

        return (
            '✅ Terapia aggiunta con successo',
            {'color': '#16a34a', 'fontSize': '13px'},
        )
        
        
    #dropdown per mostrare lista assunzioni singola terapia    
    @app.callback(
        Output({'type': 'therapy-detail', 'index': MATCH}, 'style'),
        Output({'type': 'btn-expand-therapy', 'index': MATCH}, 'children'),
        Input({'type': 'btn-expand-therapy', 'index': MATCH}, 'n_clicks'),
        prevent_initial_call=True,
    )
    def toggle_therapy_detail(n_clicks):
        if n_clicks % 2 == 1:
            return {'display': 'block'}, '▼'
        return {'display': 'none'}, '▶'
            


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