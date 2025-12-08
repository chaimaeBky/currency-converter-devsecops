"""Configuration pytest pour les tests backend"""
import pytest
import sys
import os

# Ajouter le dossier parent au path pour importer app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importer l'app Flask (votre app.py actuel)
from app import app as flask_app


@pytest.fixture
def app():
    """
    Fixture qui configure l'application Flask en mode test
    """
    flask_app.config.update({
        "TESTING": True,
    })
    
    yield flask_app


@pytest.fixture
def client(app):
    """
    Fixture qui fournit un client de test Flask
    Permet de faire des requêtes HTTP simulées
    """
    return app.test_client()


@pytest.fixture
def runner(app):
    """
    Fixture pour tester les commandes CLI (optionnel)
    """
    return app.test_cli_runner()