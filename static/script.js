const ingredientesData = {{ ingredientes | tojson }};

function generarOpciones() {
    return ingredientesData.map(i => 
        `<option value="${i[0]}">${i[1]}</option>`
    ).join('');
}

function abrirModalIngrediente() {
    document.getElementById('modal-ingrediente').classList.add('active');
}

function cerrarModalIngrediente() {
    document.getElementById('modal-ingrediente').classList.remove('active');
}

// Cerrar al hacer clic fuera del contenido
document.getElementById('modal-ingrediente').onclick = function (event) {
    if (event.target === this) {
        cerrarModalIngrediente();
    }
}

let contadorIngredientes = 0;

function agregarIngrediente() {
    contadorIngredientes++;
    const container = document.getElementById('ingredientes-container');
    
    container.insertAdjacentHTML('beforeend', `
        <div class="card-2">
            <div class="ingrediente-item">
                <h3>Ingrediente ${contadorIngredientes}</h3>
                <div class="form-row">
                    <div class="form-group">
                        <label>‎ </label>
                        <select class="ingrediente-select" name="ingredientes_ids[]" required>
                            ${generarOpciones()}
                        </select
                    </div>
                    <div class="form-group">
                        <label>Cantidad (g)</label>
                        <input type="number" class="cantidad-input" name="cantidades[]" placeholder="0" min="1">
                    </div>
                </div>
                <div class="form-group">
                    <label>Notas</label>
                    <input type="text" class="notas-input" name="notas_ing[]" placeholder="Notas adicionales">
                </div>
                <br>
                <div>   
                    <a class="btn-secondary" onclick="abrirModalIngrediente()">+ Añadir ingrediente manualmente</a>
                    <button type="button" class="btn-primary" onclick="eliminarIngrediente(this)">Eliminar ingrediente</button>
                </div>
            </div>
        </div>
        <br>
    `);
}

function eliminarIngrediente(boton) {
    const ingredienteCard = boton.closest('.card-2');
    if (ingredienteCard) {
        ingredienteCard.remove();
        contadorIngredientes--;
        renumerarIngredientes(); // Opcional: renumerar después de eliminar
    }
}

// Opcional: renumerar ingredientes para que los números sean consecutivos
function renumerarIngredientes() {
    const ingredientes = document.querySelectorAll('#ingredientes-container .card-2');
    ingredientes.forEach((ingrediente, index) => {
        const titulo = ingrediente.querySelector('h3');
        if (titulo) {
            titulo.textContent = `Ingrediente ${index + 1}`;
        }
    });
    contadorIngredientes = ingredientes.length;
}

let contadorPasos = 0;

function agregarPaso() {
    contadorPasos++;
    const container = document.getElementById('pasos-container');
    
    container.insertAdjacentHTML('beforeend', `
        <div class="card-2">
            <div class="ingrediente-item">
                <h3>Paso ${contadorPasos}</h3>
                <div class="form-group"> <br>
                    <input type="text" class="notas-input" name="notas_pasos[]" placeholder="Describe el paso ${contadorPasos}...">
                </div>
                <br>
                <button type="button" class="btn-secondary" onclick="eliminarPaso(this)">Eliminar paso</button>
            </div>
        </div>
        <br>
    `);
}

function eliminarPaso(boton) {
    const pasoCard = boton.closest('.card-2');
    if (pasoCard) {
        pasoCard.remove();
        contadorPasos--;
        renumerarPasos(); // Opcional: renumerar después de eliminar
    }
}

function renumerarPasos() {
    const pasos = document.querySelectorAll('#pasos-container .card-2');
    pasos.forEach((paso, index) => {
        const titulo = paso.querySelector('h3');
        if (titulo) {
            titulo.textContent = `Paso ${index + 1}`;
        }
    });
    contadorPasos = pasos.length;
}