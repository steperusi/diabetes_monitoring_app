"""Controller — callbacks del medico."""

from dash import Output, Input, State
from models.model import model
from views.medic_view import my_patients_tab


def register_callbacks(app):

    @app.callback(
        Output('m-tab-content', 'children'),
        Input('m-main-tabs', 'value'),
        State('medic-email', 'data'),
    )
    def render_tab(tab, email):
        if tab == 'patients':
            pazienti = model.get_pazienti_medico(email)
            return my_patients_tab(pazienti)
        return my_patients_tab([])  # fallback, aggiungi altri tab qui