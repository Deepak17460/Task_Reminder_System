// Toast notification system
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    const bgColor = {
        success: 'bg-green-600',
        error: 'bg-red-600',
        info: 'bg-blue-600',
        warning: 'bg-yellow-600'
    }[type] || 'bg-gray-600';

    toast.className = `toast ${bgColor} text-white px-4 py-2 rounded-lg shadow-md flex items-center space-x-2 max-w-sm`;
    toast.innerHTML = `
        <span class="text-sm">${escapeHtml(message)}</span>
        <button onclick="removeToast(this.parentElement)" class="text-white/80 hover:text-white">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
        </button>
    `;

    container.appendChild(toast);
    setTimeout(() => removeToast(toast), 5000);
}

function removeToast(toast) {
    if (toast && toast.parentNode) {
        toast.classList.add('removing');
        setTimeout(() => toast.parentNode && toast.remove(), 300);
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Toggle add task form
function toggleAddTask() {
    const form = document.getElementById('add-task-form');
    if (form) {
        form.classList.toggle('hidden');
        if (!form.classList.contains('hidden')) {
            const input = form.querySelector('input[name="description"]');
            input && input.focus();
        }
    }
}

// Handle form submissions with AJAX
function handleFormSubmit(event, action) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const url = form.action;

    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Processing...';
    }

    fetch(url, {
        method: 'POST',
        body: formData,
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(data => {
            showToast(data.message, data.status);
            if (data.status === 'success') {
                if (action === 'add') {
                    form.reset();
                    toggleAddTask();
                }
                setTimeout(() => location.reload(), 1000);
            }
        })
        .catch(error => {
            console.error('Error during form submission:', action, error);
            showToast('Form submission failed.', 'error');
        })
        .finally(() => {
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = action === 'add' ? 'Create Task' : 'Update';
            }
        });
}

// Handle action clicks with AJAX
function handleAction(event, action, taskId) {
    event.preventDefault();
    const url = event.currentTarget.href;

    if (!url) {
        showToast(`Failed to ${action} task #${taskId}.`, 'error');
        return;
    }

    fetch(url, {
        method: 'GET',
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(data => {
            showToast(data.message, data.status);
            if (data.status === 'success') {
                setTimeout(() => location.reload(), 1000);
            }
        })
        .catch(error => {
            console.error('Error during action:', action, taskId, error);
            showToast(`Failed to ${action} task #${taskId}.`, 'error');
        });
}

// Toggle edit form
function toggleEdit(taskId) {
    const editForm = document.getElementById(`edit-form-${taskId}`);
    if (editForm) {
        editForm.classList.toggle('hidden');
        if (!editForm.classList.contains('hidden')) {
            const firstInput = editForm.querySelector('input[name="description"]');
            firstInput && setTimeout(() => firstInput.focus(), 100);
        }
    }
}

// Filter tasks
function filterTasks(filter) {
    const tasks = document.querySelectorAll('.task-card');
    const filterBtns = document.querySelectorAll('.filter-btn');

    filterBtns.forEach(btn => {
        btn.classList.remove('active', 'bg-blue-600', 'text-white');
        btn.classList.add('text-a5adba', 'hover:bg-gray-700');
    });

    const activeBtn = document.querySelector(`[data-filter="${filter}"]`);
    if (activeBtn) {
        activeBtn.classList.add('active', 'bg-blue-600', 'text-white');
        activeBtn.classList.remove('hover:bg-gray-700', 'text-a5adba');
    }

    let visibleCount = 0;
    tasks.forEach(task => {
        const completed = task.dataset.completed === 'true';
        const priority = task.dataset.priority;

        let show = false;
        switch (filter) {
            case 'all': show = true; break;
            case 'pending': show = !completed; break;
            case 'completed': show = completed; break;
            case 'high': show = priority === 'high'; break;
        }

        task.style.display = show ? 'flex' : 'none';
        if (show) {
            task.style.animationDelay = `${visibleCount * 50}ms`;
            task.classList.add('fade-in');
            visibleCount++;
        }
    });

    updateStats();
    showToast(`Showing ${filter.charAt(0).toUpperCase() + filter.slice(1)} Tasks (${visibleCount})`, 'info');
}

// Update stats
function updateStats() {
    const allTasks = document.querySelectorAll('.task-card');
    const completed = document.querySelectorAll('.task-card[data-completed="true"]').length;
    const pending = allTasks.length - completed;
    const highPriority = document.querySelectorAll('.task-card[data-priority="high"]').length;

    animateNumber('total-tasks', allTasks.length);
    animateNumber('completed-tasks', completed);
    animateNumber('pending-tasks', pending);
    animateNumber('high-priority-tasks', highPriority);
}

// Animate number changes
function animateNumber(elementId, targetNumber) {
    const element = document.getElementById(elementId);
    if (!element) return;

    const currentNumber = parseInt(element.textContent) || 0;
    if (currentNumber === targetNumber) return;

    const increment = targetNumber > currentNumber ? 1 : -1;
    let current = currentNumber;

    const interval = setInterval(() => {
        current += increment;
        element.textContent = current;
        if (current === targetNumber) clearInterval(interval);
    }, 50);
}

// Real-time search
function initSearch() {
    const searchInput = document.getElementById('search-tasks');
    if (searchInput) {
        searchInput.addEventListener('input', () => {
            const query = searchInput.value.toLowerCase();
            const tasks = document.querySelectorAll('.task-card');
            let visibleCount = 0;

            tasks.forEach(task => {
                const description = task.querySelector('h3').textContent.toLowerCase();
                const show = description.includes(query);
                task.style.display = show ? 'flex' : 'none';
                if (show) visibleCount++;
            });

            updateStats();
            showToast(`Found ${visibleCount} tasks`, 'info');
        });
    }
}

// Drag-and-drop functionality
function initDragAndDrop() {
    const taskList = document.getElementById('task-list');
    if (!taskList) return;

    let draggedItem = null;

    taskList.addEventListener('dragstart', e => {
        draggedItem = e.target.closest('.task-card');
        if (draggedItem) {
            draggedItem.style.opacity = '0.5';
        }
    });

    taskList.addEventListener('dragend', e => {
        if (draggedItem) {
            draggedItem.style.opacity = '1';
            draggedItem = null;
        }
    });

    taskList.addEventListener('dragover', e => {
        e.preventDefault();
    });

    taskList.addEventListener('drop', e => {
        e.preventDefault();
        if (!draggedItem) return;

        const dropTarget = e.target.closest('.task-card');
        if (!dropTarget || dropTarget === draggedItem) return;

        const taskList = document.getElementById('task-list');
        const allTasks = Array.from(taskList.querySelectorAll('.task-card'));
        const draggedIndex = allTasks.indexOf(draggedItem);
        const dropIndex = allTasks.indexOf(dropTarget);

        if (draggedIndex < dropIndex) {
            taskList.insertBefore(draggedItem, dropTarget.nextSibling);
        } else {
            taskList.insertBefore(draggedItem, dropTarget);
        }

        // Placeholder for backend reorder (requires endpoint)
        const taskIds = Array.from(taskList.querySelectorAll('.task-card')).map(task => task.dataset.taskId);
        fetch('/reorder', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({ taskIds })
        })
            .then(response => response.json())
            .then(data => showToast(data.message, data.status))
            .catch(() => showToast('Failed to reorder tasks', 'error'));
    });
}

// Initialize keyboard shortcuts
function initKeyboardShortcuts() {
    document.addEventListener('keydown', event => {
        if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') return;

        if ((event.ctrlKey || event.metaKey) && event.key === 'c') {
            toggleAddTask();
            event.preventDefault();
        }

        if (event.key === 'Escape') {
            const visibleEditForms = document.querySelectorAll('.edit-form:not(.hidden)');
            visibleEditForms.forEach(form => {
                const taskId = form.id.split('-')[2];
                toggleEdit(taskId);
            });
            toggleAddTask();
        }

        if (event.key >= '1' && event.key <= '4') {
            const filters = ['all', 'pending', 'completed', 'high'];
            filterTasks(filters[parseInt(event.key) - 1]);
            event.preventDefault();
        }
    });
}
// Initialize sidebar toggle
function initSidebarToggle() {
    const toggleButton = document.getElementById('toggle-sidebar');
    const sidebarIcon = document.getElementById('sidebar-icon');
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('main-content');
    const sidebarTexts = document.querySelectorAll('.sidebar-text');

    if (!toggleButton || !sidebarIcon || !sidebar || !mainContent) {
        console.error('One or more sidebar toggle elements not found');
        return;
    }

    toggleButton.addEventListener('click', () => {
        console.log('Toggle button clicked');
        const isCollapsed = sidebar.style.width === '4rem';

        // Toggle sidebar width, background, and main content margin using inline styles
        sidebar.style.width = isCollapsed ? '14rem' : '4rem';
        sidebar.style.backgroundColor = isCollapsed ? '#1F2937' : '#1F2937'; // Match bg-gray-800 (#1F2937)
        mainContent.style.marginLeft = isCollapsed ? '14rem' : '4rem';

        // Toggle text visibility
        sidebarTexts.forEach(text => {
            text.classList.toggle('hidden', !isCollapsed);
        });

        // Toggle icon between hamburger and cross
       sidebarIcon.innerHTML = isCollapsed
            ? `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>` // Right arrow (>)
            : `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 5l-7 7 7 7"/>`
    });
}
// Initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
    updateStats();
    initSearch();
    initDragAndDrop();
    initKeyboardShortcuts();
    initSidebarToggle(); // Added sidebar toggle initialization
    document.querySelectorAll('.task-card').forEach((card, index) => {
        card.style.animationDelay = `${index * 50}ms`;
        card.classList.add('fade-in');
    });

    document.documentElement.style.scrollBehavior = 'smooth';
});

// Global functions
window.showToast = showToast;
window.removeToast = removeToast;
window.handleFormSubmit = handleFormSubmit;
window.handleAction = handleAction;
window.toggleEdit = toggleEdit;
window.filterTasks = filterTasks;
window.updateStats = updateStats;
window.toggleAddTask = toggleAddTask;