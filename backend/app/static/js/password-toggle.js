function togglePassword(inputId, toggleId) {
    const passwordInput = document.getElementById(inputId);
    const toggleButton = document.getElementById(toggleId);
    
    toggleButton.addEventListener('click', function() {
        const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordInput.setAttribute('type', type);
        
        // 아이콘 변경
        toggleButton.querySelector('i').classList.toggle('fa-eye');
        toggleButton.querySelector('i').classList.toggle('fa-eye-slash');
    });
}

document.addEventListener('DOMContentLoaded', function() {
    // 페이지에 있는 모든 비밀번호 필드에 대해 토글 기능 초기화
    const passwordFields = document.querySelectorAll('input[type="password"]');
    passwordFields.forEach((field, index) => {
        const id = `password-${index}`;
        const toggleId = `toggle-${id}`;
        field.id = id;
        
        // 토글 버튼 추가
        const toggleButton = document.createElement('button');
        toggleButton.type = 'button';
        toggleButton.id = toggleId;
        toggleButton.className = 'password-toggle-btn';
        toggleButton.innerHTML = '<i class="fas fa-eye"></i>';
        
        field.parentNode.style.position = 'relative';
        field.parentNode.appendChild(toggleButton);
        
        togglePassword(id, toggleId);
    });
}); 