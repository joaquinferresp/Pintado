from flask import Flask, request, jsonify, session
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'mi_clave_secreta_123'

# Base de datos en memoria
tasks_db = []

# Contraseñas
ADMIN_PASS = 'admin123'
TECH_PASS = 'tech456'

@app.route('/')
def home():
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>Parque Eólico</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; }
        .card { background: white; padding: 20px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .btn { background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; margin: 5px; }
        .btn:hover { background: #0056b3; }
        .btn-danger { background: #dc3545; }
        .btn-success { background: #28a745; }
        input, textarea, select { width: 100%; padding: 10px; margin: 5px 0; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        .hidden { display: none; }
        .task { border-left: 4px solid #007bff; margin: 10px 0; }
        .task.high { border-left-color: #dc3545; }
        .task.medium { border-left-color: #ffc107; }
        .task.low { border-left-color: #28a745; }
        .stats { display: flex; gap: 20px; text-align: center; }
        .stat { flex: 1; }
        .stat-number { font-size: 24px; font-weight: bold; color: #007bff; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌪️ Mantenimiento Parque Eólico</h1>
        
        <!-- Login -->
        <div id="login" class="card">
            <h2>Iniciar Sesión</h2>
            <div id="roleSelect">
                <button class="btn" onclick="selectRole('admin')">👨‍💼 Administrador</button>
                <button class="btn" onclick="selectRole('tech')">🔧 Técnico</button>
            </div>
            <div id="passForm" class="hidden">
                <p id="roleText"></p>
                <input type="password" id="password" placeholder="Contraseña">
                <button class="btn" onclick="login()">Entrar</button>
                <button class="btn btn-danger" onclick="goBack()">Atrás</button>
            </div>
        </div>

        <!-- App Principal -->
        <div id="app" class="hidden">
            <div class="card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h2>Dashboard</h2>
                        <p id="userInfo"></p>
                    </div>
                    <button class="btn btn-danger" onclick="logout()">Salir</button>
                </div>
            </div>

            <!-- Estadísticas -->
            <div class="card">
                <div class="stats">
                    <div class="stat">
                        <div class="stat-number" id="pendingCount">0</div>
                        <div>Pendientes</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number" id="progressCount">0</div>
                        <div>En Progreso</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number" id="completedCount">0</div>
                        <div>Completadas</div>
                    </div>
                </div>
            </div>

            <!-- Crear Tarea (Solo Admin) -->
            <div id="createForm" class="card hidden">
                <h3>Crear Nueva Tarea</h3>
                <input type="text" id="taskTitle" placeholder="Título de la tarea">
                <textarea id="taskDesc" placeholder="Descripción" rows="3"></textarea>
                <select id="taskTurbine">
                    <option value="">Seleccionar turbina</option>
                </select>
                <select id="taskPriority">
                    <option value="low">Prioridad Baja</option>
                    <option value="medium" selected>Prioridad Media</option>
                    <option value="high">Prioridad Alta</option>
                </select>
                <button class="btn btn-success" onclick="createTask()">Crear Tarea</button>
            </div>

            <!-- Botones de Vista -->
            <div class="card">
                <button class="btn" onclick="showView('pending')">Pendientes</button>
                <button class="btn" onclick="showView('progress')">En Progreso</button>
                <button class="btn" onclick="showView('completed')">Completadas</button>
                <button id="showCreateBtn" class="btn btn-success hidden" onclick="toggleCreate()">+ Nueva Tarea</button>
            </div>

            <!-- Lista de Tareas -->
            <div id="tasksList"></div>
        </div>
    </div>

    <script>
        let currentUser = null;
        let currentRole = null;
        let tasks = [];
        let currentView = 'pending';

        // Generar turbinas
        function generateTurbines() {
            const select = document.getElementById('taskTurbine');
            for(let i = 1; i <= 30; i++) {
                const option = document.createElement('option');
                option.value = `WTG ${i.toString().padStart(2, '0')}`;
                option.textContent = `WTG ${i.toString().padStart(2, '0')}`;
                select.appendChild(option);
            }
        }

        function selectRole(role) {
            currentRole = role;
            document.getElementById('roleSelect').classList.add('hidden');
            document.getElementById('passForm').classList.remove('hidden');
            document.getElementById('roleText').textContent = 
                `Contraseña para ${role === 'admin' ? 'Administrador' : 'Técnico'}:`;
            document.getElementById('password').focus();
        }

        function goBack() {
            document.getElementById('roleSelect').classList.remove('hidden');
            document.getElementById('passForm').classList.add('hidden');
            document.getElementById('password').value = '';
        }

        function login() {
            const password = document.getElementById('password').value;
            
            fetch('/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({role: currentRole, password: password})
            })
            .then(r => r.json())
            .then(data => {
                if(data.success) {
                    currentUser = currentRole;
                    document.getElementById('login').classList.add('hidden');
                    document.getElementById('app').classList.remove('hidden');
                    document.getElementById('userInfo').textContent = 
                        `Conectado como: ${currentRole === 'admin' ? 'Administrador' : 'Técnico'}`;
                    
                    if(currentRole === 'admin') {
                        document.getElementById('showCreateBtn').classList.remove('hidden');
                    }
                    
                    generateTurbines();
                    loadTasks();
                } else {
                    alert('Contraseña incorrecta');
                }
            });
        }

        function logout() {
            fetch('/logout', {method: 'POST'})
            .then(() => {
                document.getElementById('login').classList.remove('hidden');
                document.getElementById('app').classList.add('hidden');
                goBack();
                currentUser = null;
            });
        }

        function loadTasks() {
            fetch('/tasks')
            .then(r => r.json())
            .then(data => {
                tasks = data;
                updateStats();
                showTasks();
            });
        }

        function updateStats() {
            document.getElementById('pendingCount').textContent = 
                tasks.filter(t => t.status === 'pending').length;
            document.getElementById('progressCount').textContent = 
                tasks.filter(t => t.status === 'progress').length;
            document.getElementById('completedCount').textContent = 
                tasks.filter(t => t.status === 'completed').length;
        }

        function showView(view) {
            currentView = view;
            showTasks();
        }

        function showTasks() {
            const container = document.getElementById('tasksList');
            const filtered = tasks.filter(t => t.status === currentView);
            
            if(filtered.length === 0) {
                container.innerHTML = '<div class="card"><p>No hay tareas en esta sección</p></div>';
                return;
            }

            container.innerHTML = filtered.map(task => `
                <div class="card task ${task.priority}">
                    <h4>${task.title}</h4>
                    <p>${task.description}</p>
                    <p><strong>Turbina:</strong> ${task.turbine || 'Sin asignar'}</p>
                    <p><strong>Prioridad:</strong> ${task.priority}</p>
                    <p><strong>Creada:</strong> ${task.created_at}</p>
                    ${task.evidence ? `<p><strong>✅ Evidencia:</strong> ${task.evidence}</p>` : ''}
                    <div>
                        ${createButtons(task)}
                    </div>
                </div>
            `).join('');
        }

        function createButtons(task) {
            let buttons = '';
            
            if(currentUser === 'tech' && task.status !== 'completed') {
                if(task.status === 'pending') {
                    buttons += `<button class="btn" onclick="updateTask(${task.id}, 'progress')">▶️ Iniciar</button>`;
                }
                if(task.status === 'progress') {
                    buttons += `<button class="btn btn-success" onclick="completeTask(${task.id})">📁 Completar</button>`;
                }
            }
            
            if(currentUser === 'admin') {
                buttons += `<button class="btn btn-danger" onclick="deleteTask(${task.id})">🗑️ Eliminar</button>`;
            }
            
            return buttons;
        }

        function toggleCreate() {
            const form = document.getElementById('createForm');
            form.classList.toggle('hidden');
        }

        function createTask() {
            const title = document.getElementById('taskTitle').value;
            const description = document.getElementById('taskDesc').value;
            const turbine = document.getElementById('taskTurbine').value;
            const priority = document.getElementById('taskPriority').value;

            if(!title || !description) {
                alert('Complete título y descripción');
                return;
            }

            fetch('/tasks', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({title, description, turbine, priority})
            })
            .then(r => r.json())
            .then(data => {
                if(data.success) {
                    document.getElementById('taskTitle').value = '';
                    document.getElementById('taskDesc').value = '';
                    document.getElementById('taskTurbine').value = '';
                    document.getElementById('taskPriority').value = 'medium';
                    toggleCreate();
                    loadTasks();
                    alert('Tarea creada!');
                }
            });
        }

        function updateTask(id, status) {
            fetch(`/tasks/${id}`, {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({status})
            })
            .then(r => r.json())
            .then(data => {
                if(data.success) {
                    loadTasks();
                }
            });
        }

        function completeTask(id) {
            fetch(`/tasks/${id}`, {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    status: 'completed',
                    evidence: `evidencia_${id}_${new Date().toISOString().slice(0,10)}.jpg`
                })
            })
            .then(r => r.json())
            .then(data => {
                if(data.success) {
                    loadTasks();
                    alert('Tarea completada!');
                }
            });
        }

        function deleteTask(id) {
            if(confirm('¿Eliminar esta tarea?')) {
                fetch(`/tasks/${id}`, {method: 'DELETE'})
                .then(r => r.json())
                .then(data => {
                    if(data.success) {
                        loadTasks();
                        alert('Tarea eliminada!');
                    }
                });
            }
        }
    </script>
</body>
</html>
'''

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    role = data.get('role')
    password = data.get('password')
    
    correct_pass = ADMIN_PASS if role == 'admin' else TECH_PASS
    
    if password == correct_pass:
        session['user'] = role
        return jsonify({'success': True})
    else:
        return jsonify({'success': False})

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/tasks', methods=['GET'])
def get_tasks():
    if 'user' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    return jsonify(tasks_db)

@app.route('/tasks', methods=['POST'])
def create_task():
    if session.get('user') != 'admin':
        return jsonify({'error': 'No autorizado'}), 403
    
    data = request.json
    
    task = {
        'id': len(tasks_db) + 1,
        'title': data.get('title'),
        'description': data.get('description'),
        'turbine': data.get('turbine'),
        'priority': data.get('priority', 'medium'),
        'status': 'pending',
        'evidence': None,
        'created_at': datetime.now().strftime('%Y-%m-%d')
    }
    
    tasks_db.append(task)
    return jsonify({'success': True, 'task': task})

@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    if 'user' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    data = request.json
    
    for task in tasks_db:
        if task['id'] == task_id:
            if 'status' in data:
                task['status'] = data['status']
            if 'evidence' in data:
                task['evidence'] = data['evidence']
            return jsonify({'success': True})
    
    return jsonify({'error': 'Tarea no encontrada'}), 404

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    if session.get('user') != 'admin':
        return jsonify({'error': 'No autorizado'}), 403
    
    global tasks_db
    tasks_db = [t for t in tasks_db if t['id'] != task_id]
    return jsonify({'success': True})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)