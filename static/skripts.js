document.addEventListener('DOMContentLoaded', function() {
    const authBtn = document.querySelector('.auth-btn');
    const registerBtn = document.querySelector('.register-btn');
    const loginForm = document.querySelector('.login-form');
    const registerForm = document.querySelector('.register-form');

    authBtn.addEventListener('click', function(event) {
        event.preventDefault();
        loginForm.classList.toggle('hidden');
        registerForm.classList.add('hidden');
    });

    registerBtn.addEventListener('click', function(event) {
        event.preventDefault();
        registerForm.classList.toggle('hidden');
        loginForm.classList.add('hidden');
    });
});

document.addEventListener('DOMContentLoaded', () => {
  const animatedHeader = document.querySelector('.animated-header');

  // Анимация заголовка при появлении на экране
  const fadeIn = () => {
    animatedHeader.style.opacity = '1';
    animatedHeader.style.transform = 'translateY(0)';
  };

  setTimeout(fadeIn, 500);
});

// JavaScript для отображения сообщения после изменения пароля
    var form = document.getElementById('change-password-form');
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        fetch('/change_password', {
            method: 'POST',
            body: new FormData(form)
        })
        .then(response => response.text())
        .then(data => {
            if (data === 'Пароль успешно изменен') {
                var message = document.getElementById('password-change-message');
                message.style.display = 'block';
            } else {
                alert(data); // Показать другие сообщения об ошибках, если есть
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
        });
    });

