from flask import Flask, request, jsonify, session
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'clave_secreta_parque_eolico_2025'

# Archivo para tareas
TASKS_FILE = "tareas_web.json"

# Contraseñas
PASSWORDS = {
    'admin': 'admin123',
    'technician': 'tech456'
}

def load_tasks():
    """Cargar tareas desde archivo"""
    if os.path.exists(TASKS_FILE):
        try:
            with open(TASKS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_tasks(tasks):
    """Guardar tareas en archivo"""
    with open(TASKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

def is_older_than_30_days(completed_date):
    """Verificar si una fecha es mayor a 30 días"""
    if not completed_date:
        return False
    try:
        completed = datetime.strptime(completed_date, '%Y-%m-%d')
        return datetime.now() - completed > timedelta(days=30)
    except:
        return False

@app.route('/')
def index():
    """Página principal con HTML completo"""
    return '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mantenimiento Parque Eólico</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background-color: #F9FAFB; }
        
        .login-container { 
            display: flex; justify-content: center; align-items: center; 
            min-height: 100vh; padding: 20px; 
        }
        .login-box { 
            background: white; padding: 40px; border-radius: 12px; 
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); max-width: 400px; width: 100%; 
            text-align: center; 
        }
        .login-title { font-size: 28px; font-weight: bold; color: #1F2937; margin-bottom: 8px; }
        .login-subtitle { font-size: 18px; color: #6B7280; margin-bottom: 40px; }
        
        .role-btn { 
            width: 100%; padding: 16px; margin: 8px 0; border: 2px solid #E5E7EB; 
            background: white; border-radius: 8px; font-size: 16px; cursor: pointer;
            transition: all 0.2s; 
        }
        .role-btn:hover { border-color: #3B82F6; background-color: #EFF6FF; }
        
        .password-section { margin-top: 20px; display: none; }
        .password-input { 
            width: 100%; padding: 12px; border: 1px solid #D1D5DB; 
            border-radius: 8px; font-size: 16px; margin: 16px 0; 
        }
        
        .login-buttons { display: flex; gap: 12px; margin-top: 20px; }
        .btn { 
            flex: 1; padding: 12px; border: none; border-radius: 8px; 
            font-size: 16px; font-weight: bold; cursor: pointer; 
        }
        .btn-primary { background-color: #3B82F6; color: white; }
        .btn-secondary { background-color: #6B7280; color: white; }
        
        .header { 
            background: white; padding: 16px 20px; border-bottom: 1px solid #E5E7EB;
            display: flex; justify-content: space-between; align-items: center; 
        }
        .header-title { font-size: 20px; font-weight: bold; color: #1F2937; }
        .header-role { font-size: 14px; color: #6B7280; }
        
        .tabs { 
            background: white; display: flex; border-bottom: 1px solid #E5E7EB; 
            overflow-x: auto; 
        }
        .tab { 
            padding: 12px 16px; border: none; background: none; 
            cursor: pointer; white-space: nowrap; font-size: 14px;
            border-bottom: 2px solid transparent; 
        }
        .tab.active { border-bottom-color: #3B82F6; color: #3B82F6; font-weight: bold; }
        
        .stats { 
            display: flex; gap: 16px; padding: 20px; justify-content: center;
            flex-wrap: wrap; 
        }
        .stat-card { 
            background: white; padding: 20px; border-radius: 8px; 
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); text-align: center; 
            min-width: 120px; 
        }
        .stat-number { font-size: 32px; font-weight: bold; color: #3B82F6; }
        .stat-label { font-size: 12px; color: #6B7280; margin-top: 4px; }
        
        .content { padding: 20px; max-width: 1200px; margin: 0 auto; }
        
        .task-card { 
            background: white; border-radius: 8px; margin-bottom: 16px; 
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); overflow: hidden; 
        }
        .task-card.priority-alta { border-left: 4px solid #EF4444; }
        .task-card.priority-media { border-left: 4px solid #EAB308; }
        .task-card.priority-baja { border-left: 4px solid #22C55E; }
        
        .task-header { 
            display: flex; justify-content: space-between; align-items: flex-start; 
            padding: 16px 16px 8px 16px; 
        }
        .task-title { font-size: 18px; font-weight: bold; color: #1F2937; flex: 1; }
        .task-status { 
            padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: 600; 
        }
        .status-pendiente { background-color: #FEF3C7; color: #92400E; }
        .status-en-progreso { background-color: #DBEAFE; color: #1E40AF; }
        .status-completada { background-color: #D1FAE5; color: #065F46; }
        
        .task-body { padding: 0 16px 16px 16px; }
        .task-description { color: #6B7280; margin-bottom: 12px; }
        .task-info { font-size: 12px; color: #6B7280; margin-bottom: 12px; }
        .task-evidence { 
            background-color: #D1FAE5; padding: 8px; border-radius: 6px; 
            margin-bottom: 12px; font-size: 12px; color: #065F46; 
        }
        
        .task-actions { display: flex; gap: 8px; flex-wrap: wrap; }
        .task-btn { 
            padding: 8px 12px; border: none; border-radius: 6px; 
            font-size: 12px; font-weight: bold; cursor: pointer; 
        }
        .btn-start { background-color: #3B82F6; color: white; }
        .btn-evidence { background-color: #10B981; color: white; }
        .btn-delete { background-color: #EF4444; color: white; }
        
        .floating-btn { 
            position: fixed; bottom: 30px; right: 30px; width: 60px; height: 60px; 
            border-radius: 50%; background-color: #3B82F6; color: white; 
            border: none; font-size: 24px; font-weight: bold; cursor: pointer;
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4); 
        }
        
        .modal { 
            display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
            background-color: rgba(0, 0, 0, 0.5); z-index: 1000; 
        }
        .modal-content { 
            background: white; margin: 50px auto; padding: 20px; 
            border-radius: 8px; max-width: 500px; width: 90%; 
        }
        .modal-header { 
            display: flex; justify-content: space-between; align-items: center; 
            margin-bottom: 20px; 
        }
        .close-btn { 
            background: none; border: none; font-size: 24px; 
            cursor: pointer; color: #6B7280; 
        }
        
        .form-group { margin-bottom: 16px; }
        .form-label { display: block; margin-bottom: 4px; font-weight: bold; color: #374151; }
        .form-input, .form-textarea, .form-select { 
            width: 100%; padding: 12px; border: 1px solid #D1D5DB; 
            border-radius: 8px; font-size: 16px; 
        }
        .form-textarea { height: 100px; resize: vertical; }
        
        @media (max-width: 768px) {
            .stats { flex-direction: column; }
            .task-actions { flex-direction: column; }
            .login-box { margin: 20px; }
        }
    </style>
</head>
<body>
    <div id="app">
        <!-- Login Screen -->
        <div id="loginScreen" class="login-container">
            <div class="login-box">
                <h1 class="login-title">🌪️ Sistema de Mantenimiento</h1>
                <h2 class="login-subtitle">Parque Eólico</h2>
                
                <div id="roleSelection">
                    <p style="margin-bottom: 20px; color: #374151;">Selecciona tu rol:</p>
                    <button class="role-btn" onclick="selectRole('admin')">👨‍💼 Administrador</button>
                    <button class="role-btn" onclick="selectRole('technician')">🔧 Técnico</button>
                </div>
                
                <div id="passwordSection" class="password-section">
                    <p id="passwordLabel" style="color: #374151; margin-bottom: 16px;"></p>
                    <input type="password" id="passwordInput" class="password-input" placeholder="Contraseña">
                    <div class="login-buttons">
                        <button class="btn btn-secondary" onclick="goBack()">← Atrás</button>
                        <button class="btn btn-primary" onclick="login()">Ingresar</button>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Main App -->
        <div id="mainApp" style="display: none;">
            <header class="header">
                <div>
                    <div class="header-title">🌪️ Mantenimiento Parque Eólico</div>
                    <div class="header-role" id="userRoleDisplay"></div>
                </div>
                <button class="btn btn-secondary" onclick="logout()">Salir</button>
            </header>
            
            <nav class="tabs">
                <button class="tab active" onclick="switchTab('pendientes', this)">Pendientes (<span id="pendientesCount">0</span>)</button>
                <button class="tab" onclick="switchTab('en-progreso', this)">En Progreso (<span id="progresoCount">0</span>)</button>
                <button class="tab" onclick="switchTab('completadas', this)">Completadas (<span id="completadasCount">0</span>)</button>
                <button class="tab" onclick="switchTab('historial', this)">Historial</button>
            </nav>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number" id="statPendientes">0</div>
                    <div class="stat-label">Pendientes</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="statProgreso">0</div>
                    <div class="stat-label">En Progreso</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="statCompletadas">0</div>
                    <div class="stat-label">Completadas</div>
                </div>
            </div>
            
            <div class="content">
                <h2 id="sectionTitle">Tareas Pendientes</h2>
                <div id="tasksContainer"></div>
            </div>
            
            <button id="createTaskBtn" class="floating-btn" onclick="openCreateModal()" style="display: none;">+</button>
        </div>
        
        <!-- Modal Crear Tarea -->
        <div id="createTaskModal" class="modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Crear Nueva Tarea</h3>
                    <button class="close-btn" onclick="closeCreateModal()">&times;</button>
                </div>
                <form onsubmit="createTask(event)">
                    <div class="form-group">
                        <label class="form-label">Título *</label>
                        <input type="text" id="taskTitle" class="form-input" required>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Descripción *</label>
                        <textarea id="taskDescription" class="form-textarea" required></textarea>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Turbina</label>
                        <select id="taskTurbine" class="form-select">
                            <option value="">Seleccionar turbina</option>
                            <option value="WTG 01">WTG 01</option>
                            <option value="WTG 02">WTG 02</option>
                            <option value="WTG 03">WTG 03</option>
                            <option value="WTG 04">WTG 04</option>
                            <option value="WTG 05">WTG 05</option>
                            <option value="WTG 06">WTG 06</option>
                            <option value="WTG 07">WTG 07</option>
                            <option value="WTG 08">WTG 08</option>
                            <option value="WTG 09">WTG 09</option>
                            <option value="WTG 10">WTG 10</option>
                            <option value="WTG 11">WTG 11</option>
                            <option value="WTG 12">WTG 12</option>
                            <option value="WTG 13">WTG 13</option>
                            <option value="WTG 14">WTG 14</option>
                            <option value="WTG 15">WTG 15</option>
                            <option value="WTG 16">WTG 16</option>
                            <option value="WTG 17">WTG 17</option>
                            <option value="WTG 18">WTG 18</option>
                            <option value="WTG 19">WTG 19</option>
                            <option value="WTG 20">WTG 20</option>
                            <option value="WTG 21">WTG 21</option>
                            <option value="WTG 22">WTG 22</option>
                            <option value="WTG 23">WTG 23</option>
                            <option value="WTG 24">WTG 24</option>
                            <option value="WTG 25">WTG 25</option>
                            <option value="WTG 26">WTG 26</option>
                            <option value="WTG 27">WTG 27</option>
                            <option value="WTG 28">WTG 28</option>
                            <option value="WTG 29">WTG 29</option>
                            <option value="WTG 30">WTG 30</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Prioridad</label>
                        <select id="taskPriority" class="form-select">
                            <option value="baja">Baja</option>
                            <option value="media" selected>Media</option>
                            <option value="alta">Alta</option>
                        </select>
                    </div>
                    <button type="submit" class="btn btn-primary" style="width: 100%; padding: 12px;">✅ Crear Tarea</button>
                </form>
            </div>
        </div>
    </div>
    
    <script>
        let currentUser = null;
        let currentView = 'pendientes';
        let tasks = [];
        
        function selectRole(role) {
            currentUser = role;
            document.getElementById('roleSelection').style.display = 'none';
            document.getElementById('passwordSection').style.display = 'block';
            document.getElementById('passwordLabel').textContent = 
                `Ingresa la contraseña para ${role === 'admin' ? 'Administrador' : 'Técnico'}:`;
            document.getElementById('passwordInput').focus();
        }
        
        function goBack() {
            document.getElementById('roleSelection').style.display = 'block';
            document.getElementById('passwordSection').style.display = 'none';
            document.getElementById('passwordInput').value = '';
        }
        
        function login() {
            const password = document.getElementById('passwordInput').value;
            
            fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ role: currentUser, password: password })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('loginScreen').style.display = 'none';
                    document.getElementById('mainApp').style.display = 'block';
                    document.getElementById('userRoleDisplay').textContent = 
                        `${currentUser === 'admin' ? '👨‍💼 Administrador' : '🔧 Técnico'}`;
                    
                    if (currentUser === 'admin') {
                        document.getElementById('createTaskBtn').style.display = 'block';
                    }
                    
                    loadTasks();
                } else {
                    alert('Contraseña incorrecta');
                    document.getElementById('passwordInput').value = '';
                }
            });
        }
        
        function logout() {
            fetch('/api/logout', { method: 'POST' })
            .then(() => {
                document.getElementById('loginScreen').style.display = 'block';
                document.getElementById('mainApp').style.display = 'none';
                currentUser = null;
                goBack();
            });
        }
        
        function loadTasks() {
            fetch('/api/tasks')
            .then(response => response.json())
            .then(data => {
                tasks = data;
                updateStats();
                displayTasks();
            });
        }
        
        function updateStats() {
            const pendientes = tasks.filter(t => t.status === 'pendiente').length;
            const progreso = tasks.filter(t => t.status === 'en-progreso').length;
            const completadas = tasks.filter(t => t.status === 'completada' && !t.is_old).length;
            
            document.getElementById('statPendientes').textContent = pendientes;
            document.getElementById('statProgreso').textContent = progreso;
            document.getElementById('statCompletadas').textContent = completadas;
            
            document.getElementById('pendientesCount').textContent = pendientes;
            document.getElementById('progresoCount').textContent = progreso;
            document.getElementById('completadasCount').textContent = completadas;
        }
        
        function switchTab(view, element) {
            currentView = view;
            
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            element.classList.add('active');
            
            const titles = {
                'pendientes': 'Tareas Pendientes',
                'en-progreso': 'Tareas en Progreso', 
                'completadas': 'Tareas Completadas (Últimos 30 días)',
                'historial': 'Historial Completo'
            };
            document.getElementById('sectionTitle').textContent = titles[view];
            
            displayTasks();
        }
        
        function displayTasks() {
            const container = document.getElementById('tasksContainer');
            container.innerHTML = '';
            
            const filteredTasks = getFilteredTasks();
            
            if (filteredTasks.length === 0) {
                container.innerHTML = '<p style="text-align: center; color: #6B7280; padding: 40px;">No hay tareas en esta sección</p>';
                return;
            }
            
            filteredTasks.forEach(task => {
                const taskDiv = createTaskCard(task);
                container.appendChild(taskDiv);
            });
        }
        
        function getFilteredTasks() {
            if (currentView === 'historial') {
                return tasks.filter(task => task.status === 'completada');
            } else if (currentView === 'completadas') {
                return tasks.filter(task => task.status === 'completada' && !task.is_old);
            } else {
                return tasks.filter(task => task.status === currentView);
            }
        }
        
        function createTaskCard(task) {
            const div = document.createElement('div');
            div.className = `task-card priority-${task.priority}`;
            
            const evidenceHtml = task.evidence ? 
                `<div class="task-evidence">✅ ${task.evidence}</div>` : '';
            
            const actionsHtml = createTaskActions(task);
            
            div.innerHTML = `
                <div class="task-header">
                    <div class="task-title">${task.title}</div>
                    <div class="task-status status-${task.status}">${task.status}</div>
                </div>
                <div class="task-body">
                    <div class="task-description">${task.description}</div>
                    <div class="task-info">
                        🔧 ${task.turbine || 'Sin asignar'} | 
                        ⚡ Prioridad ${task.priority} | 
                        📋 Creada: ${task.created_at}
                        ${task.completed_at ? ` | ✅ Completada: ${task.completed_at}` : ''}
                    </div>
                    ${evidenceHtml}
                    <div class="task-actions">${actionsHtml}</div>
                </div>
            `;
            
            return div;
        }
        
        function createTaskActions(task) {
            let html = '';
            
            if (currentUser === 'technician' && task.status !== 'completada') {
                if (task.status === 'pendiente') {
                    html += `<button class="task-btn btn-start" onclick="updateTaskStatus(${task.id}, 'en-progreso')">▶️ Iniciar</button>`;
                }
                if (task.status === 'en-progreso') {
                    html += `<button class="task-btn btn-evidence" onclick="uploadEvidence(${task.id})">📁 Subir Evidencia</button>`;
                }
            }
            
            if (currentUser === 'admin') {
                html += `<button class="task-btn btn-delete" onclick="deleteTask(${task.id})">🗑️ Eliminar</button>`;
            }
            
            return html;
        }
        
        function openCreateModal() {
            document.getElementById('createTaskModal').style.display = 'block';
        }
        
        function closeCreateModal() {
            document.getElementById('createTaskModal').style.display = 'none';
            document.getElementById('taskTitle').value = '';
            document.getElementById('taskDescription').value = '';
            document.getElementById('taskTurbine').value = '';
            document.getElementById('taskPriority').value = 'media';
        }
        
        function createTask(event) {
            event.preventDefault();
            
            const title = document.getElementById('taskTitle').value;
            const description = document.getElementById('taskDescription').value;
            const turbine = document.getElementById('taskTurbine').value;
            const priority = document.getElementById('taskPriority').value;
            
            fetch('/api/tasks', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title, description, turbine, priority })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    closeCreateModal();
                    loadTasks();
                    alert('¡Tarea creada correctamente!');
                } else {
                    alert('Error al crear la tarea');
                }
            });
        }
        
        function updateTaskStatus(taskId, newStatus) {
            fetch(`/api/tasks/${taskId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status: newStatus })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    loadTasks();
                    alert(`Tarea marcada como ${newStatus}`);
                }
            });
        }
        
        function uploadEvidence(taskId) {
            const filename = `evidencia_${taskId}_${new Date().toISOString().slice(0,10)}.jpg`;
            
            fetch(`/api/tasks/${taskId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status: 'completada', evidence: filename })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    loadTasks();
                    alert('¡Evidencia subida y tarea completada!');
                }
            });
        }
        
        function deleteTask(taskId) {
            if (confirm('¿Estás seguro de eliminar esta tarea?')) {
                fetch(`/api/tasks/${taskId}`, { method: 'DELETE' })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        loadTasks();
                        alert('Tarea eliminada correctamente');
                    }
                });
            }
        }
        
        // Cerrar modal al hacer clic fuera
        window.onclick = function(event) {
            const modal = document.getElementById('createTaskModal');
            if (event.target === modal) {
                closeCreateModal();
            }
        }
        
        // Enter para login
        document.addEventListener('DOMContentLoaded', function() {
            document.getElementById('passwordInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    login();
                }
            });
        });
    </script>
</body>
</html>
'''

@app.route('/api/login', methods=['POST'])
def login_api():
    """Endpoint para login"""
    data = request.json
    role = data.get('role')
    password = data.get('password')
    
    if role in PASSWORDS and PASSWORDS[role] == password:
        session['authenticated'] = True
        session['role'] = role
        return jsonify({'success': True, 'role': role})
    else:
        return jsonify({'success': False, 'message': 'Contraseña incorrecta'})

@app.route('/api/logout', methods=['POST'])
def logout_api():
    """Endpoint para logout"""
    session.clear()
    return jsonify({'success': True})

@app.route('/api/tasks', methods=['GET'])
def get_tasks_api():
    """Obtener todas las tareas"""
    if not session.get('authenticated'):
        return jsonify({'error': 'No autenticado'}), 401
    
    tasks = load_tasks()
    
    # Agregar información de si la tarea es antigua
    for task in tasks:
        task['is_old'] = is_older_than_30_days(task.get('completed_at'))
    
    return jsonify(tasks)

@app.route('/api/tasks', methods=['POST'])
def create_task_api():
    """Crear nueva tarea"""
    if not session.get('authenticated') or session.get('role') != 'admin':
        return jsonify({'error': 'No autorizado'}), 403
    
    data = request.json
    
    if not data.get('title') or not data.get('description'):
        return jsonify({'error': 'Título y descripción son obligatorios'}), 400
    
    tasks = load_tasks()
    
    new_task = {
        'id': len(tasks) + 1,
        'title': data['title'],
        'description': data['description'],
        'turbine': data.get('turbine', ''),
        'priority': data.get('priority', 'media'),
        'status': 'pendiente',
        'evidence': None,
        'created_at': datetime.now().strftime('%Y-%m-%d'),
        'completed_at': None
    }
    
    tasks.append(new_task)
    save_tasks(tasks)
    
    return jsonify({'success': True, 'task_id': new_task['id']})

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task_api(task_id):
    """Actualizar tarea"""
    if not session.get('authenticated'):
        return jsonify({'error': 'No autenticado'}), 401
    
    data = request.json
    tasks = load_tasks()
    
    for task in tasks:
        if task['id'] == task_id:
            if 'status' in data:
                task['status'] = data['status']
                if data['status'] == 'completada':
                    task['completed_at'] = datetime.now().strftime('%Y-%m-%d')
            
            if 'evidence' in data:
                task['evidence'] = data['evidence']
                task['status'] = 'completada'
                task['completed_at'] = datetime.now().strftime('%Y-%m-%d')
            
            break
    
    save_tasks(tasks)
    return jsonify({'success': True})

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task_api(task_id):
    """Eliminar tarea"""
    if not session.get('authenticated') or session.get('role') != 'admin':
        return jsonify({'error': 'No autorizado'}), 403
    
    tasks = load_tasks()
    tasks = [task for task in tasks if task['id'] != task_id]
    save_tasks(tasks)
    
    return jsonify({'success': True})

if __name__ == '__main__':
    print("🌪️ Iniciando servidor del Parque Eólico...")
    print("📱 Acceso local: http://localhost:5000")
    print("📱 Para celulares: http://TU_IP:5000")
    print("⚠️  Presiona Ctrl+C para detener")
    
    # Ejecutar servidor
    app.run(debug=True, host='0.0.0.0', port=5000)