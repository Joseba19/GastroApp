# app_refactorizado.py
from flask import Flask, render_template, jsonify
import json
import os

class Configuracion:
    """Clase de configuración - aparecerá en UML"""
    SECRET_KEY = 'tu-clave-secreta'
    DEBUG = True
    JSON_FILE = 'recetas.json'

class GestorRecetas:
    """Clase que maneja la lógica de recetas - aparecerá en UML"""
    
    def __init__(self, archivo_json):
        self.archivo = archivo_json
        self._cache = None
    
    def cargar_recetas(self):
        """Carga recetas desde el archivo JSON"""
        if self._cache is None:
            with open(self.archivo, 'r', encoding='utf-8') as f:
                self._cache = json.load(f)
        return self._cache
    
    def buscar_receta(self, nombre):
        """Busca una receta por nombre"""
        recetas = self.cargar_recetas()
        return [r for r in recetas if nombre.lower() in r.get('nombre', '').lower()]

class ControladorWeb:
    """Controlador Flask - maneja las rutas HTTP"""
    
    def __init__(self, app, gestor_recetas):
        self.app = app
        self.gestor = gestor_recetas
        self._registrar_rutas()
    
    def _registrar_rutas(self):
        """Registra todas las rutas de la aplicación"""
        
        @self.app.route('/')
        def home():
            return render_template('index.html')
        
        @self.app.route('/recetas')
        def obtener_recetas():
            return jsonify(self.gestor.cargar_recetas())
        
        @self.app.route('/recetas/buscar/<nombre>')
        def buscar_receta(nombre):
            return jsonify(self.gestor.buscar_receta(nombre))

# Instanciación (esto NO va en el diagrama, pero ejecuta la app)
if __name__ == '__main__':
    app = Flask(__name__)
    app.config.from_object(Configuracion)
    
    gestor = GestorRecetas(Configuracion.JSON_FILE)
    controlador = ControladorWeb(app, gestor)
    
    app.run(debug=Configuracion.DEBUG)