"""View del medico."""

from dash import html, dcc
from models.model import model

# ── Stili ─────────────────────────────────────────────────────────────────────
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
BTN_SECONDARY = {
    'background': 'linear-gradient(90deg, #4748AC 0%, #5E60CE 100%)',
    'color': 'white', 'border': 'none', 'borderRadius': '10px',
    'padding': '10px 28px', 'fontWeight': '600', 'fontSize': '14px',
    'cursor': 'pointer', 'marginBottom': '12px',
}

LABEL_STYLE = {
    'fontWeight': '600', 'fontSize': '13px',
    'color': '#6b7280', 'marginBottom': '4px',
    'display': 'block', 'letterSpacing': '0.4px',
}
CHAT_BOX = {
    'height': '300px', 'overflowY': 'auto',
    'border': '1px solid #e5e7eb', 'borderRadius': '12px',
    'padding': '12px', 'marginTop': '12px', 'marginBottom': '12px',
    'background': '#f9fafb',
}

# ── Helpers ───────────────────────────────────────────────────────────────────
    
def _table_row(cells: list, style: dict, col_widths: list = None) -> html.Div:
    children = []
    for i, c in enumerate(cells):
        if col_widths and i < len(col_widths):
            cell_style = {'flex': f'0 0 {col_widths[i]}', 'minWidth': col_widths[i]}
        else:
            cell_style = {'flex': '1', 'minWidth': '60px'}
        children.append(html.Div(c, style=cell_style))
    return html.Div(
        children,
        style={**style, 'display': 'flex', 'gap': '12px',
               'borderBottom': '1px solid #f3f4f6', 'width': 'max-content',
               'minWidth': '100%'},
    )

def _badge(val: bool) -> html.Span:
    return html.Span('Sì' if val else 'No', style=BADGE_SI if val else BADGE_NO)

def render_chat(msgs: list, my_email: str) -> html.Div:
    if not msgs:
        return html.P('Nessun messaggio.', style={'color': '9ca3af', 'fontSize': '14px'})
    
    bubbles = []
    for m in msgs:
        is_mine = m['mittente'] == my_email
        bubbles.append(
            html.Div([
                html.Div(m['testo'], style={
                    'background': '#4748AC' if is_mine else '#f3f4f6',
                    'color': 'white' if is_mine else '#1f2937',
                    'borderRadius': '12px', 'padding': '8px 14px',
                    'maxWidth': '70%', 'fontSize': '14px',
                }),
            html.Div(m['timestamp'], style={
                'fontSize': '11px', 'color': '9ca3af', 'marginTop': '2px',
            }),
            ], style={
                'display': 'flex', 'flexDirection': 'column',
                'alignItems': 'flex-end' if is_mine else 'flex-start',
                'marginBottom': '10px',
            })
        )
    return html.Div(bubbles)

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
    
def _fascia_ordine(fascia: str) -> int:
    fascia = fascia.lower()
    if 'colazione' in fascia:
        return 0
    elif 'pranzo' in fascia:
        return 1
    elif 'cena' in fascia:
        return 2
    return 3
    
    
def render_storico_temp(assunzioni: list) -> list:
    """Storico temporaneo durante la compilazione — con bottone elimina."""
    header = _table_row(['Fascia', 'Farmaco', 'Quantità', ''], TABLE_HEADER)
    ordinate = sorted(assunzioni, key=lambda x: (_fascia_ordine(x['orario']), x['orario']))
    rows = [
        _table_row([
            a['orario'].capitalize(),
            a['farmaco_nome'],
            str(a['quantita']),
            html.Button('✕', id={'type': 'btn-del-assunzione', 'index': i},
                        n_clicks=0, style={
                            'background': 'none', 'border': '1px solid #e53e3e',
                            'color': '#e53e3e', 'borderRadius': '6px',
                            'cursor': 'pointer', 'padding': '2px 8px', 'fontSize': '12px',
                        }),
        ], TABLE_ROW_EVEN if i % 2 == 0 else TABLE_ROW_ODD)
        for i, a in enumerate(ordinate)
    ]
    return [header] + rows
    
def render_storico_assunzioni(storico: list) -> list:

    header = _table_row(
        ['Paziente', 'Farmaco', 'Fascia', 'Quantità', 'Data Inizio', 'Data Fine'],
        TABLE_HEADER,
    )
    if not storico:
        return [header, html.Div(
            'Nessuna assunzione registrata.',
            style={'padding': '20px', 'color': '#9ca3af',
                'fontSize': '14px', 'textAlign': 'center'},
        )]
    ordinate = sorted(storico, key=lambda x: (_fascia_ordine(x['orario'])))
    rows = [
        _table_row([
            s['paziente'],
            s['farmaco'],
            s['fascia'].capitalize(),
            s['quantita'],
            s['data_inizio'],
            s['data_fine'],
        ], TABLE_ROW_EVEN if i % 2 == 0 else TABLE_ROW_ODD)
        for i, s in enumerate(ordinate)
    ]
    return [header] + rows


# ── Schede ────────────────────────────────────────────────────────────────────
def my_patients_tab(pazienti: list) -> html.Div:
    headers = ['Nome', 'Cognome', 'Cod. Fiscale', 'Fumatore', 'Ex-fumatore',
               'Obesità', 'Alcolista', 'Stupefacenti', '', '']
    PATIENT_COLS = ['80px', '80px', '150px', '70px', '80px', '60px', '60px', '80px', '32px', '32px']
    
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
            html.Button('✏️', id={'type': 'btn-edit-patient', 'index': p['codice_fiscale']}, n_clicks=0, style={
                'background': 'none', 'border': '1px solid #4748AC', 'borderRadius': '6px', 'cursor': 'pointer',
                'padding': '2px 8px', 'fontSize': '14px',}),
            html.Button('📊', id={'type': 'btn-view-data', 'index': p['codice_fiscale']}, n_clicks=0, style={
                'background': 'none', 'border': '1px solid #4748AC', 'borderRadius': '6px', 'cursor': 'pointer',
                'padding': '2px 8px', 'fontSize': '14px',}),
        ], style, PATIENT_COLS))
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
            _table_row(headers, TABLE_HEADER, PATIENT_COLS),
            *(rows if rows else [
                html.Div('Nessun paziente assegnato.',
                         style={'padding': '20px', 'color': '#9ca3af',
                                'fontSize': '14px', 'textAlign': 'center'}),
            ]),
        ], style={'borderRadius': '12px', 'overflowX': 'auto', 'minWidth': '0',
                  'border': '1px solid #e5e7eb'}),
    ], key='patients-tab', style=CARD)
   
def edit_patient_tab(paziente: dict) -> html.Div:
    """Form di modifica paziente, precompilato con i dati esistenti."""
    flags_attuali=[]
    if paziente.get('fumatore'):                    flags_attuali.append('fumatore')
    if paziente.get('ex_fumatore'):                 flags_attuali.append('ex_fumatore')
    if paziente.get('obesita'):                     flags_attuali.append('obesita')
    if paziente.get('problemi_alcol'):              flags_attuali.append('problemi_alcol')
    if paziente.get('problemi_stupefacenti'):       flags_attuali.append('problemi_stupefacenti')

    return html.Div([
        # Tasto per tornare indietro
        html.Button('← Torna alla lista', id='btn-back-patients', n_clicks=0,
                    style={'background': 'none', 'border': 'none', 'color': '#4748AC',
                           'fontWeight': '600', 'cursor': 'pointer', 'fontSize': '14px',
                           'marginBottom': '16px', 'padding': '0'}),

        html.Div('Modifica Paziente', style=SECTION_TITLE),
        html.Div(f"Stai modificando: {paziente.get('nome')} {paziente.get('cognome')}",
                 style=SECTION_SUBTITLE),

        html.Div(style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr',
                        'gap': '0 24px', 'marginTop': '20px'}, children=[
                html.Div([
                        html.Label('Nome *', style=LABEL_STYLE),
                        dcc.Input(id='edit-p-nome', type='text',
                                value=paziente.get('nome', ''),
                                style=INPUT_STYLE),
                    ]),
                    html.Div([
                        html.Label('Cognome *', style=LABEL_STYLE),
                        dcc.Input(id='edit-p-cognome', type='text',
                                value=paziente.get('cognome', ''),
                                style=INPUT_STYLE),
                    ]),
        ]),

        # Campi di sola lettura (non modificabili)
        html.Div(style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr',
                        'gap': '0 24px'}, children=[
            html.Div([
                html.Label('Email (non modificabile)', style=LABEL_STYLE),
                html.Div(paziente.get('email', '—'),
                         style={**INPUT_STYLE, 'background': '#f3f4f6',
                                'color': '#9ca3af', 'cursor': 'not-allowed'}),
            ]),
            html.Div([
                html.Label('Codice Fiscale (non modificabile)', style=LABEL_STYLE),
                html.Div(paziente.get('codice_fiscale', '—'),
                         style={**INPUT_STYLE, 'background': '#f3f4f6',
                                'color': '#9ca3af', 'cursor': 'not-allowed'}),
            ]),
        ]),

        # Comorbidità
        html.Div([
            html.Label('Comorbidità', style=LABEL_STYLE),
            dcc.Textarea(id='edit-p-comorbidita',
                         value=paziente.get('comorbidita', ''),
                         placeholder='Es. ipertensione, insufficienza renale…',
                         style={**INPUT_STYLE, 'minHeight': '80px',
                                'fontFamily': '"Inter", "Segoe UI", sans-serif'}),
        ], style={'marginTop': '8px'}),

        # Fattori di rischio
        html.Div([
            html.Label('Fattori di rischio', style={**LABEL_STYLE, 'marginBottom': '10px'}),
            dcc.Checklist(
                id='edit-p-flags',
                options=[
                    {'label': '  Fumatore',                   'value': 'fumatore'},
                    {'label': '  Ex fumatore',                'value': 'ex_fumatore'},
                    {'label': '  Obesità',                    'value': 'obesita'},
                    {'label': '  Problemi con alcol',         'value': 'problemi_alcol'},
                    {'label': '  Dipendenza da stupefacenti', 'value': 'problemi_stupefacenti'},
                ],
                value=flags_attuali,
                inputStyle={'marginRight': '8px'},
                labelStyle={'display': 'flex', 'alignItems': 'center',
                            'fontSize': '14px', 'color': '#374151', 'padding': '6px 0'},
            ),
        ], style={'marginTop': '16px', 'marginBottom': '16px', 'padding': '16px',
                  'borderRadius': '10px', 'border': '1px solid #e5e7eb',
                  'backgroundColor': '#f9fafb'}),

        html.Div(id='msg-edit-patient', style={'marginTop': '8px', 'fontSize': '13px'}),
        html.Button('Salva Modifiche', id='btn-save-edit-patient', n_clicks=0, style=BTN_PRIMARY),

        # Store con il CF del paziente in modifica
        dcc.Store(id='editing-patient-cf', data=paziente.get('codice_fiscale')),
    ], style=CARD)

def patient_data_tab(paziente: dict) -> html.Div:
    """Analisi dati del paziente"""
    return html.Div([
        # Tasto per tornare indietro
        html.Button('← Torna alla lista', id='btn-back-patients', n_clicks=0,
                    style={'background': 'none', 'border': 'none', 'color': '#4748AC',
                           'fontWeight': '600', 'cursor': 'pointer', 'fontSize': '14px',
                           'marginBottom': '16px', 'padding': '0'}),

        html.Div('Analisi Dati Paziente', style=SECTION_TITLE),
        html.Div(f"Stai analizzando: {paziente.get('nome')} {paziente.get('cognome')}",
                 style=SECTION_SUBTITLE),

        # Dropdown per selezionare intervallo di analisi
        html.Div(id='p-tab-data', children=[
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
                        dcc.Graph(id='m-p-graph-pre-colazione', config={'responsive': True})
                    ], style={'background': '#ffffff', 'borderRadius': '12px', 'padding': '12px', 'border': '1px solid #e5e7eb',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.05)', 'flex': '1', 'marginLeft': '5px', 'minWidth': '0', 'overflow': 'hidden'}),
                    html.Div([
                        dcc.Graph(id='m-p-graph-post-colazione', config={'responsive': True})
                    ], style={'background': '#ffffff', 'borderRadius': '12px', 'padding': '12px', 'border': '1px solid #e5e7eb',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.05)', 'flex': '1', 'marginLeft': '5px', 'minWidth': '0', 'overflow': 'hidden'}),
                ], style={'display': 'flex', 'marginBottom': '20px', 'height': '350px'}),
                
                # Riga 2
                html.Div([
                    html.Div([
                        dcc.Graph(id='m-p-graph-pre-pranzo', config={'responsive': True})
                    ], style={'background': '#ffffff', 'borderRadius': '12px', 'padding': '12px', 'border': '1px solid #e5e7eb',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.05)', 'flex': '1', 'marginRight': '5px', 'minWidth': '0', 'overflow': 'hidden'}),
                    html.Div([
                        dcc.Graph(id='m-p-graph-post-pranzo', config={'responsive': True})
                    ], style={'background': '#ffffff', 'borderRadius': '12px', 'padding': '12px', 'border': '1px solid #e5e7eb',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.05)', 'flex': '1', 'marginLeft': '5px', 'minWidth': '0', 'overflow': 'hidden'}),
                ], style={'display': 'flex', 'marginBottom': '20px', 'height': '350px'}),
                
                # Riga 3
                html.Div([
                    html.Div([
                        dcc.Graph(id='m-p-graph-pre-cena', config={'responsive': True})
                    ], style={'background': '#ffffff', 'borderRadius': '12px', 'padding': '12px', 'border': '1px solid #e5e7eb',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.05)', 'flex': '1', 'marginRight': '5px', 'minWidth': '0', 'overflow': 'hidden'}),
                    html.Div([
                        dcc.Graph(id='m-p-graph-post-cena', config={'responsive': True})
                    ], style={'background': '#ffffff', 'borderRadius': '12px', 'padding': '12px', 'border': '1px solid #e5e7eb',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.05)', 'flex': '1', 'marginLeft': '5px', 'minWidth': '0', 'overflow': 'hidden'}),
                ], style={'display': 'flex', 'height': '350px'}),
            ], style={'display': 'flex', 'flexDirection': 'column'}),
            
            # Refresh interval
            dcc.Interval(id='p-data-refresh', interval=5000),
        ]),

        # Store con l'email del paziente visualizzato
        dcc.Store(id='viewing-patient-email', data=paziente.get('email')),
    
    ], style=CARD)
    
def manage_therapy_tab(terapie: list) -> html.Div:
    def _assunzioni_detail(terapia: dict) -> html.Div:
        """Sotto-tabella assunzioni espandibile."""
        assunzioni = terapia.get('assunzioni', [])
        if not assunzioni:
            return html.Div('Nessuna assunzione registrata.',
                            style={'padding': '10px 16px', 'color': '#9ca3af', 'fontSize': '13px'})
        header = _table_row(
            ['Fascia', 'Farmaco', 'Quantità', 'Unità'],
            {**TABLE_HEADER, 'background': '#f0f0ff', 'color': '#4748AC'},
        )
        righe = [
            _table_row([
                a['orario'].capitalize(),
                a['farmaco_nome'],
                str(a['quantita']),
                a['unita_misura'],
            ], TABLE_ROW_EVEN if i % 2 == 0 else TABLE_ROW_ODD)
            for i, a in enumerate(sorted(assunzioni, key=lambda x: _fascia_ordine(x['orario'])))
        ]
        return html.Div([header] + righe,
                        style={'borderTop': '1px solid #e5e7eb', 'background': '#fafbff'})

    headers = ['', 'Paziente', 'Inizio', 'Fine']
    rows = []
    for i, t in enumerate(terapie):
        row_style = TABLE_ROW_EVEN if i % 2 == 0 else TABLE_ROW_ODD
        rows.append(html.Div([
            _table_row([
                html.Button(
                    '▶',
                    id={'type': 'btn-expand-therapy', 'index': t['id']},
                    n_clicks=0,
                    style={
                        'background': 'none', 'border': 'none',
                        'cursor': 'pointer', 'fontSize': '12px',
                        'color': '#4748AC', 'padding': '0 4px',
                        'transition': 'transform 0.2s',
                    },
                ),
                t['paziente_nome'],
                t['data_inizio'],
                t['data_fine'] if t['data_fine'] else '—',
            ], row_style),
            html.Div(
                id={'type': 'therapy-detail', 'index': t['id']},
                children=_assunzioni_detail(t),
                style={'display': 'none'},
            ),
        ]))

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
        ], style={'borderRadius': '12px', 'overflow': 'hidden', 'minWidth': '0', 'border': '1px solid #e5e7eb'}),
    ], key='therapies-tab', style=CARD)


def add_therapy_tab(pazienti_options: list, farmaci_options: list) -> html.Div:
    return html.Div([
        html.Div('Inserimento', style=SECTION_TITLE),
        html.Div('Aggiungi una terapia scegliendo il paziente, le date e le assunzioni.', style=SECTION_SUBTITLE),

        html.Div(id='insert-therapy-form', children=[

            # ── Paziente + Date ───────────────────────────────────────────────
            html.Div(style={
                'display': 'grid', 'gridTemplateColumns': '1fr 1fr 1fr',
                'gap': '0 24px', 'marginTop': '20px', 'marginBottom': '20px',
            }, children=[
                _field('Paziente *', 'inp-p-nome', 'Seleziona…', options=pazienti_options),
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
            ]),

            # ── Input singola assunzione ──────────────────────────────────────
            html.Hr(style={'borderColor': '#e2e8f0', 'margin': '4px 0 16px'}),
            html.Div('Assunzioni giornaliere', style={
                'fontWeight': '600', 'fontSize': '14px',
                'color': '#4748AC', 'marginBottom': '12px',
            }),

            html.Div(style={
                'display': 'grid', 'gridTemplateColumns': '160px 1fr 100px auto',
                'gap': '0 12px', 'alignItems': 'end', 'marginBottom': '12px',
            }, children=[
                _field('Fascia', 'inp-fascia', options=[
                    {'label': 'Colazione', 'value': 'colazione'},
                    {'label': 'Pranzo',    'value': 'pranzo'},
                    {'label': 'Cena',      'value': 'cena'},
                ]),
                _field('Farmaco', 'inp-farmaco-row', 'Seleziona farmaco…', options=farmaci_options),
                _field('Quantità', 'inp-quantita-row', 'es. 1', type_='text'),
                html.Div([
                    html.Button('+ Aggiungi', id='btn-add-assunzione', n_clicks=0, style=BTN_SECONDARY),
                ]),
            ]),

            html.Div(id='msg-add-assunzione', style={'fontSize': '13px', 'marginBottom': '8px'}),

            # ── Storico temporaneo assunzioni ─────────────────────────────────
            html.Div(id='storico-temp-section', style={'display': 'none'}, children=[
                html.Div('Assunzioni aggiunte', style={
                    'fontWeight': '600', 'fontSize': '13px',
                    'color': '#6b7280', 'marginBottom': '8px',
                }),
                html.Div(id='storico-temp-table',
                         style={'borderRadius': '12px', 'overflowX': 'auto',
                                'border': '1px solid #e5e7eb', 'marginBottom': '16px'}),
            ]),

            html.Div(id='msg-add-therapy', style={'marginTop': '8px', 'fontSize': '13px'}),
            html.Button('Salva Terapia', id='btn-save-therapy', n_clicks=0, style=BTN_PRIMARY),
        ]),

        # ── Store temporaneo assunzioni ───────────────────────────────────────
        dcc.Store(id='store-assunzioni-temp', data={'items': [], 'ts': 0}),
        dcc.Store(id='store-reset-form', data=0),

    ], style=CARD)



def messages_tab() -> html.Div:
    return html.Div([
        html.Div('Messaggi', style=SECTION_TITLE),
        html.Div('Scrivi ai tuoi pazienti.', style=SECTION_SUBTITLE),
        dcc.Dropdown(id='m-conv-select', placeholder='Seleziona paziente…',
                     style={'marginBottom': '12px'}),
        html.Div(id='m-chat-area', style=CHAT_BOX),
        html.Div([
            dcc.Input(id='m-msg-input', type='text',
                      placeholder='Scrivi messaggio…',
                      style={**INPUT_STYLE, 'width': '75%',
                             'display': 'inline-block', 'marginBottom': '0',
                             'marginRight': '8px'}),
            html.Button('Invia', id='m-btn-send', n_clicks=0, style=BTN_PRIMARY),
        ], style={'display': 'flex', 'alignItems': 'center'}),
        html.Div(id='m-send-status',
                 style={'color': '#16a34a', 'marginTop': '6px', 'fontSize': '13px'}),
    ], style=CARD)
    

# ── Layout principale ─────────────────────────────────────────────────────────
def medic_layout(session: dict) -> html.Div:
    name = session['display_name']
    
    return html.Div([
        # Header
        html.Div([
            html.Img(src='/assets/full_logo.png', alt='Logo',
                    style={'height': '50px', 'borderRadius': '8px', 'marginRight': '16px'}),
            html.H3('Medico', style={'margin': '0', 'color': 'white'}),
            html.Div([
                html.Span(name, style={'marginRight': '15px', 'fontWeight': 'bold'}),
                html.Div([
                    html.Button(
                        ['🔔', html.Span('0', id='m-alert-badge', style={
                            'background': '#ef4444', 'color': 'white',
                            'borderRadius': '50%', 'fontSize': '11px',
                            'padding': '1px 6px', 'marginLeft': '4px',
                            'fontWeight': '700', 'display': 'none',
                        })],
                        id='m-alert-btn', n_clicks=0,
                        style={'background': 'none', 'border': '1px solid white',
                            'borderRadius': '8px', 'color': 'white',
                            'padding': '6px 12px', 'cursor': 'pointer',
                            'fontSize': '16px', 'marginRight': '10px'},
                    ),
                    html.Div(id='m-alert-panel', style={
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
        ], style={**HEADER, 'position': 'relative'}),

        # Corpo
        html.Div([
            dcc.Tabs(id='m-main-tabs', value='patients', children=[
                dcc.Tab(label='I tuoi Pazienti', value='patients'),
                dcc.Tab(label='Terapie Attive', value='view-therapies'),
                dcc.Tab(label='Aggiungi Terapia', value='add-therapy'),
                dcc.Tab(label='Messaggi', value='messages'),
            ]),
            html.Div(id='m-tab-content'),
        ], style=CONTAINER),

        # Store per passare l'email al controller senza rifare il login
        dcc.Store(id='medic-email', data=session.get('email')),
        dcc.Interval(id='m-refresh', interval=3000),
    ])