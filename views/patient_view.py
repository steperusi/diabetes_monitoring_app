from dash import html, dcc
from datetime import date
from models.model import Farmaco
from pony.orm import db_session

HEADER = {
    'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center',
    'padding': '16px 16px',
    'background': 'linear-gradient(90deg, #8284D9 0%, #3C3CEC 100%)',
    'color': 'white', 'fontFamily': '"Inter", "Segoe UI", sans-serif',
    'fontSize': '16px', 'fontWeight': '600',
    'borderRadius': '18px',
    'boxShadow': '0 4px 12px rgba(0,0,0,0.12)',
    'minHeight': '70px', 'letterSpacing': '0.3px',
}
CONTAINER = {'maxWidth': '1400px', 'margin': 'auto', 'padding': '15px',
             'fontFamily': 'sans-serif'}
HIDE = {'display': 'none'}
CHAT_BOX = {'height': '300px', 'overflowY': 'auto', 'border': '1px solid #e5e7eb',
            'padding': '12px', 'marginTop': '10px', 'marginBottom': '10px', 'marginTop': '12px',
            'backgroundColor': '#f9fafb', 'borderRadius': '12px'}
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

def patient_header(session):
    name = session['display_name']
    return html.Div([
            html.Img(src='/assets/full_logo.png', alt='Icona', style={'height': '80px', 'borderRadius': '12px'}),
            html.H2('Paziente', style={'margin': '0 15px', 'color': 'white'}),
            html.Div([
                html.Span(name, style={'marginRight': '15px', 'fontWeight': 'bold'}),
                html.Button('Logout', id='btn-logout', n_clicks=0,
                            style={'padding': '6px 16px', 'borderRadius': '8px'}),
            ]),
        ], style=HEADER)

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
            html.Label('Pre colazione:', style={'fontWeight': 'bold', 'marginTop': '10px', 'display': 'inline-block', 'width': '30%'}),
            dcc.Input(id='p-meas-breakfast-before', type='number', 
                        placeholder='Es. 120', 
                        style={'padding': '5px', 'width': '65%'}),
            html.Span(id='p-meas-status-breakfast-before', style={'marginLeft': '8px', 'fontSize': '16px', 'minWidth': '20px'}),
        ], style={'marginBottom': '10px', 'display': 'flex', 'alignItems': 'center', 'gap': '10px'}),
        
        # Post Colazione
        html.Div([
            html.Label('Post colazione:', style={'fontWeight': 'bold', 'marginTop': '10px', 'display': 'inline-block', 'width': '30%'}),
            dcc.Input(id='p-meas-breakfast-after', type='number', 
                        placeholder='Es. 180', 
                        style={'padding': '5px', 'width': '65%'}),
            html.Span(id='p-meas-status-breakfast-after', style={'marginLeft': '8px', 'fontSize': '16px', 'minWidth': '20px'}),
        ], style={'marginBottom': '10px', 'display': 'flex', 'alignItems': 'center', 'gap': '10px'}),
                
        # Pre Pranzo
        html.Div([
            html.Label('Pre pranzo:', style={'fontWeight': 'bold', 'marginTop': '10px', 'display': 'inline-block', 'width': '30%'}),
            dcc.Input(id='p-meas-lunch-before', type='number', 
                        placeholder='Es. 120', 
                        style={'padding': '5px', 'width': '65%'}),
            html.Span(id='p-meas-status-lunch-before', style={'marginLeft': '8px', 'fontSize': '16px', 'minWidth': '20px'}),
        ], style={'marginBottom': '10px', 'display': 'flex', 'alignItems': 'center', 'gap': '10px'}),
                
        # Post Pranzo
        html.Div([
            html.Label('Post pranzo:', style={'fontWeight': 'bold', 'marginTop': '10px', 'display': 'inline-block', 'width': '30%'}),
            dcc.Input(id='p-meas-lunch-after', type='number', 
                        placeholder='Es. 180', 
                        style={'padding': '5px', 'width': '65%'}),
            html.Span(id='p-meas-status-lunch-after', style={'marginLeft': '8px', 'fontSize': '16px', 'minWidth': '20px'}),
        ], style={'marginBottom': '10px', 'display': 'flex', 'alignItems': 'center', 'gap': '10px'}),
                
        # Pre Cena
        html.Div([
            html.Label('Pre cena:', style={'fontWeight': 'bold', 'marginTop': '10px', 'display': 'inline-block', 'width': '30%'}),
            dcc.Input(id='p-meas-dinner-before', type='number', 
                        placeholder='Es. 120', 
                        style={'padding': '5px', 'width': '65%'}),
            html.Span(id='p-meas-status-dinner-before', style={'marginLeft': '8px', 'fontSize': '16px', 'minWidth': '20px'}),
        ], style={'marginBottom': '10px', 'display': 'flex', 'alignItems': 'center', 'gap': '10px'}),
                
        # Post Cena
        html.Div([
            html.Label('Post cena:', style={'fontWeight': 'bold', 'marginTop': '10px', 'display': 'inline-block', 'width': '30%'}),
            dcc.Input(id='p-meas-dinner-after', type='number', 
                        placeholder='Es. 180', 
                        style={'padding': '5px', 'width': '65%'}),
            html.Span(id='p-meas-status-dinner-after', style={'marginLeft': '8px', 'fontSize': '16px', 'minWidth': '20px'}),
        ], style={'marginBottom': '10px', 'display': 'flex', 'alignItems': 'center', 'gap': '10px'}),
    ], style={'border': '1px solid #ddd', 'padding': '15px', 'borderRadius': '4px', 'flex': '1', 'marginRight': '15px'})

@db_session
def daily_medicine_assumptions():
    return html.Div([
        html.H4('Assunzione farmaci'),
        html.P('Registra i farmaci assunti oggi:', 
                style={'fontSize': '14px', 'color': '#666'}),
        
        # Header row
        html.Div([
            html.Div('Ora', style={'fontWeight': 'bold', 'flex': '0 0 25%', 'textAlign': 'center'}),
            html.Div('Farmaco', style={'fontWeight': 'bold', 'flex': '0 0 52.5%', 'textAlign': 'center'}),
            html.Div('Quantità', style={'fontWeight': 'bold', 'flex': '0 0 12.5%', 'textAlign': 'center'}),
            html.Div('Stato', style={'fontWeight': 'bold', 'flex': '0 0 10%', 'textAlign': 'center'}),
        ], style={'display': 'flex', 'gap': '3px', 'marginBottom': '10px', 'paddingBottom': '10px', 'borderBottom': '2px solid #ddd'}),
        
        # Medicine entries (placeholder for 5 rows)
        html.Div([
            html.Div([
                html.Div([
                    dcc.Input(id=f'p-med-hour-{i}', type='number', min=0, max=23, step=1, placeholder='HH',
                        style={'width': '45px', 'padding': '5px', 'textAlign': 'center', 'border': '1px solid #ddd', 'borderRadius': '4px'}),
                    html.Span(':',
                        style={'padding': '0 4px', 'fontWeight': 'bold', 'fontSize': '18px'}),
                    dcc.Input(id=f'p-med-minute-{i}', type='number', min=0, max=59, step=1, placeholder='MM',
                        style={'width': '45px', 'padding': '5px', 'textAlign': 'center', 'border': '1px solid #ddd', 'borderRadius': '4px'}),
                ], style={'display': 'flex', 'alignItems': 'center', 'flex': '0 0 25%', 'justifyContent': 'center', 'gap': '2px'}),
                html.Div([
                    dcc.Dropdown(
                        id=f'p-med-name-{i}',
                        options=[{'label': f.nome, 'value': f.nome} for f in Farmaco.select()],
                        placeholder='Seleziona',
                        style={'padding': '5px', 'width': '100%', 'boxSizing': 'border-box', 'fontSize': '13px'}
                    )
                ], style={'flex': '0 0 52.5%', 'paddingX': '2px'}),
                html.Div([
                    dcc.Input(id=f'p-med-qty-{i}', type='text', placeholder='Es. 100',
                        style={'padding': '5px', 'width': '100%', 'boxSizing': 'border-box', 'border': '1px solid #ddd', 'borderRadius': '4px'})
                ], style={'flex': '0 0 12.5%', 'paddingX': '2px'}),
                html.Div([
                    html.Span(id=f'p-med-status-{i}', style={'fontSize': '18px', 'width': '100%', 'textAlign': 'center'})
                ], style={'flex': '0 0 10%', 'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'}),
            ], style={'display': 'flex', 'gap': '3px', 'marginBottom': '8px', 'alignItems': 'center'})
            for i in range(5)
        ], style={'maxHeight': '200px', 'overflowY': 'auto'}),
    ], style={'border': '1px solid #ddd', 'padding': '15px', 'borderRadius': '4px', 'flex': '1'})

def daily_data():
    return html.Div(id='p-tab-health', children=[
        html.H4('Registra i tuoi dati giornalieri'),
                
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
        ], style={'display': 'flex', 'gap': '15px', 'marginBottom': '20px'}),
                
        # Submit button for misurazioni and assunzioni
        html.Div([
            html.Button('Salva dati', id='p-save-daily-data', n_clicks=0,
                       style={'padding': '10px 30px', 'backgroundColor': '#0066cc', 'color': 'white',
                             'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer', 'fontSize': '16px'}),
            html.Span(id='p-save-message', style={'marginLeft': '15px', 'color': 'green'}),
        ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '30px'}),
                
        # Segnalazioni section
        html.Div([
            html.H4('Segnalazioni'),
            html.P('Se necessario, segnala qualcosa al tuo medico:', 
                   style={'fontSize': '14px', 'color': '#666'}),
                    
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
        html.H4('Analisi dati dell\'ultimo mese'),
        html.P('Andamento delle tue misurazioni per ogni momento della giornata:', 
                style={'fontSize': '14px', 'color': '#666', 'marginBottom': '20px'}),
        
        # Grid di 6 grafici (2 colonne, 3 righe)
        html.Div([
            # Riga 1
            html.Div([
                html.Div([
                    dcc.Graph(id='p-graph-pre-colazione')
                ], style={'flex': '1', 'marginRight': '10px'}),
                html.Div([
                    dcc.Graph(id='p-graph-post-colazione')
                ], style={'flex': '1', 'marginLeft': '10px'}),
            ], style={'display': 'flex', 'marginBottom': '20px', 'height': '250px'}),
            
            # Riga 2
            html.Div([
                html.Div([
                    dcc.Graph(id='p-graph-pre-pranzo')
                ], style={'flex': '1', 'marginRight': '10px'}),
                html.Div([
                    dcc.Graph(id='p-graph-post-pranzo')
                ], style={'flex': '1', 'marginLeft': '10px'}),
            ], style={'display': 'flex', 'marginBottom': '20px', 'height': '250px'}),
            
            # Riga 3
            html.Div([
                html.Div([
                    dcc.Graph(id='p-graph-pre-cena')
                ], style={'flex': '1', 'marginRight': '10px'}),
                html.Div([
                    dcc.Graph(id='p-graph-post-cena')
                ], style={'flex': '1', 'marginLeft': '10px'}),
            ], style={'display': 'flex', 'height': '250px'}),
        ], style={'display': 'flex', 'flexDirection': 'column'}),
        
        # Refresh interval
        dcc.Interval(id='p-data-refresh', interval=5000),
    ])

def medic_and_chat():
    return html.Div(id='p-tab-doctor', style=HIDE, children=[
        html.Div([
            html.Div('Il tuo Medico', style=SECTION_TITLE),
            html.Div(id='p-doc-info', style = SECTION_SUBTITLE),
            html.Div(id='p-doc-email', style = SECTION_SUBTITLE),
        ]),
        html.Div([
            html.Div('Messaggi', style=SECTION_TITLE),
            html.Div('Scrivi al tuo medico.', style=SECTION_SUBTITLE),
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
        html.H4('La tua terapia'),
        html.Div(id='p-therapy-container', children=[
            html.P('Caricamento terapie...', style={'color': '#888'}),
        ]),
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

            # Refresh interval
            dcc.Interval(id='p-refresh', interval=5000),
            # Store email in session storage for callbacks
            dcc.Store(id='session-email', storage_type='session', data=session['email']),
        ], style=CONTAINER),
    ])