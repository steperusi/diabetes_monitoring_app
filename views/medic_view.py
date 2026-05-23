"""View del medico."""

from dash import html, dcc
from models.model import model, Paziente, Medico, Terapia, Utente, FarmacoEnum
from pony.orm import db_session, select

# ── Stili ─────────────────────────────────────────────────────────────────────
HEADER = {
    'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center',
    'padding': '16px 32px',
    'background': 'linear-gradient(90deg, #8284D9 0%, #3C3CEC 100%)',
    'color': 'white', 'fontFamily': '"Inter", "Segoe UI", sans-serif',
    'fontSize': '16px', 'fontWeight': '600',
    'borderRadius': '18px',
    'boxShadow': '0 4px 12px rgba(0,0,0,0.12)',
    'minHeight': '70px', 'letterSpacing': '0.3px',
}
CONTAINER = {
    'maxWidth': '960px', 'margin': '30px auto', 'padding': '24px',
    'fontFamily': '"Inter", "Segoe UI", sans-serif', 'color': '#1f2937',
}
CARD = {
    'background': '#ffffff', 'borderRadius': '16px',
    'padding': '24px', 'marginTop': '20px',
    'boxShadow': '0 4px 12px rgba(0,0,0,0.07)',
    'border': '1px solid #e5e7eb',
}
TABLE_HEADER = {
    'background': 'linear-gradient(90deg, #4748AC 0%, #5E60CE 100%)',
    'color': 'white', 'padding': '10px 16px', 'fontWeight': '600',
    'fontSize': '13px', 'letterSpacing': '0.5px', 'overflow': 'auto',
}
TABLE_ROW_EVEN = {
    'background': '#f9fafb', 'padding': '10px 16px',
    'fontSize': '14px', 'color': '#374151',
}
TABLE_ROW_ODD = {
    'background': '#ffffff', 'padding': '10px 16px',
    'fontSize': '14px', 'color': '#374151',
}
INPUT_STYLE = {
    'width': '100%', 'padding': '10px 14px',
    'border': '1px solid #d1d5db', 'borderRadius': '10px',
    'fontSize': '14px', 'color': '#1f2937',
    'outline': 'none', 'boxSizing': 'border-box',
    'marginBottom': '14px',
}
SECTION_TITLE = {
    'fontSize': '18px', 'fontWeight': '700',
    'color': '#4748AC', 'marginBottom': '4px',
}
SECTION_SUBTITLE = {
    'fontSize': '13px', 'color': '#9ca3af', 'marginBottom': '16px',
}
BADGE_SI = {
    'background': '#fee2e2', 'color': '#991b1b',
    'borderRadius': '6px', 'padding': '2px 10px',
    'fontSize': '12px', 'fontWeight': '600',
}
BADGE_NO = {
    'background': '#f0fdf4', 'color': '#166534',
    'borderRadius': '6px', 'padding': '2px 10px',
    'fontSize': '12px', 'fontWeight': '600',
}
BTN_PRIMARY = {
    'background': 'linear-gradient(90deg, #4748AC 0%, #5E60CE 100%)',
    'color': 'white', 'border': 'none', 'borderRadius': '10px',
    'padding': '10px 28px', 'fontWeight': '600', 'fontSize': '14px',
    'cursor': 'pointer', 'marginTop': '8px',
}
LABEL_STYLE = {
    'fontWeight': '600', 'fontSize': '13px',
    'color': '#6b7280', 'marginBottom': '4px',
    'display': 'block', 'letterSpacing': '0.4px',
}


# ── Helpers ───────────────────────────────────────────────────────────────────
def _table_row(cells: list, style: dict) -> html.Div:
    return html.Div(
        [html.Div(c, style={'flex': '1', 'minWidth': '0'}) for c in cells],
        style={**style, 'display': 'flex', 'gap': '12px',
               'borderBottom': '1px solid #f3f4f6', 'width': 'max-content',
               'minWidth': '100%'},
    )

def _badge(val: bool) -> html.Span:
    return html.Span('Sì' if val else 'No', style=BADGE_SI if val else BADGE_NO)

def _field(label: str, input_id: str, placeholder: str = '',
           type_: str = 'text', options: list = None) -> html.Div:
    if options:
        ctrl = dcc.Dropdown(
            id=input_id,
            options=[{'label': o['label'], 'value': o['value']} for o in options],
            placeholder=placeholder,
            style={**INPUT_STYLE, 'padding': '2px 4px'},
            clearable=True,
        )
    else:
        ctrl = dcc.Input(
            id=input_id, type=type_, placeholder=placeholder,
            style=INPUT_STYLE, debounce=False,
        )
    return html.Div([
        html.Label(label, style=LABEL_STYLE),
        ctrl,
    ])


# ── Schede ────────────────────────────────────────────────────────────────────
@db_session
def my_patients_tab(email: str):
    """Mostra solo i pazienti assegnati al medico loggato."""
    utente = Utente.get(email=email)
    medico = Medico.get(utente=utente)

    if not medico:
        return html.Div('Medico non trovato.', style={'color': '#dc2626', 'padding': '20px'})

    pazienti = medico.pazienti.select()[:]

def my_patients_tab(pazienti: list) -> html.Div:
    headers = ['Nome', 'Cognome', 'Cod. Fiscale', 'Fumatore', 'Ex-fumatore',
               'Obesità', 'Alcolista', 'Stupefacenti']
    rows = []
    for i, p in enumerate(pazienti):
        style = TABLE_ROW_EVEN if i % 2 == 0 else TABLE_ROW_ODD
        rows.append(_table_row([
            p['nome'],
            p['cognome'],
            p['codice_fiscale'],
            _badge(p['fumatore']),
            _badge(p['ex-fumatore']),
            _badge(p['obesita']),
            _badge(p['problemi_alcol']),
            _badge(p['problemi_stupefacenti']),
        ], style))
    return html.Div([
        html.Div(style={'display': 'flex', 'justifyContent': 'space-between',
                        'alignItems': 'flex-end', 'marginBottom': '4px'}, children=[
            html.Div([
                html.Div('I tuoi Pazienti', style=SECTION_TITLE),
                html.Div(f'{len(pazienti)} pazienti assegnati', style=SECTION_SUBTITLE),
            ]),
            dcc.Input(placeholder='🔍  Cerca paziente…',
                      style={**INPUT_STYLE, 'width': '220px', 'marginBottom': '0'}),
        ]),
        html.Div([
            _table_row(headers, TABLE_HEADER),
            *(rows if rows else [
                html.Div('Nessun paziente assegnato.',
                         style={'padding': '20px', 'color': '#9ca3af',
                                'fontSize': '14px', 'textAlign': 'center'}),
            ]),
        ], style={'borderRadius': '12px', 'overflowX': 'auto', 'minWidth': '0',
                  'border': '1px solid #e5e7eb'}),
    ], style=CARD)
   
    
@db_session
def manage_therapy_tab(email: str):
    utente = Utente.get(email=email)
    medico = Medico.get(utente=utente)

    if not medico:
        return html.Div('Medico non trovato.', style={'color': '#dc2626', 'padding': '20px'})

    terapie = medico.terapie.select()[:]

    headers = ['Paziente', 'Farmaco', 'Inizio', 'Fine', 'Ass./giorno', 'Quantità', 'Unità'] #, 'Stato
    rows = []
    for i, t in enumerate(terapie):
        style = TABLE_ROW_EVEN if i % 2 == 0 else TABLE_ROW_ODD
        rows.append(_table_row([
            f"{t.paziente.utente.nome} {t.paziente.utente.cognome}",
            t.farmaco_nome,
            str(t.data_inizio),
            str(t.data_fine) if t.data_fine else '—',
            str(t.assunzioni_giornaliere),
            str(t.quantita_per_assunzione),
            t.unita_misura,
            #html.Span('Attiva',    style={'background': '#dcfce7', 'color': '#166534', 'borderRadius': '6px', 'padding': '2px 10px', 'fontSize': '12px', 'fontWeight': '600'})
            #if t.attiva else
            #html.Span('Terminata', style={'background': '#f3f4f6', 'color': '#6b7280', 'borderRadius': '6px', 'padding': '2px 10px', 'fontSize': '12px', 'fontWeight': '600'}),
        ], style))

    return html.Div([
        html.Div(style={'display': 'flex', 'justifyContent': 'space-between',
                        'alignItems': 'flex-end', 'marginBottom': '4px'}, children=[
            html.Div([
                html.Div('Terapie', style=SECTION_TITLE),
                html.Div(f'{len(terapie)} terapie registrate', style=SECTION_SUBTITLE),
            ]),
            dcc.Input(placeholder='🔍  Cerca…',
                      style={**INPUT_STYLE, 'width': '220px', 'marginBottom': '0'}),
        ]),
        html.Div([
            _table_row(headers, TABLE_HEADER),
            *(rows if rows else [
                html.Div('Nessuna terapia registrata.',
                         style={'padding': '20px', 'color': '#9ca3af',
                                'fontSize': '14px', 'textAlign': 'center'}),
            ]),
        ], style={'borderRadius': '12px', 'overflowX': 'auto', 'minWidth': '0',
                  'border': '1px solid #e5e7eb'}),
    ], style=CARD)


    
@db_session
def add_therapy_tab(email: str):
    pazienti_options = [
        {'label': f"{p.utente.nome} {p.utente.cognome}", 'value': p.utente.email}
        for p in list(Paziente.select())
    ]
    farmaci_options = [
        {'label': f.value, 'value': f.value} for f in FarmacoEnum
    ]

    return html.Div([
        html.Div('Inserimento', style=SECTION_TITLE),
        html.Div('Aggiungi una terapia scegliendo il paziente e compilando i campi.', style=SECTION_SUBTITLE),

    html.Div(id='insert-therapy-form', children=[
        html.Div(style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr',
                        'gap': '0 24px', 'marginTop': '20px'}, children=[
            _field('Paziente *', 'inp-p-nome', 'Seleziona…', options=pazienti_options),
            _field('Nome Farmaco *', 'inp-f-nome', 'Seleziona… ', options=farmaci_options),
            
            html.Div([
                html.Label('Data Inizio *', style=LABEL_STYLE),
                dcc.DatePickerSingle(id='inp-data-inizio', display_format='YYYY-MM-DD',
                                    placeholder='YYYY-MM-DD', style={'marginBottom': '14px'}),
            ]),
            html.Div([
                html.Label('Data Fine', style=LABEL_STYLE),
                dcc.DatePickerSingle(id='inp-data-fine', display_format='YYYY-MM-DD',
                                    placeholder='YYYY-MM-DD', style={'marginBottom': '14px'}),
            ]),
            _field('Assunzioni Giornaliere *', 'inp-assunzioni-giornaliere',    'es. 2'),
            _field('Quantità per Assunzione *', 'inp-quantita-per-assunzione',    'es. 1'),
            _field('Unità di Misura *',        'inp-unita-misura',              'es. compressa'),
        ]),

        html.Div(id='msg-add-therapy', style={'marginTop': '8px', 'fontSize': '13px'}),
        html.Button('Salva Terapia', id='btn-save-therapy', n_clicks=0, style=BTN_PRIMARY),
    ]),

], style=CARD)
    

# ── Layout principale ─────────────────────────────────────────────────────────
def medic_layout(session: dict) -> html.Div:
    name = session['display_name']
    
    return html.Div([
        # Header
        html.Div([
            html.H3('Diabetes Control Center - Sezione Medico', style={'margin': '0'}),
            html.Div([
                html.Span(name, style={'marginRight': '15px', 'fontWeight': 'bold'}),
                html.Button('Logout', id='btn-logout', n_clicks=0,
                            style={'padding': '6px 16px', 'borderRadius': '8px'}),
            ]),
        ], style=HEADER),

        # Corpo
        html.Div([
            dcc.Tabs(id='m-main-tabs', value='patients', children=[
                dcc.Tab(label='I tuoi Pazienti', value='patients'),
                dcc.Tab(label='Terapie Attive', value='view-therapies'),
                dcc.Tab(label='Aggiungi Terapia', value='add-therapy'),
            ]),
            html.Div(id='m-tab-content'),
        ], style=CONTAINER),

        # Store per passare l'email al controller senza rifare il login
        dcc.Store(id='medic-email', data=session.get('email')),
    ])