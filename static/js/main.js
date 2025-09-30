// Modal functionality
function createNewQuestionnaire() {
    const modal = document.getElementById('createModal');
    if (modal) {
        modal.style.display = 'block';
    }
}

function closeModal() {
    const modal = document.getElementById('createModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('createModal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
}

// Form submission
const form = document.getElementById('questionnaireForm');
if (form) {
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const title = document.getElementById('title').value;
        const description = document.getElementById('description').value;
        
        try {
            const response = await fetch('/api/questions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    title: title,
                    description: description,
                    questions: []
                })
            });
            
            if (response.ok) {
                alert('Questionnaire created successfully!');
                window.location.reload();
            } else {
                alert('Error creating questionnaire');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error creating questionnaire');
        }
    });
}

// View questionnaire
function viewQuestionnaire(id) {
    fetch(`/api/questions/${id}`)
        .then(response => response.json())
        .then(data => {
            alert(`Questionnaire: ${data.title}\nDescription: ${data.description}`);
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error viewing questionnaire');
        });
}

// Delete questionnaire
function deleteQuestionnaire(id) {
    if (confirm('Are you sure you want to delete this questionnaire?')) {
        fetch(`/api/questions/${id}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            alert('Questionnaire deleted successfully!');
            window.location.reload();
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error deleting questionnaire');
        });
    }
}

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth'
            });
        }
    });
});
