function toggleForm() {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');

    loginForm.classList.toggle('hidden');
    registerForm.classList.toggle('hidden');


}

// Form validation
document.addEventListener('DOMContentLoaded', function () {
    const forms = document.querySelectorAll('form');

    forms.forEach(form => {
        form.addEventListener('submit', function (e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;

            // Show loading state
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Procesando...';
        });
    });

    // Password confirmation validation for register form
    const registerForm = document.getElementById('registerForm');
    const password = registerForm.querySelector('input[name="password"]');
    const confirmPassword = registerForm.querySelector('input[name="confirm_password"]');

    confirmPassword.addEventListener('input', function () {
        if (password.value !== confirmPassword.value) {
            confirmPassword.setCustomValidity('Las Credenciales no coinciden');
        } else {
            confirmPassword.setCustomValidity('');
        }
    });

    // Auto-hide error messages
    const errorMessages = document.querySelectorAll('.error-message');
    errorMessages.forEach(msg => {
        setTimeout(() => {
            msg.style.animation = 'fadeOut 0.5s ease-out forwards';
            setTimeout(() => msg.remove(), 500);
        }, 5000);
    });
});

// Service Worker
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register("{% static 'service-worker.js' %}")
        .then(reg => console.log("Service Worker registrado:", reg))
        .catch(err => console.error("Fallo al registrar Service Worker:", err));
}