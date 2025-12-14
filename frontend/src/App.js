// frontend/src/App.js
import React, { useState, useEffect } from 'react';
import './App.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [tasks, setTasks] = useState([]);
  const [newTask, setNewTask] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/api/tasks`);
      if (!response.ok) throw new Error('Failed to fetch tasks');
      const data = await response.json();
      setTasks(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const addTask = async (e) => {
    e.preventDefault();
    if (!newTask.trim()) return;

    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/api/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: newTask, completed: false })
      });
      if (!response.ok) throw new Error('Failed to add task');
      const data = await response.json();
      setTasks([...tasks, data]);
      setNewTask('');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const toggleTask = async (id, completed) => {
    setError(null);
    try {
      const response = await fetch(`${API_URL}/api/tasks/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ completed: !completed })
      });
      if (!response.ok) throw new Error('Failed to update task');
      const data = await response.json();
      setTasks(tasks.map(t => t.id === id ? data : t));
    } catch (err) {
      setError(err.message);
    }
  };

  const deleteTask = async (id) => {
    setError(null);
    try {
      const response = await fetch(`${API_URL}/api/tasks/${id}`, {
        method: 'DELETE'
      });
      if (!response.ok) throw new Error('Failed to delete task');
      setTasks(tasks.filter(t => t.id !== id));
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>📝 Task Management System</h1>
        <p className="subtitle">Deployed with Blue-Green Strategy on AKS</p>
      </header>

      <main className="container">
        {error && (
          <div className="error-banner">
            ⚠️ {error}
          </div>
        )}

        <form onSubmit={addTask} className="task-form">
          <input
            type="text"
            value={newTask}
            onChange={(e) => setNewTask(e.target.value)}
            placeholder="Enter a new task..."
            disabled={loading}
            className="task-input"
          />
          <button type="submit" disabled={loading} className="add-button">
            {loading ? '⏳ Adding...' : '➕ Add Task'}
          </button>
        </form>

        <div className="tasks-container">
          <h2>Tasks ({tasks.length})</h2>
          {loading && tasks.length === 0 ? (
            <div className="loading">Loading tasks...</div>
          ) : tasks.length === 0 ? (
            <div className="empty-state">
              <p>No tasks yet. Add one to get started! 🚀</p>
            </div>
          ) : (
            <ul className="task-list">
              {tasks.map(task => (
                <li key={task.id} className={`task-item ${task.completed ? 'completed' : ''}`}>
                  <input
                    type="checkbox"
                    checked={task.completed}
                    onChange={() => toggleTask(task.id, task.completed)}
                    className="task-checkbox"
                  />
                  <span className="task-title">{task.title}</span>
                  <button
                    onClick={() => deleteTask(task.id)}
                    className="delete-button"
                    title="Delete task"
                  >
                    🗑️
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>

        <footer className="app-footer">
          <p>🔵 Blue-Green Deployment | 🐳 Docker | ☸️ Kubernetes | 🔄 GitHub Actions</p>
        </footer>
      </main>
    </div>
  );
}

export default App;<!-- trigger -->
