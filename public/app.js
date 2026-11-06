// app.js – Task toggle logic for Tarefas da Casa

// Initialize Firebase (the app config is stored in localStorage by existing code)
const firebaseConfig = JSON.parse(localStorage.getItem('firebaseConfig')||'{}');
if (!firebase.apps.length) {
  firebase.initializeApp(firebaseConfig);
}
const db = firebase.database();

// Helper to update UI for a task element
function setTaskChecked(elem, checked) {
  elem.setAttribute('aria-checked', checked ? 'true' : 'false');
  // toggle checkbox visual
  const box = elem.querySelector('.box');
  if (box) {
    if (checked) {
      box.setAttribute('style', 'background:var(--p);border-color:var(--p)');
    } else {
      box.removeAttribute('style');
    }
  }
  // toggle text style
  const txt = elem.querySelector('.txt');
  if (txt) {
    if (checked) {
      txt.style.color = 'var(--done-ink)';
      txt.style.textDecoration = 'line-through';
    } else {
      txt.style.color = '';
      txt.style.textDecoration = '';
    }
  }
}

// Attach click listeners to all existing tasks after DOM load
function attachTaskListeners() {
  const tasks = document.querySelectorAll('.task');
  tasks.forEach(task => {
    // ensure we don't attach multiple times
    task.removeEventListener('click', onTaskClick);
    task.addEventListener('click', onTaskClick);
  });
}

function onTaskClick(event) {
  const taskElem = event.currentTarget;
  const key = taskElem.dataset.key; // assumption: each .task has data-key attribute set when rendered
  if (!key) return; // safety
  const currentlyChecked = taskElem.getAttribute('aria-checked') === 'true';
  const newChecked = !currentlyChecked;
  // Optimistically update UI
  setTaskChecked(taskElem, newChecked);
  // Persist to Firebase
  db.ref('tasks/' + key).update({checked: newChecked});
}

// Listen for realtime updates to keep UI in sync across devices
function listenFirebase() {
  db.ref('tasks').on('value', snapshot => {
    const data = snapshot.val() || {};
    Object.entries(data).forEach(([key, task]) => {
      const elem = document.querySelector(`.task[data-key="${key}"]`);
      if (elem) {
        setTaskChecked(elem, !!task.checked);
      }
    });
  });
}

// Nova função para marcar tarefas atrasadas via modal de alerta
function markLateTaskAsDone(taskKey) {
  const elem = document.querySelector(`.task[data-key="${taskKey}"]`);
  if (elem) setTaskChecked(elem, true);
  // Update Firebase task status to checked
  db.ref('tasks/' + taskKey).update({checked: true}).catch(err => console.error('Erro ao marcar tarefa atrasada:', err));
}

  db.ref('tasks').on('value', snapshot => {
    const data = snapshot.val() || {};
    Object.entries(data).forEach(([key, task]) => {
      const elem = document.querySelector(`.task[data-key="${key}"]`);
      if (elem) {
        setTaskChecked(elem, !!task.checked);
      }
    });
  });
}

// Run after page load
window.addEventListener('load', () => {
  attachTaskListeners();
  listenFirebase();
});
