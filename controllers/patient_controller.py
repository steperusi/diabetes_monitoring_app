from dash import Output, Input, State, ctx, html, no_update
import plotly.express as px
from models.model import model
from datetime import date

MOMENTI = {
    'pre_colazione': 'p-meas-breakfast-before',
    'post_colazione': 'p-meas-breakfast-after',
    'pre_pranzo': 'p-meas-lunch-before',
    'post_pranzo': 'p-meas-lunch-after',
    'pre_cena': 'p-meas-dinner-before',
    'post_cena': 'p-meas-dinner-after',
}

SHOW = {'display': 'block'}
HIDE = {'display': 'none'}

def _render_chat_patient(msgs: list, my_email: str):
    if not msgs:
        return html.P('Nessun messaggio.', style={'color': '#9ca3af', 'fontSize': '14px'})
    bubbles = []
    for m in msgs:
        is_mine = m['mittente'] == my_email
        bubbles.append(
            html.Div([
                html.Div(m['testo'], style={
                    'background': '#0066cc' if is_mine else '#f3f4f6',
                    'color': 'white' if is_mine else '#1f2937',
                    'borderRadius': '12px', 'padding': '8px 14px',
                    'maxWidth': '70%', 'fontSize': '14px',
                }),
                html.Div(m['timestamp'], style={
                    'fontSize': '11px', 'color': '#9ca3af', 'marginTop': '2px',
                }),
            ], style={
                'display': 'flex', 'flexDirection': 'column',
                'alignItems': 'flex-end' if is_mine else 'flex-start',
                'marginBottom': '10px',
            })
        )
    return html.Div(bubbles)
        


def register_callbacks(app):
    
    # Switch tab
    @app.callback(
        Output('p-tab-health', 'style'),
        Output('p-tab-data', 'style'),
        Output('p-tab-doctor', 'style'),
        Output('p-tab-therapy', 'style'),
        Input('p-main-tabs', 'value'),
    )
    def switch_tab(tab):
        return (SHOW if tab == 'health' else HIDE,
                SHOW if tab == 'data' else HIDE,
                SHOW if tab == 'doctor' else HIDE,
                SHOW if tab == 'therapy' else HIDE)
    
    # ---- Misurazioni callback --------------------------------------------------
    @app.callback(
        Output('p-meas-breakfast-before', 'value'),
        Output('p-meas-breakfast-after', 'value'),
        Output('p-meas-lunch-before', 'value'),
        Output('p-meas-lunch-after', 'value'),
        Output('p-meas-dinner-before', 'value'),
        Output('p-meas-dinner-after', 'value'),
        Input('p-date-picker', 'date'),
        State('session', 'data'),
    )
    def load_misurazioni_for_date(meas_date, session):
        if not session or not meas_date:
            return None, None, None, None, None, None
        
        values = {}
        momenti = ['pre_colazione', 'post_colazione', 'pre_pranzo', 'post_pranzo', 'pre_cena', 'post_cena']
        
        for momento in momenti:
            mis = model.get_misurazione(session['email'], meas_date, momento)
            if mis:
                values[momento] = mis['valore_mg_dl']
            else:
                values[momento] = None
        
        return (values['pre_colazione'], values['post_colazione'], 
                values['pre_pranzo'], values['post_pranzo'],
                values['pre_cena'], values['post_cena'])
    
    # ---- Load assunzioni when date changes --------------------------------------------------
    @app.callback(
        Output('p-med-hour-0', 'value'),
        Output('p-med-minute-0', 'value'),
        Output('p-med-name-0', 'value'),
        Output('p-med-qty-0', 'value'),
        Output('p-med-hour-1', 'value'),
        Output('p-med-minute-1', 'value'),
        Output('p-med-name-1', 'value'),
        Output('p-med-qty-1', 'value'),
        Output('p-med-hour-2', 'value'),
        Output('p-med-minute-2', 'value'),
        Output('p-med-name-2', 'value'),
        Output('p-med-qty-2', 'value'),
        Output('p-med-hour-3', 'value'),
        Output('p-med-minute-3', 'value'),
        Output('p-med-name-3', 'value'),
        Output('p-med-qty-3', 'value'),
        Output('p-med-hour-4', 'value'),
        Output('p-med-minute-4', 'value'),
        Output('p-med-name-4', 'value'),
        Output('p-med-qty-4', 'value'),
        Input('p-date-picker', 'date'),
        State('session', 'data'),
    )
    def load_assunzioni_for_date(ass_date, session):
        if not session or not ass_date:
            return tuple([None] * 20)
        
        assunzioni = model.get_assunzioni_by_date(session['email'], ass_date)
        
        # Crea una lista di tuple (hour, minute, name, qty) per ogni entry
        result = []
        for i in range(5):
            if i < len(assunzioni):
                ass = assunzioni[i]
                result.extend([
                    ass['timestamp_hour'],
                    ass['timestamp_minute'],
                    ass['farmaco_nome'],
                    ass['quantita_assunta']
                ])
            else:
                result.extend([None, None, None, None])
        
        return tuple(result)
    
    # ---- Save all daily data (misurazioni + assunzioni) --------------------------------------------------
    @app.callback(
        Output('p-save-message', 'children'),
        Input('p-save-daily-data', 'n_clicks'),
        State('p-date-picker', 'date'),
        State('p-meas-breakfast-before', 'value'),
        State('p-meas-breakfast-after', 'value'),
        State('p-meas-lunch-before', 'value'),
        State('p-meas-lunch-after', 'value'),
        State('p-meas-dinner-before', 'value'),
        State('p-meas-dinner-after', 'value'),
        State('p-med-hour-0', 'value'),
        State('p-med-minute-0', 'value'),
        State('p-med-name-0', 'value'),
        State('p-med-qty-0', 'value'),
        State('p-med-hour-1', 'value'),
        State('p-med-minute-1', 'value'),
        State('p-med-name-1', 'value'),
        State('p-med-qty-1', 'value'),
        State('p-med-hour-2', 'value'),
        State('p-med-minute-2', 'value'),
        State('p-med-name-2', 'value'),
        State('p-med-qty-2', 'value'),
        State('p-med-hour-3', 'value'),
        State('p-med-minute-3', 'value'),
        State('p-med-name-3', 'value'),
        State('p-med-qty-3', 'value'),
        State('p-med-hour-4', 'value'),
        State('p-med-minute-4', 'value'),
        State('p-med-name-4', 'value'),
        State('p-med-qty-4', 'value'),
        State('session', 'data'),
        prevent_initial_call=True,
    )
    def save_all_data(n_clicks, meas_date, bf, af, lf, laf, df, daf,
                      h0, m0, n0, q0, h1, m1, n1, q1, h2, m2, n2, q2,
                      h3, m3, n3, q3, h4, m4, n4, q4, session):
        if not session or not meas_date:
            return 'Errore: sessione non valida.'
        
        total_saved = 0
        total_errors = 0
        
        # Salva misurazioni
        measurements = [
            ('pre_colazione', bf),
            ('post_colazione', af),
            ('pre_pranzo', lf),
            ('post_pranzo', laf),
            ('pre_cena', df),
            ('post_cena', daf),
        ]
        
        for momento, valore in measurements:
            if valore is not None:
                try:
                    success = model.create_misurazione(session['email'], meas_date, momento, valore)
                    if success:
                        total_saved += 1
                    else:
                        total_errors += 1
                except Exception as e:
                    total_errors += 1
        
        # Salva assunzioni
        medicine_entries = [
            (h0, m0, n0, q0),
            (h1, m1, n1, q1),
            (h2, m2, n2, q2),
            (h3, m3, n3, q3),
            (h4, m4, n4, q4),
        ]
        
        for ora, minuto, nome, qty in medicine_entries:
            # Valida che tutti i campi siano valorizzati e non vuoti/None
            nome_str = str(nome).strip() if nome else ""
            qty_str = str(qty).strip() if qty else ""
            
            if (ora is not None and minuto is not None and nome_str and qty_str):
                try:
                    success = model.create_assunzione(session['email'], meas_date, int(ora), int(minuto), nome_str, qty_str)
                    if success:
                        total_saved += 1
                    else:
                        total_errors += 1
                except Exception as e:
                    print(f"Errore save assunzione: {e}")
                    total_errors += 1
        
        if total_saved > 0 and total_errors == 0:
            return 'Salvati con successo'
        elif total_saved > 0:
            return f'Salvati con successo ({total_saved}/{total_saved + total_errors})'
        else:
            return 'Errore nel salvataggio dei dati.'
        

    # ---- Chat paziente ----------------------------------------------------------ù
    @app.callback(
            Output('p-doc-info', 'children'),
            Output('p-chat-box', 'children'),
            Output('p-chat-input', 'value'),
            Output('p-chat-status', 'children'),
            Input('p-chat-send', 'n_clicks'),
            Input('p-refresh', 'n_intervals'),
            State('p-chat-input', 'value'),
            State('session', 'data'),
    )
    def update_chat(send_n, _, msg_text, session):
        if not session:
            return 'Nessun medico assegnato', html.P('Caricamento...'), '', ''
        
        trigger = ctx.triggered_id
        status = ''
        patient_email = session['email']

        #info medico
        medico = model.get_my_doctor(patient_email)
        doc_info = (html.P(f"Dr.{medico['nome']}", style={'fontWeight': '600', 'fontSize': '15px'})
                    if medico else html.P('Nessun medico assegnato.', style={'color': '#9ca3af'}))

        if not medico:
            return doc_info, html.P('Nessun medico trovato.'), '', ''
        medic_email = medico['email']

        #Invia messaggio
        if trigger == 'p-chat-send' and msg_text:
            try:
                model.invia_messaggio(patient_email, medic_email, msg_text)
                status = '✅ Inviato.'
            except Exception as e:
                status = f'❌ Errore: {str(e)}'

        #Carica conversazione
        msgs = model.get_conversazione(patient_email, medic_email)
        chat = _render_chat_patient(msgs, patient_email)

        new_input = '' if trigger == 'p-chat-send' else no_update
        return doc_info, chat, new_input, status

    # ---- Segnalazioni callback --------------------------------------------------
    @app.callback(
        Output('p-segnalazione-message', 'children'),
        Output('p-segnalazione-title', 'value'),
        Output('p-segnalazione-description', 'value'),
        Output('p-segnalazioni-history', 'children'),
        Input('p-btn-send-segnalazione', 'n_clicks'),
        Input('p-refresh', 'n_intervals'),
        State('p-segnalazione-title', 'value'),
        State('p-segnalazione-description', 'value'),
        State('session', 'data'),
    )
    def handle_segnalazione(send_n, _, title, description, session):
        if not session:
            return no_update, no_update, no_update, no_update
        
        trigger = ctx.triggered_id
        message = ''
        
        # Invia segnalazione
        if trigger == 'p-btn-send-segnalazione' and title and description:
            success = model.create_segnalazione(session['email'], title, description)
            if success:
                message = 'Segnalazione inviata con successo!'
                new_title = ''
                new_description = ''
            else:
                message = 'Errore nell\'invio della segnalazione.'
                new_title = no_update
                new_description = no_update
        else:
            new_title = no_update
            new_description = no_update
        
        # Recupera cronologia segnalazioni
        segnalazioni = model.get_segnalazioni(session['email'])
        if segnalazioni:
            children = []
            for seg in segnalazioni:
                children.append(
                    html.Div([
                        html.Div([
                            html.Strong(seg['titolo'], style={'fontSize': '15px', 'marginBottom': '5px'}),
                            html.Span(f" — {seg['data_ora']}", style={'fontSize': '12px', 'color': '#888', 'marginLeft': '10px'}),
                        ], style={'marginBottom': '5px'}),
                        html.P(seg['descrizione'], style={'margin': '5px 0', 'fontSize': '13px', 'color': '#333'}),
                    ], style={'paddingBottom': '10px', 'marginBottom': '10px', 'borderBottom': '1px solid #e0e0e0'})
                )
            history = html.Div(children)
        else:
            history = html.P('Nessuna segnalazione inviata.', style={'color': '#888', 'fontStyle': 'italic'})
        
        return message, new_title, new_description, history
    
    # Tab Dati giornalieri
    #@app.callback()
