# test.py - Versión que funciona con tu aplicación real
import pytest
import json
import os
from unittest.mock import patch, MagicMock

# Importar la aplicación real
from app import app, USER, PASS, cargar_json, guardar_json

@pytest.fixture
def client():
    """Fixture para el cliente de pruebas de Flask"""
    app.config['TESTING'] = True
    app.config['DEBUG'] = False
    with app.test_client() as client:
        yield client

@pytest.fixture
def temp_json_file():
    """Fixture que crea un archivo temporal para pruebas"""
    # Guardar el archivo original si existe
    original_exists = os.path.exists("recetas.json")
    original_content = None
    
    if original_exists:
        with open("recetas.json", "r", encoding="utf-8") as f:
            original_content = f.read()
    
    # Crear archivo de prueba con strings en los IDs
    test_recetas = [
        {
            "id": "1",
            "nombre": "Tortilla de patatas",
            "descripcion": "Tortilla española clásica",
            "tiempo": "30 minutos",
            "dificultad": "Media",
            "ingredientes": ["patatas", "huevos", "cebolla", "aceite", "sal"],
            "pasos": ["Pelar y cortar patatas", "Freír patatas", "Batir huevos", "Mezclar", "Cuajar"]
        },
        {
            "id": "2",
            "nombre": "Ensalada César",
            "descripcion": "Ensalada con pollo y aderezo César",
            "tiempo": "15 minutos",
            "dificultad": "Fácil",
            "ingredientes": ["lechuga", "pollo", "queso", "crutones", "salsa César"],
            "pasos": ["Lavar lechuga", "Cocinar pollo", "Mezclar ingredientes", "Aliñar"]
        }
    ]
    
    with open("recetas.json", "w", encoding="utf-8") as f:
        json.dump(test_recetas, f, indent=2, ensure_ascii=False)
    
    yield test_recetas
    
    # Restaurar el archivo original
    if original_exists:
        with open("recetas.json", "w", encoding="utf-8") as f:
            f.write(original_content)
    else:
        if os.path.exists("recetas.json"):
            os.remove("recetas.json")

# ============ PRUEBAS DE CARGA Y GUARDADO ============

def test_cargar_json_con_mock():
    """Usar MagicMock para simular la lectura de archivos JSON"""
    mock_data = [
        {"id": "1", "nombre": "Receta mock", "descripcion": "Mock description"}
    ]
    
    with patch('builtins.open', create=True) as mock_open:
        with patch('json.load') as mock_json_load:
            mock_json_load.return_value = mock_data
            
            result = cargar_json()
            
            mock_open.assert_called_once_with("recetas.json", encoding="utf-8")
            mock_json_load.assert_called_once()
            assert result == mock_data

def test_cargar_json_error_archivo_no_encontrado():
    """Probar error cuando no existe el archivo"""
    with patch('builtins.open', side_effect=FileNotFoundError("Archivo no encontrado")):
        with pytest.raises(FileNotFoundError):
            cargar_json()

def test_guardar_json_con_mock():
    """Usar MagicMock para simular la escritura de archivos"""
    test_data = [{"id": "3", "nombre": "Nueva receta mock"}]
    
    with patch('builtins.open', create=True) as mock_open:
        with patch('json.dump') as mock_json_dump:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file
            
            guardar_json(test_data)
            
            mock_open.assert_called_once_with("recetas.json", "w", encoding="utf-8")
            mock_json_dump.assert_called_once_with(test_data, mock_file, indent=2, ensure_ascii=False)

# ============ PRUEBAS DE LOGIN ============

def test_login_correcto(client):
    """Probar login con credenciales correctas"""
    response = client.post('/login', json={"username": USER, "password": PASS})
    data = response.get_json()
    assert response.status_code == 200
    assert data["success"] == True

def test_login_incorrecto(client):
    """Probar login con credenciales incorrectas"""
    response = client.post('/login', json={"username": "wrong", "password": "wrong"})
    data = response.get_json()
    assert response.status_code == 200
    assert data["success"] == False
    assert "error" in data

@patch('app.USER', 'test_user')
@patch('app.PASS', 'test_pass')
def test_login_con_credenciales_mockeadas(client):
    """Usar Mock para cambiar las credenciales"""
    response = client.post('/login', json={"username": "test_user", "password": "test_pass"})
    data = response.get_json()
    assert response.status_code == 200
    assert data["success"] == True

def test_login_sin_json(client):
    """Probar login sin enviar JSON"""
    response = client.post('/login', data={})
    assert response.status_code == 415

# ============ PRUEBAS DE RECETAS ============

def test_recetas(client, temp_json_file):
    """Probar que se obtienen todas las recetas"""
    response = client.get('/recetas')
    data = response.get_json()
    assert response.status_code == 200
    assert isinstance(data, list)
    assert len(data) == 2

# ============ PRUEBAS DE EDICIÓN ============

def test_editar_receta(client, temp_json_file):
    """Probar edición de una receta"""
    nuevos_datos = {"nombre": "Tortilla actualizada"}
    
    response = client.post('/editar_receta/1', json=nuevos_datos)
    assert response.status_code == 200
    assert response.get_json()["success"] == True
    
    # Verificar cambio
    response = client.get('/recetas')
    recetas = response.get_json()
    receta = next(r for r in recetas if r["id"] == "1")
    assert receta["nombre"] == "Tortilla actualizada"

def test_editar_receta_con_mock(client):
    """Usar mock para editar receta"""
    mock_recetas = [
        {"id": "1", "nombre": "Original", "descripcion": "Desc", "tiempo": "30 min"}
    ]
    
    with patch('app.cargar_json', return_value=mock_recetas):
        with patch('app.guardar_json') as mock_guardar:
            response = client.post('/editar_receta/1', json={"nombre": "Modificada"})
            
            assert response.status_code == 200
            mock_guardar.assert_called_once()

def test_editar_receta_id_no_encontrado(client):
    """Probar editar receta que no existe"""
    with patch('app.cargar_json', return_value=[{"id": "1", "nombre": "Original"}]):
        with patch('app.guardar_json') as mock_guardar:
            response = client.post('/editar_receta/999', json={"nombre": "Nueva"})
            
            assert response.status_code == 200
            mock_guardar.assert_called_once()

def test_editar_receta_sin_json(client):
    """Probar editar sin enviar JSON"""
    response = client.post('/editar_receta/1', data={})
    assert response.status_code == 415

# ============ PRUEBAS DE BORRADO ============

def test_borrar_receta(client, temp_json_file):
    """Probar borrar una receta"""
    response = client.post('/borrar_receta/1')
    assert response.status_code == 200
    assert response.get_json()["success"] == True
    
    # Verificar que se eliminó
    response = client.get('/recetas')
    recetas = response.get_json()
    assert len(recetas) == 1
    assert recetas[0]["id"] == "2"

def test_borrar_receta_con_mock(client):
    """Usar mock para borrar receta"""
    mock_recetas = [{"id": "1", "nombre": "Receta 1"}, {"id": "2", "nombre": "Receta 2"}]
    
    with patch('app.cargar_json', return_value=mock_recetas):
        with patch('app.guardar_json') as mock_guardar:
            response = client.post('/borrar_receta/1')
            
            assert response.status_code == 200
            mock_guardar.assert_called_once()
            
            # Verificar que se guardó sin la receta eliminada
            args, _ = mock_guardar.call_args
            recetas_guardadas = args[0]
            assert len(recetas_guardadas) == 1
            assert recetas_guardadas[0]["id"] == "2"

def test_borrar_receta_multiple_con_mock(client):
    """Probar borrar múltiples recetas con estado mutable"""
    # Usar una lista mutable para mantener el estado
    current_recetas = [
        {"id": "1", "nombre": "Receta 1"},
        {"id": "2", "nombre": "Receta 2"}
    ]
    
    def mock_cargar():
        return current_recetas.copy()
    
    def mock_guardar(recetas):
        nonlocal current_recetas
        current_recetas = recetas.copy()
    
    with patch('app.cargar_json', side_effect=mock_cargar):
        with patch('app.guardar_json', side_effect=mock_guardar):
            # Primera receta
            client.post('/borrar_receta/1')
            assert len(current_recetas) == 1
            assert current_recetas[0]["id"] == "2"
            
            # Segunda receta
            client.post('/borrar_receta/2')
            assert len(current_recetas) == 0

# ============ PRUEBAS DE INTEGRACIÓN ============

def test_flujo_completo(client, temp_json_file):
    """Probar flujo completo de operaciones"""
    # 1. Obtener recetas iniciales
    response = client.get('/recetas')
    assert len(response.get_json()) == 2
    
    # 2. Editar una receta
    client.post('/editar_receta/1', json={"nombre": "Receta Modificada"})
    
    # 3. Verificar cambio
    response = client.get('/recetas')
    recetas = response.get_json()
    receta = next(r for r in recetas if r["id"] == "1")
    assert receta["nombre"] == "Receta Modificada"
    
    # 4. Borrar la otra receta
    client.post('/borrar_receta/2')
    
    # 5. Verificar estado final
    response = client.get('/recetas')
    recetas_finales = response.get_json()
    assert len(recetas_finales) == 1
    assert recetas_finales[0]["id"] == "1"

def test_flujo_completo_con_mocks(client):
    """Probar flujo completo usando mocks"""
    current_recetas = [
        {"id": "1", "nombre": "Receta 1", "descripcion": "Desc 1"},
        {"id": "2", "nombre": "Receta 2", "descripcion": "Desc 2"}
    ]
    
    def mock_cargar():
        return current_recetas.copy()
    
    def mock_guardar(recetas):
        nonlocal current_recetas
        current_recetas = recetas.copy()
    
    with patch('app.cargar_json', side_effect=mock_cargar):
        with patch('app.guardar_json', side_effect=mock_guardar):
            client.post('/editar_receta/1', json={"nombre": "Modificada"})
            client.post('/borrar_receta/2')
            
            assert len(current_recetas) == 1
            assert current_recetas[0]["nombre"] == "Modificada"

# ============ PRUEBAS DE ERRORES ============

def test_error_en_carga_json(client):
    """Probar error cuando cargar_json falla"""
    with patch('app.cargar_json', side_effect=Exception("Error de carga")):
        with pytest.raises(Exception):
            client.get('/recetas')

def test_error_en_guardado_json(client):
    """Probar error cuando guardar_json falla"""
    with patch('app.cargar_json', return_value=[{"id": "1", "nombre": "Test"}]):
        with patch('app.guardar_json', side_effect=Exception("Error al guardar")):
            with pytest.raises(Exception):
                client.post('/editar_receta/1', json={"nombre": "Nuevo"})

# ============ PRUEBAS DE LLAMADAS ============

def test_multiples_llamadas_con_mock(client):
    """Verificar cantidad de llamadas a funciones mockeadas"""
    mock_cargar = MagicMock(return_value=[{"id": "1", "nombre": "Test"}])
    mock_guardar = MagicMock()
    
    with patch('app.cargar_json', mock_cargar):
        with patch('app.guardar_json', mock_guardar):
            client.get('/recetas')
            client.post('/editar_receta/1', json={"nombre": "Nuevo"})
            client.get('/recetas')
            client.post('/borrar_receta/1')
    
    # En tu app: GET(1), POST editar(2), GET(3), POST borrar(4)
    assert mock_cargar.call_count == 4
    assert mock_guardar.call_count == 2

# ============ PRUEBAS DE SPY Y PATCH ============

def test_spy_en_cargar_json(client, temp_json_file):
    """Usar spy para verificar llamadas"""
    original_cargar = cargar_json
    spy_cargar = MagicMock(side_effect=original_cargar)
    
    with patch('app.cargar_json', spy_cargar):
        client.get('/recetas')
        client.post('/editar_receta/1', json={"nombre": "Test"})
        
        assert spy_cargar.call_count >= 2

@patch('app.cargar_json')
@patch('app.guardar_json')
def test_patch_multiple(mock_guardar, mock_cargar, client):
    """Usar múltiples decoradores patch"""
    mock_cargar.return_value = [{"id": "1", "nombre": "Mock"}]
    
    response = client.post('/borrar_receta/1')
    
    assert response.status_code == 200
    mock_cargar.assert_called_once()
    mock_guardar.assert_called_once()

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])