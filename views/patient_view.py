from dash import html, dcc
from datetime import date
from models.model import model, Farmaco
from pony.orm import db_session

HEADER = {
    'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center',
    'padding': '16px 32px',
    'background': 'linear-gradient(to bottom, #2E1F5E 0%, #6A5ACD 100%)',
    'color': 'white', 'fontFamily': '"Inter", "Segoe UI", sans-serif',
    'fontSize': '16px', 'fontWeight': '600',
    'borderRadius': '18px',
    'boxShadow': '0 4px 12px rgba(0,0,0,0.12)',
    'minHeight': '70px', 'letterSpacing': '0.3px',
}
CONTAINER = {'maxWidth': '960px', 'margin': 'auto', 'padding': '15px',
             'fontFamily': '"Inter", "Segoe UI", sans-serif', 'color': '#1f2937',
            }
HIDE = {'display': 'none'}
CHAT_BOX = {'height': '300px', 'overflowY': 'auto', 'border': '1px solid #e5e7eb',
            'padding': '12px', 'marginTop': '10px', 'marginBottom': '10px', 'marginTop': '12px',
            'backgroundColor': '#f9fafb', 'borderRadius': '12px'
            }
SECTION_TITLE = {
    'fontSize': '18px', 'fontWeight': '700',
    'color': '#4748AC', 'marginBottom': '4px',
}
SECTION_SUBTITLE = {
    'fontSize': '13px', 'color': '#9ca3af', 'marginBottom': '16px',
}
CARD = {
    'background': '#ffffff', 'borderRadius': '16px',
    'padding': '24px', 'marginTop': '20px',
    'boxShadow': '0 4px 12px rgba(0,0,0,0.07)',
    'border': '1px solid #e5e7eb',
}
BTN_PRIMARY = {
    'background': 'linear-gradient(90deg, #4748AC 0%, #5E60CE 100%)',
    'color': 'white', 'border': 'none', 'borderRadius': '10px',
    'padding': '10px 28px', 'fontWeight': '600', 'fontSize': '14px',
    'cursor': 'pointer',
}
INPUT_STYLE = {
    'width': '100%', 'padding': '10px 14px',
    'border': '1px solid #d1d5db', 'borderRadius': '10px',
    'fontSize': '14px', 'color': '#1f2937',
    'outline': 'none', 'boxSizing': 'border-box',
    'marginBottom': '14px',
}

#--- Funzioni Helper ------

#per riordinare scheda assunzioni da tab terapia
def _fascia_ordine(fascia: str) -> int:
    fascia = fascia.lower()
    if 'colazione' in fascia:
        return 0
    elif 'pranzo' in fascia:
        return 1
    elif 'cena' in fascia:
        return 2
    return 3

def render_chat_patient(msgs: list, my_email: str) -> html.Div:
    """Renderizza la chat del paziente con il proprio medico."""
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


def render_storico(entries: list) -> list:
    """Renderizza lo storico assunzioni del paziente."""
    if not entries:
        return []
    return [
        html.Div([
            html.Span(
                v['ora'] if isinstance(v, dict) and 'ora' in v
                else f"{v['timestamp_hour']:02d}:{v['timestamp_minute']:02d}",
                style={'fontSize': '13px', 'fontWeight': '500',
                       'flex': '0 0 25%', 'textAlign': 'center', 'color': '#1f2937'}
            ),
            html.Span(
                v['farmaco'] if isinstance(v, dict) and 'farmaco' in v else v['farmaco_nome'],
                style={'fontSize': '13px', 'flex': '1', 'color': '#1f2937'}
            ),
            html.Span(
                f"{v['qty'] if 'qty' in v else v['quantita_assunta']} cp",
                style={'fontSize': '12px', 'color': '#6b7280',
                       'background': '#f3f4f6', 'border': '1px solid #e5e7eb',
                       'borderRadius': '20px', 'padding': '2px 10px',
                       'flex': '0 0 70px', 'textAlign': 'center'}
            ),
        ], style={
            'display': 'flex', 'alignItems': 'center', 'gap': '8px',
            'padding': '6px 4px', 'borderBottom': '1px solid #f3f4f6',
        })
        for v in entries
    ]


def render_terapie(terapie):
    return html.Div([
        html.Div([
            html.Div([
                html.Span(f"Dal {t['data_inizio']} al {t['data_fine']}",
                        style={'fontSize': '13px', 'color': '#6b7280'}),
                html.Span(f" — {t['indicazioni']}",
                        style={'fontSize': '13px', 'color': '#9ca3af', 'fontStyle': 'italic'}),
            ], style={'marginBottom': '10px'}),

            html.Div([
                html.Div([
                    html.Span(a['orario'], style={
                        'fontWeight': '600', 'fontSize': '13px',
                        'color': '#4748AC', 'minWidth': '80px', 'display': 'inline-block',
                    }),
                    html.Span(a['farmaco'], style={'fontSize': '13px', 'marginRight': '8px'}),
                    html.Span(f"{a['quantita']} {a['unita_misura']}", style={'fontSize': '13px', 'color': '#6b7280'}),
                ], style={
                    'padding': '6px 10px',
                    'background': '#f9fafb' if i % 2 == 0 else '#ffffff',
                    'borderRadius': '6px', 'marginBottom': '4px',
                })
                for i, a in enumerate(sorted(t['assunzioni'], key=lambda x: _fascia_ordine(x['orario'])))
            ]) if t['assunzioni'] else html.P('Nessuna assunzione registrata.',
                                              style={'color': '#9ca3af', 'fontSize': '13px'}),

        ], style={
            'border': '1px solid #e5e7eb', 'padding': '16px',
            'borderRadius': '10px', 'marginBottom': '12px',
            'backgroundColor': '#ffffff',
        })
        for t in terapie
    ])
    

def patient_header(session):
    name = session['display_name']
    return html.Div([
        html.Img(src='/assets/full_logo.png', alt='Logo',
                 style={'height': '50px', 'borderRadius': '8px', 'marginRight': '16px'}),
        html.H2('Paziente', style={'margin': '0', 'color': 'white'}),
        html.Div([
            html.Span(name, style={'marginRight': '15px', 'fontWeight': 'bold'}),
            html.Div([
                html.Button(
                    ['🔔', html.Span('0', id='p-alert-badge', style={
                        'background': '#ef4444', 'color': 'white',
                        'borderRadius': '50%', 'fontSize': '11px',
                        'padding': '1px 6px', 'marginLeft': '4px',
                        'fontWeight': '700', 'display': 'none',
                    })],
                    id='p-alert-btn', n_clicks=0,
                    style={'background': 'none', 'border': '1px solid white',
                           'borderRadius': '8px', 'color': 'white',
                           'padding': '6px 12px', 'cursor': 'pointer',
                           'fontSize': '16px', 'marginRight': '10px'},
                ),
                html.Div(id='p-alert-panel', style={
                    'display': 'none', 'position': 'absolute', 'right': '160px',
                    'top': '70px', 'zIndex': '1000', 'width': '340px',
                    'background': 'white', 'borderRadius': '12px',
                    'boxShadow': '0 8px 24px rgba(0,0,0,0.15)',
                    'border': '1px solid #e5e7eb', 'overflow': 'hidden',
                }),
            ], style={'position': 'relative'}),
            html.Button('Logout', id='btn-logout', n_clicks=0,
                        style={'padding': '6px 16px', 'borderRadius': '8px'}),
        ], style={'display': 'flex', 'alignItems': 'center'}),
    ], style={**HEADER, 'position': 'relative'})

def navigation_tabs():
    return dcc.Tabs(id='p-main-tabs', value='health', children=[
        dcc.Tab(label='Dati giornalieri', value='health'),
        dcc.Tab(label='Analisi dati', value='data'),
        dcc.Tab(label='Medico + Chat', value='doctor'),
        dcc.Tab(label='Terapia', value='therapy'),
    ])

def daily_measurements():
    return html.Div([
        html.H4('Misurazioni giornaliere'),
        html.P('Inserisci le tue misurazioni prima e dopo ogni pasto:', 
                style={'fontSize': '14px', 'color': '#666'}),
                
        # Pre Colazione
        html.Div([
            html.Label('Pre colazione:', style={'fontWeight': 'bold', 'marginTop': '10px', 'display': 'inline-block', 'width': '35%'}),
            dcc.Input(id='p-meas-breakfast-before', type='number', 
                        placeholder='Es. 120', 
                        style={'padding': '5px', 'width': '45%'}),
            html.Span(id='p-meas-status-breakfast-before', style={'marginLeft': '8px', 'fontSize': '16px', 'minWidth': '20px'}),
        ], style={'marginBottom': '10px', 'display': 'flex', 'alignItems': 'center', 'gap': '10px'}),
        
        # Post Colazione
        html.Div([
            html.Label('Post colazione:', style={'fontWeight': 'bold', 'marginTop': '10px', 'display': 'inline-block', 'width': '35%'}),
            dcc.Input(id='p-meas-breakfast-after', type='number', 
                        placeholder='Es. 180', 
                        style={'padding': '5px', 'width': '45%'}),
            html.Span(id='p-meas-status-breakfast-after', style={'marginLeft': '8px', 'fontSize': '16px', 'minWidth': '20px'}),
        ], style={'marginBottom': '10px', 'display': 'flex', 'alignItems': 'center', 'gap': '10px'}),
                
        # Pre Pranzo
        html.Div([
            html.Label('Pre pranzo:', style={'fontWeight': 'bold', 'marginTop': '10px', 'display': 'inline-block', 'width': '35%'}),
            dcc.Input(id='p-meas-lunch-before', type='number', 
                        placeholder='Es. 120', 
                        style={'padding': '5px', 'width': '45%'}),
            html.Span(id='p-meas-status-lunch-before', style={'marginLeft': '8px', 'fontSize': '16px', 'minWidth': '20px'}),
        ], style={'marginBottom': '10px', 'display': 'flex', 'alignItems': 'center', 'gap': '10px'}),
                
        # Post Pranzo
        html.Div([
            html.Label('Post pranzo:', style={'fontWeight': 'bold', 'marginTop': '10px', 'display': 'inline-block', 'width': '35%'}),
            dcc.Input(id='p-meas-lunch-after', type='number', 
                        placeholder='Es. 180', 
                        style={'padding': '5px', 'width': '45%'}),
            html.Span(id='p-meas-status-lunch-after', style={'marginLeft': '8px', 'fontSize': '16px', 'minWidth': '20px'}),
        ], style={'marginBottom': '10px', 'display': 'flex', 'alignItems': 'center', 'gap': '10px'}),
                
        # Pre Cena
        html.Div([
            html.Label('Pre cena:', style={'fontWeight': 'bold', 'marginTop': '10px', 'display': 'inline-block', 'width': '35%'}),
            dcc.Input(id='p-meas-dinner-before', type='number', 
                        placeholder='Es. 120', 
                        style={'padding': '5px', 'width': '45%'}),
            html.Span(id='p-meas-status-dinner-before', style={'marginLeft': '8px', 'fontSize': '16px', 'minWidth': '20px'}),
        ], style={'marginBottom': '10px', 'display': 'flex', 'alignItems': 'center', 'gap': '10px'}),
                
        # Post Cena
        html.Div([
            html.Label('Post cena:', style={'fontWeight': 'bold', 'marginTop': '10px', 'display': 'inline-block', 'width': '35%'}),
            dcc.Input(id='p-meas-dinner-after', type='number', 
                        placeholder='Es. 180', 
                        style={'padding': '5px', 'width': '45%'}),
            html.Span(id='p-meas-status-dinner-after', style={'marginLeft': '8px', 'fontSize': '16px', 'minWidth': '20px'}),
        ], style={'marginBottom': '10px', 'display': 'flex', 'alignItems': 'center', 'gap': '10px'}),
    ], style={'border': '1px solid #ddd', 'padding': '15px', 'borderRadius': '4px', 'flex': '0 0 40%', 'minWidth': '0'})

def daily_medicine_assumptions():
    farmaci = [f['value'] for f in model.get_tutti_farmaci()]
    return html.Div([
        html.H4('Assunzione farmaci'),
        html.P('Registra i farmaci assunti oggi:',
               style={'fontSize': '14px', 'color': '#666'}),


        # Header colonne
        html.Div([
            html.Div('Ora',      style={'fontWeight': 'bold', 'flex': '0 0 25%', 'textAlign': 'center', 'fontSize': '13px'}),
            html.Div('Farmaco',  style={'fontWeight': 'bold', 'flex': '1',       'textAlign': 'center', 'fontSize': '13px'}),
            html.Div('Quantità', style={'fontWeight': 'bold', 'flex': '0 0 80px','textAlign': 'center', 'fontSize': '13px'}),
        ], style={
            'display': 'flex', 'gap': '8px',
            'paddingBottom': '6px', 'borderBottom': '1px solid #e5e7eb',
            'marginBottom': '8px',
        }),

        # Riga di input singola
        html.Div([
            # Ora HH:MM
            html.Div([
                dcc.Input(
                    id='p-med-hour-0', type='number',
                    min=0, max=23, step=1, placeholder='HH',
                    style={'width': '45px', 'padding': '5px',
                           'textAlign': 'center', 'border': '1px solid #ddd',
                           'borderRadius': '4px'}
                ),
                html.Span(':', style={'padding': '0 4px', 'fontWeight': 'bold', 'fontSize': '18px'}),
                dcc.Input(
                    id='p-med-minute-0', type='number',
                    min=0, max=59, step=1, placeholder='MM',
                    style={'width': '45px', 'padding': '5px',
                           'textAlign': 'center', 'border': '1px solid #ddd',
                           'borderRadius': '4px'}
                ),
            ], style={'display': 'flex', 'alignItems': 'center',
                      'gap': '2px', 'flex': '0 0 25%', 'justifyContent': 'center'}),

            # Farmaco
            html.Div([
                dcc.Dropdown(
                    id='p-med-name-0',
                    options=farmaci,
                    placeholder='Seleziona farmaco',
                    style={'fontSize': '13px'}
                ),
            ], style={'flex': '1'}),

            # Quantità
            dcc.Input(
                id='p-med-qty-0', type='text', placeholder='Es. 1',
                style={'width': '70px', 'padding': '5px',
                       'border': '1px solid #ddd', 'borderRadius': '4px',
                       'textAlign': 'center', 'flex': '0 0 70px'}
            ),
        ], style={
            'display': 'flex', 'alignItems': 'center',
            'gap': '8px',
        }),
        
        # Storico assunzioni (sotto la riga di input)
        html.Div(
            id='p-med-history',
            children=[],
            style={'marginBottom': '8px'},
        ),

        # Store per tenere le assunzioni in memoria
        dcc.Store(id='p-med-store', data=[]),

    ], style={
        'border': '1px solid #ddd', 'padding': '15px',
        'borderRadius': '4px', 'flex': '1',
        'minWidth': '0', 'maxWidth': '100%', 'boxSizing': 'border-box',
    })

def daily_data():
    return html.Div(id='p-tab-health', children=[
        html.H4('Registra i tuoi dati giornalieri', style=SECTION_TITLE),
                
        # Date selection
        html.Div([
            html.Label('Seleziona data:', style={'fontWeight': 'bold', 'marginRight': '10px'}),
            dcc.DatePickerSingle(id='p-date-picker', 
                                date=date.today(),
                                display_format='DD/MM/YYYY'),
        ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '20px'}),
                
        # Measurements and Medicines side-by-side
        html.Div([
            daily_measurements(),
            daily_medicine_assumptions(),
        ], style={'background': '#ffffff', 'borderRadius': '16px', 'padding': '24px', 
        'marginTop': '20px', 'boxShadow': '0 4px 12px rgba(0,0,0,0.07)',
        'border': '1px solid #e5e7eb', 'display': 'flex', 'gap': '15px', 
        'marginBottom': '20px', 'boxSizing': 'border-box'}),
                
        # Submit button for misurazioni and assunzioni
        html.Div([
            html.Button('Salva dati', id='p-save-daily-data', n_clicks=0,
                       style=BTN_PRIMARY),
            html.Span(id='p-save-message', style={'marginLeft': '15px', 'color': 'green'}),
        ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '30px'}),
                
        # Segnalazioni section
        html.Div([
            html.H4('Segnalazioni'),
            html.P('Se necessario, segnala qualcosa al tuo medico:', style={'fontSize': '14px', 'color': '#666'}),
                    
            # Segnalazione form
            html.Div([
                html.Div([
                    html.Label('Titolo:', style={'fontWeight': 'bold', 'display': 'block', 'marginBottom': '5px'}),
                    dcc.Input(id='p-segnalazione-title', type='text', 
                             placeholder='Es. Mal di testa persistente',
                             style={'padding': '8px', 'width': '100%', 'boxSizing': 'border-box',
                                   'border': '1px solid #ddd', 'borderRadius': '4px'}),
                ], style={'marginBottom': '15px'}),
                        
                html.Div([
                    html.Label('Descrizione:', style={'fontWeight': 'bold', 'display': 'block', 'marginBottom': '5px'}),
                    dcc.Textarea(id='p-segnalazione-description',
                                placeholder='Descrivi il problema in dettaglio...',
                                style={'padding': '8px', 'width': '100%', 'boxSizing': 'border-box',
                                      'border': '1px solid #ddd', 'borderRadius': '4px',
                                      'minHeight': '100px', 'fontFamily': 'sans-serif', 'fontSize': '14px'}),
                ], style={'marginBottom': '15px'}),
                        
                html.Div([
                    html.Button('Invia segnalazione', id='p-btn-send-segnalazione', n_clicks=0,
                               style={'padding': '10px 30px', 'backgroundColor': '#28a745', 'color': 'white',
                                     'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer', 'fontSize': '16px'}),
                    html.Span(id='p-segnalazione-message', style={'marginLeft': '15px', 'color': 'green'}),
                ], style={'display': 'flex', 'alignItems': 'center'}),
            ], style={'border': '1px solid #ddd', 'padding': '15px', 'borderRadius': '4px', 'backgroundColor': '#f9f9f9', 'marginBottom': '20px'}),
                    
            # Segnalazioni sent history
            html.Div([
                html.H5('Segnalazioni inviate'),
                html.Div(id='p-segnalazioni-history', children=[
                    html.P('Nessuna segnalazione inviata.', style={'color': '#888', 'fontStyle': 'italic'}),
                ], style={'border': '1px solid #e0e0e0', 'padding': '15px', 'borderRadius': '4px',
                         'backgroundColor': '#fafafa', 'maxHeight': '300px', 'overflowY': 'auto'}),
            ]),
        ], style={'border': '1px solid #ddd', 'padding': '15px', 'borderRadius': '4px', 'marginTop': '20px'}),
    ])

def data_analysis():
    return html.Div(id='p-tab-data', style=HIDE, children=[
        html.Div([
            html.Label('Seleziona intervallo analisi:', style={'fontWeight': 'bold', 'marginRight': '10px'}),
            dcc.Dropdown(
                id='p-analysis-range',
                options=[
                    {'label': 'Ultima settimana', 'value': 'week'},
                    {'label': 'Ultimo mese', 'value': 'month'},
                ],
                value='month',
                clearable=False,
                style={'width': '250px'}
            )], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '20px', 'margin-top': '20px'}),

        html.P('Andamento delle tue misurazioni per ogni momento della giornata:', 
                style={'fontSize': '14px', 'color': '#666'}),
        
        
        # Grid di 6 grafici (2 colonne, 3 righe)
        html.Div([
            # Riga 1
            html.Div([
                html.Div([
                    dcc.Graph(id='p-graph-pre-colazione')
                ], style={'background': '#ffffff', 'borderRadius': '12px', 'padding': '12px', 'border': '1px solid #e5e7eb',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.05)', 'flex': '1', 'marginRight': '5px', 'minWidth': '0', 'overflow': 'hidden'}),
                html.Div([
                    dcc.Graph(id='p-graph-post-colazione')
                ], style={'background': '#ffffff', 'borderRadius': '12px', 'padding': '12px', 'border': '1px solid #e5e7eb',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.05)', 'flex': '1', 'marginRight': '5px', 'minWidth': '0', 'overflow': 'hidden'}),
            ], style={'display': 'flex', 'marginBottom': '20px', 'height': '250px'}),
            
            # Riga 2
            html.Div([
                html.Div([
                    dcc.Graph(id='p-graph-pre-pranzo')
                ], style={'background': '#ffffff', 'borderRadius': '12px', 'padding': '12px', 'border': '1px solid #e5e7eb',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.05)', 'flex': '1', 'marginRight': '5px', 'minWidth': '0', 'overflow': 'hidden'}),
                html.Div([
                    dcc.Graph(id='p-graph-post-pranzo')
                ], style={'background': '#ffffff', 'borderRadius': '12px', 'padding': '12px', 'border': '1px solid #e5e7eb',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.05)', 'flex': '1', 'marginLeft': '5px', 'minWidth': '0', 'overflow': 'hidden'}),
            ], style={'display': 'flex', 'marginBottom': '20px', 'height': '250px'}),
            
            # Riga 3
            html.Div([
                html.Div([
                    dcc.Graph(id='p-graph-pre-cena')
                ], style={'background': '#ffffff', 'borderRadius': '12px', 'padding': '12px', 'border': '1px solid #e5e7eb',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.05)', 'flex': '1', 'marginRight': '5px', 'minWidth': '0', 'overflow': 'hidden'}),
                html.Div([
                    dcc.Graph(id='p-graph-post-cena')
                ], style={'background': '#ffffff', 'borderRadius': '12px', 'padding': '12px', 'border': '1px solid #e5e7eb',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.05)', 'flex': '1', 'marginRight': '5px', 'minWidth': '0', 'overflow': 'hidden'}),
            ], style={'display': 'flex', 'height': '250px'}),
        ], style={'display': 'flex', 'flexDirection': 'column'}),
        
        # Refresh interval
        dcc.Interval(id='p-data-refresh', interval=5000),
    ])

def medic_and_chat():
    return html.Div(id='p-tab-doctor', style=HIDE, children=[
        html.Div([
            html.Div('Messaggi', style=SECTION_TITLE),
            html.Div('Scrivi al tuo medico.', style=SECTION_SUBTITLE),
            html.Div(id='p-doc-info', style = SECTION_SUBTITLE),
            html.Div(id='p-doc-email', style = SECTION_SUBTITLE),
            html.Div(id='p-chat-box', style=CHAT_BOX),
            html.Div([
                dcc.Input(id='p-chat-input', type='text',
                            placeholder='Scrivi un messaggio...',
                            style={**INPUT_STYLE, 'width': '75%',
                                    'display': 'inline-block', 'marginBottom':'0',
                                    'marginRight': '8px'}),
                html.Button('Invia', id='p-chat-send', n_clicks=0, style=BTN_PRIMARY),
            ], style={'display': 'flex', 'alignItems': 'center'}),
            html.Div(id='p-chat-status',
                        style={'color': '#16a34a', 'marginTop': '6px', 'fontSize': '13px'}),
        ], style=CARD)
    ])
    
    


def therapy():
    return html.Div(id='p-tab-therapy', style=HIDE, children=[
        html.Div([
            html.H1('La tua terapia', style=SECTION_TITLE),
            html.Div(id='p-therapy-container', children=[
            html.P('Caricamento terapie...', style={'color': '#888'}),
        ]),
        dcc.Store(id='store-terapie-loaded', data=False),
        ], style=CARD)
    ])

def patient_layout(session):

    return html.Div([
        # Header
        patient_header(session),

        # Main
        html.Div([
            # Pages navigation tabs
            navigation_tabs(),


            # Tab Dati giornalieri
            daily_data(),

            # Tab Analisi dati
            data_analysis(),

            # Tab Medico + Chat
            medic_and_chat(),

            # Tab Terapia
            therapy(),

            # Store per email utente
            dcc.Store(id='session-email', data=session['email']),

            # Refresh interval
            dcc.Interval(id='p-refresh', interval=5000),
        ], style=CONTAINER),
    ])


# ── Helpers rendering ──────────────────────────────────────────────────────────

def render_chat_patient(msgs: list, my_email: str) -> html.Div:
    """Render della chat lato paziente."""
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


def render_storico(entries: list) -> list:
    """Render dello storico assunzioni giornaliere."""
    if not entries:
        return []
    return [
        html.Div([
            html.Span(
                v['ora'] if isinstance(v, dict) and 'ora' in v
                else f"{v['timestamp_hour']:02d}:{v['timestamp_minute']:02d}",
                style={'fontSize': '13px', 'fontWeight': '500',
                       'flex': '0 0 25%', 'textAlign': 'center', 'color': '#1f2937'}
            ),
            html.Span(
                v['farmaco'] if isinstance(v, dict) and 'farmaco' in v else v['farmaco_nome'],
                style={'fontSize': '13px', 'flex': '1', 'color': '#1f2937'}
            ),
            html.Span(
                f"{v['qty'] if 'qty' in v else v['quantita_assunta']} cp",
                style={'fontSize': '12px', 'color': '#6b7280',
                       'background': '#f3f4f6', 'border': '1px solid #e5e7eb',
                       'borderRadius': '20px', 'padding': '2px 10px',
                       'flex': '0 0 70px', 'textAlign': 'center'}
            ),
        ], style={
            'display': 'flex', 'alignItems': 'center', 'gap': '8px',
            'padding': '6px 4px', 'borderBottom': '1px solid #f3f4f6',
        })
        for v in entries
    ]