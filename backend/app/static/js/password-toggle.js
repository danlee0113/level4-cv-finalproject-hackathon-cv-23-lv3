function togglePassword(inputId, toggleId) {
    // 비밀번호 입력 필드와 토글 버튼 요소 가져오기
    const passwordInput = document.getElementById(inputId);
    const toggleButton = document.getElementById(toggleId);
    
    // 토글 버튼 클릭 이벤트 리스너 추가
    toggleButton.addEventListener('click', function() {
        // 현재 input type이 password면 text로, text면 password로 변경
        const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordInput.setAttribute('type', type);
        
        // 아이콘 변경 (눈 모양 아이콘 토글)
        toggleButton.querySelector('i').classList.toggle('fa-eye');
        toggleButton.querySelector('i').classList.toggle('fa-eye-slash');
    });
}

// DOM이 완전히 로드된 후 실행
document.addEventListener('DOMContentLoaded', function() {
    // 페이지 내의 모든 비밀번호 입력 필드 선택
    const passwordFields = document.querySelectorAll('input[type="password"]');
    
    // 각 비밀번호 필드에 대해 토글 기능 초기화
    passwordFields.forEach((field, index) => {
        // 고유 ID 생성
        const id = `password-${index}`;
        const toggleId = `toggle-${id}`;
        field.id = id;
        
        // 토글 버튼 생성 및 설정
        const toggleButton = document.createElement('button');
        toggleButton.type = 'button';
        toggleButton.id = toggleId;
        toggleButton.className = 'password-toggle-btn';
        toggleButton.innerHTML = '<i class="fas fa-eye"></i>';  // 기본 아이콘 설정
        
        // 부모 요소에 상대 위치 설정 및 토글 버튼 추가
        field.parentNode.style.position = 'relative';
        field.parentNode.appendChild(toggleButton);
        
        // 토글 기능 초기화
        togglePassword(id, toggleId);
    });
}); 