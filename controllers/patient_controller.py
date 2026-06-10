from dash import Output, Input, State, ctx, html, no_update, ALL
import plotly.express as px
from models.model import model
from datetime import date, datetime
from views.patient_view import render_terapie, render_chat_patient, render_storico

SHOW = {'display': 'block'}
HIDE = {'display': 'none'}


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
    
    # ---- Measurements status indicators ------------------------------------------
    measurement_fields = [
        ('breakfast-before', 'pre_colazione'),
        ('breakfast-after', 'post_colazione'),
        ('lunch-before', 'pre_pranzo'),
        ('lunch-after', 'post_pranzo'),
        ('dinner-before', 'pre_cena'),
        ('dinner-after', 'post_cena'),
    ]
    
    def create_meas_callback(field_name, momento_type):
        @app.callback(
            Output(f'p-meas-status-{field_name}', 'children'),
            Output(f'p-meas-status-{field_name}', 'style'),
            Input(f'p-meas-{field_name}', 'value'),
        )
        def update_meas_status(value):
            symbol, color = model.validate_measurement(value, momento_type)
            return symbol, {'fontSize': '18px', 'color': color}
        return update_meas_status
    
    for field_name, momento_type in measurement_fields:
        create_meas_callback(field_name, momento_type)
    
    
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
        Output('p-med-history', 'children'),
        Output('p-med-store', 'data'),
        Output('p-save-message', 'children'),
        Input('p-date-picker', 'date'),
        Input('p-save-daily-data', 'n_clicks'),
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
        State('p-med-store', 'data'),
        State('session', 'data'),
        prevent_initial_call=False,
    )
    def handle_assunzioni(ass_date, n_clicks,
                        bf, af, lf, laf, df, daf,
                        h0, m0, n0, q0, store, session):
        trigger = ctx.triggered_id

        # ---- cambio data: carica storico dal DB ----
        if trigger is None or trigger == 'p-date-picker':
            if not session or not ass_date:
                return None, None, None, None, [], [], no_update
            assunzioni = model.get_assunzioni_by_date(session['email'], ass_date)
            voci = render_storico(assunzioni, session['email'])
            store = [
                {'ora': f"{a['timestamp_hour']:02d}:{a['timestamp_minute']:02d}",
                'farmaco': a['farmaco_nome'],
                'qty': a['quantita_assunta'],
                'unita_misura': a.get('unita_misura', 'N/D')}
                for a in assunzioni
            ]
            return None, None, None, None, voci, store, no_update

        # ---- salva dati ----
        if trigger == 'p-save-daily-data':
            if not session or not ass_date:
                return no_update, no_update, no_update, no_update, no_update, no_update, 'Errore: sessione non valida.'

            total_saved = 0
            total_errors = 0

            # Misurazioni
            for momento, valore in [
                ('pre_colazione', bf), ('post_colazione', af),
                ('pre_pranzo', lf),    ('post_pranzo', laf),
                ('pre_cena', df),      ('post_cena', daf),
            ]:
                if valore is not None:
                    try:
                        if model.create_misurazione(session['email'], ass_date, momento, valore):
                            total_saved += 1
                        else:
                            total_errors += 1
                    except:
                        total_errors += 1

            # Nuova assunzione dalla riga di input
            store = store or []
            nome_str = str(n0).strip() if n0 else ''
            qty_str  = str(q0).strip() if q0 else ''

            if h0 is not None and m0 is not None and nome_str and qty_str:
                try:
                    if model.create_assunzione(session['email'], ass_date,
                                            int(h0), int(m0), nome_str, qty_str):
                        unita = model.get_farmaco_unita_misura(nome_str)
                        store = store + [{'ora': f'{int(h0):02d}:{int(m0):02d}',
                                        'farmaco': nome_str, 'qty': qty_str, 'unita_misura': unita}]
                        total_saved += 1
                    else:
                        total_errors += 1
                except Exception as e:
                    print(f'Errore save assunzione: {e}')
                    total_errors += 1

            voci = render_storico(store, session['email'])
            msg = ('Salvati con successo' if total_saved > 0 and total_errors == 0
                else f'Salvati ({total_saved}/{total_saved + total_errors})' if total_saved > 0
                else 'Errore nel salvataggio.')

            return None, None, None, None, voci, store, msg

        return no_update, no_update, no_update, no_update, no_update, no_update, no_update

    # ---- genera e carica alert -----------------------------------------------
    @app.callback(
        Output('p-alert-badge', 'children'),
        Output('p-alert-badge', 'style'),
        Output('p-alert-panel', 'children'),
        Input('p-refresh', 'n_intervals'),
        State('session', 'data'),
    )
    def refresh_alerts(_, session):
        if not session:
            return '0', {'display': 'none'}, []

        # Genera alert se mancano misurazioni oggi
        model.genera_alert_misurazioni(session['email'])
        model.genera_alert_assunzioni(session['email'])

        alerts = model.get_alert_non_letti(session['email'])
        count = len(alerts)

        badge_style = {
            'background': '#ef4444', 'color': 'white',
            'borderRadius': '50%', 'fontSize': '11px',
            'padding': '1px 6px', 'marginLeft': '4px',
            'fontWeight': '700',
            'display': 'inline' if count > 0 else 'none',
        }

        # Contenuto pannello
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
                        html.Button('✓ Letto', id={'type': 'btn-mark-read', 'index': a['id']},
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


    # ---- apri/chiudi pannello alert ------------------------------------------
    @app.callback(
        Output('p-alert-panel', 'style'),
        Input('p-alert-btn', 'n_clicks'),
        State('p-alert-panel', 'style'),
        prevent_initial_call=True,
    )
    def toggle_alert_panel(n, current_style):
        is_open = current_style.get('display') == 'block'
        return {**current_style, 'display': 'none' if is_open else 'block'}


    # ---- segna alert come letto ----------------------------------------------
    @app.callback(
        Output('p-refresh', 'n_intervals'),
        Input({'type': 'btn-mark-read', 'index': ALL}, 'n_clicks'),
        State('p-refresh', 'n_intervals'),
        prevent_initial_call=True,
    )
    def mark_alert_read(n_clicks_list, current_intervals):
        triggered = ctx.triggered_id
        if not triggered or not any(n for n in n_clicks_list if n):
            return no_update
        model.segna_alert_letto(triggered['index'])
        return (current_intervals or 0) + 1  # forza refresh del badge
        

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
        doc_info = (html.P(f"Dr. {medico['nome']}", style={'fontWeight': '600', 'fontSize': '15px'})
                    if medico else html.P('Nessun medico assegnato.', style={'color': '#9ca3af'}))
        doc_email = (html.P(medico['email'], style={'fontSize': '14px', 'color': '#555'})
                    if medico else html.P(''))

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
        chat = render_chat_patient(msgs, patient_email)

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
                dt = datetime.fromisoformat(seg['data_ora'])
                children.append(
                    html.Div([
                        html.Div([
                            html.Strong(seg['titolo'], style={'fontSize': '15px', 'marginBottom': '5px'}),
                            html.Span(f" — {dt.strftime('%d-%m-%Y %H:%M')}", style={'fontSize': '12px', 'color': '#888', 'marginLeft': '10px'}),
                        ], style={'marginBottom': '5px'}),
                        html.P(seg['descrizione'], style={'margin': '5px 0', 'fontSize': '13px', 'color': '#333'}),
                    ], style={'paddingBottom': '10px', 'marginBottom': '10px', 'borderBottom': '1px solid #e0e0e0'})
                )
            history = html.Div(children)
        else:
            history = html.P('Nessuna segnalazione inviata.', style={'color': '#888', 'fontStyle': 'italic'})
        
        return message, new_title, new_description, history
    
    # ---- Analisi dati callback (6 grafici per i momenti) --------------------------------------------------
    @app.callback(
        Output('p-graph-pre-colazione', 'figure'),
        Output('p-graph-post-colazione', 'figure'),
        Output('p-graph-pre-pranzo', 'figure'),
        Output('p-graph-post-pranzo', 'figure'),
        Output('p-graph-pre-cena', 'figure'),
        Output('p-graph-post-cena', 'figure'),
        Input('p-data-refresh', 'n_intervals'),
        Input('p-analysis-range', 'value'),
        State('session-email', 'data'),
    )
    def update_misurazioni_graphs(_, analysis_range, email):
        if not email:
            # Restituisci 6 grafici vuoti
            empty_fig = px.line(title='Nessun dato')
            return empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig

        momenti = {
            'pre_colazione': 'Pre colazione',
            'post_colazione': 'Post colazione',
            'pre_pranzo': 'Pre pranzo',
            'post_pranzo': 'Post pranzo',
            'pre_cena': 'Pre cena',
            'post_cena': 'Post cena',
        }
        
        figures = []
        for momento_key, momento_label in momenti.items():
            misurazioni = model.get_misurazioni(email, momento_key, analysis_range)
            
            if misurazioni:
                dates = [m['date'] for m in misurazioni]
                values = [m['valore_mg_dl'] for m in misurazioni]
                
                fig = px.line(
                    x=dates,
                    y=values,
                    title=f'Andamento {momento_label}',
                    labels={'x': 'Data', 'y': 'mg/dl'},
                    template='plotly_white',
                    markers=False
                )
                
                # Determina i colori dei marker basati sui valori
                marker_colors = []
                if 'pre_' in momento_key:
                    # Prima dei pasti: 80-130
                    for v in values:
                        if 80 <= v <= 130:
                            marker_colors.append('green')
                        else:
                            marker_colors.append('red')
                else:
                    # Dopo i pasti: sotto 180
                    for v in values:
                        if v <= 180:
                            marker_colors.append('green')
                        else:
                            marker_colors.append('red')
                
                # Aggiungi scatter trace con marker colorati
                fig.add_scatter(
                    x=dates,
                    y=values,
                    mode='markers',
                    marker=dict(
                        size=8,
                        color=marker_colors,
                        line=dict(width=1, color='white')
                    ),
                    hovertemplate='<b>%{x}</b><br>Valore: %{y} mg/dl<extra></extra>',
                    showlegend=False
                )
                
                fig.update_layout(
                    hovermode='x unified',
                    margin=dict(l=50, r=60, t=50, b=60),
                    xaxis_title='Data',
                    yaxis_title='mg/dl',
                    showlegend=False,
                    height=350,
                    plot_bgcolor='#fafafa',
                    paper_bgcolor='white',
                )
                fig.update_xaxes(
                    tickformat='%d/%m', 
                    showticklabels=True,
                    automargin=True,
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='#e5e7eb'
                )
                fig.update_yaxes(
                    showticklabels=True,
                    automargin=True,
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='#e5e7eb',
                    zeroline=False
                )
                
                # Aggiungi linee di riferimento per i valori normali
                if 'pre_' in momento_key:
                    # Prima dei pasti: 80-130
                    fig.add_hline(y=80, line_dash='dash', line_color='gray', annotation_text='Min(80)', annotation_position='right')
                    fig.add_hline(y=130, line_dash='dash', line_color='gray', annotation_text='Max(130)', annotation_position='right')
                else:
                    # Dopo i pasti: sotto 180
                    fig.add_hline(y=180, line_dash='dash', line_color='gray', annotation_text='Max(180)', annotation_position='right')
            else:
                fig = px.line(title=f'Nessun dato per {momento_label}')
                fig.update_layout(template='plotly_white')
            
            figures.append(fig)
        
        return tuple(figures)
    
    # ---- Terapia callback --------------------------------------------------
    @app.callback(
        Output('p-therapy-container', 'children'),
        Output('store-terapie-loaded', 'data'),
        Input('p-refresh', 'n_intervals'),
        State('store-terapie-loaded', 'data'),
        State('session', 'data'),
    )
    def load_terapie(_, already_loaded, session):
        if already_loaded:
            return no_update, no_update
        if not session:
            return (html.P('Nessuna sessione attiva.', style={'color': '#888'}), False)

        terapie = model.get_terapie_paziente(session['email'])

        if not terapie:
            return (html.P('Nessuna terapia prescritta.',
                        style={'color': '#888', 'fontStyle': 'italic'}),
                        True)

        content = render_terapie(terapie)
        return content, True
        