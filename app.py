# python -m venv venv
# .\venv\Scripts\activate
# pip install -r requirements.txt
# python app.py

"""
App Dash con architettura Model-View-Controller.
"""

import argparse
from dash import Dash, html, dcc, Input, State, Output

from views.login_view import login_layout
from views.secretary_view import secretary_layout
from views.medic_view import medic_layout
from views.patient_view import patient_layout

from controllers import auth_controller, secretary_controller, medic_controller, patient_controller

# ---- App Dash ---------------------------------------------------------------

app = Dash(__name__, suppress_callback_exceptions=True)

app.title = 'Telemedicina'

app.layout = html.Div([
    dcc.Store(id='session', storage_type='session'),
    html.Div(id='page-content'),
])

# ---- Routing ----------------------------------------------------------------

@app.callback(
    Output('page-content', 'children'),
    Input('session', 'modified_timestamp'),
    State('session', 'data'),
)
def route(_, session):
    if not session:
        return login_layout()
    if session.get('ruolo') == 'segretario':
        return secretary_layout(session)
    if session.get('ruolo') == 'paziente':
        return patient_layout(session)
    if session.get('ruolo') == 'medico':
        return medic_layout(session)
    
    return login_layout()

# ---- Registra callbacks -----------------------------------------------------

auth_controller.register_callbacks(app)
secretary_controller.register_callbacks(app)
medic_controller.register_callbacks(app)
patient_controller.register_callbacks(app)

# ---- Main -------------------------------------------------------------------

if __name__ == '__main__':
    backend = 'orm'
    
    app.run(debug=True, port=8060)
