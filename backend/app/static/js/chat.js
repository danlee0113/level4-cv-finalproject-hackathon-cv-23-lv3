// 전역 변수 설정
const botImagePath = "/static/images/chart-icon.png";  // 챗봇 프로필 이미지 경로
let userId = "";  // 사용자 ID (HTML에서 동적으로 설정됨)
let currentSessionId = null;  // 현재 활성화된 채팅 세션 ID

// 채팅창을 항상 최신 메시지가 보이도록 스크롤
function scrollToBottom() {
  const messageBody = document.getElementById("messageContainer");
  messageBody.scrollTop = messageBody.scrollHeight;
}

// 특정 채팅 세션의 이전 메시지들을 불러오는 함수
function loadMessages(sessionId) {
  $.ajax({
    url: `/chats/${sessionId}/messages`,
    type: "GET",
    success: function(data) {
      $("#messageContainer").empty();  // 기존 메시지 초기화
      data.forEach(msg => {
        // UTC 시간을 한국 시간으로 변환
        const date = new Date(msg.created_at + 'Z');
        const timeStr = date.toLocaleTimeString('ko-KR', {
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
          hour12: false
        });

        // 발신자에 따라 다른 메시지 스타일 적용
        if (msg.sender_role === "user") {
          // 사용자 메시지 (오른쪽)
          let userHtml = `<div class="d-flex justify-content-end mb-4"><div class="msg_container_send" style="max-width:60%; padding:15px;">${msg.message}<span class="msg_time_send">${timeStr}</span></div><div class="icon_cont_msg"><i class="fas fa-user"></i></div></div>`;
          $("#messageContainer").append(userHtml);
        } else {
          // 봇 메시지 (왼쪽)
          let botHtml = `<div class="d-flex justify-content-start mb-4"><div class="img_cont_msg"><img src="${botImagePath}" class="rounded-circle user_img_msg" /></div><div class="msg_container" style="max-width:60%; padding:15px;">${msg.message}<span class="msg_time">${timeStr}</span></div></div>`;
          $("#messageContainer").append(botHtml);
        }
      });
      scrollToBottom();
    },
    error: function() {
      alert("Failed to load messages.");
    }
  });
}

// 새로운 채팅 세션 생성 함수
function createNewSession(callback) {
  if (!userId) {
    alert("User ID is missing; cannot create session.");
    return;
  }
  $.ajax({
    url: "/chats/",
    type: "POST",
    data: { user_id: userId },
    success: function(res) {
      currentSessionId = res.chat_session_id;
      // 새 세션을 목록 최상단에 추가
      $("#sessionList").prepend(`
        <li class="session-item">
          <button class="session-button" data-session-id="${currentSessionId}">
            <i class="far fa-comment-alt nav__icon"></i>
            새로운 채팅
          </button>
        </li>
      `);
      // 새로 생성된 세션 버튼에 클릭 이벤트 추가
      $("#sessionList .session-button").first().on("click", function() {
        currentSessionId = $(this).data("session-id");
        loadMessages(currentSessionId);
      });
      if (callback) callback();
    },
    error: function(xhr) {
      alert("Failed to create a new session. Error: " + xhr.responseText);
    }
  });
}

// 실제 메시지 전송 처리 함수
function actuallySendMessage(rawText) {
  // 현재 시간 포맷팅
  const date = new Date();
  const timeStr = date.toLocaleTimeString('ko-KR', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  });

  // 사용자 메시지 표시
  let userHtml = `<div class="d-flex justify-content-end mb-4 user-message-animation"><div class="msg_container_send" style="max-width:60%; padding:15px;">${rawText}<span class="msg_time_send">${timeStr}</span></div><div class="icon_cont_msg"><i class="fas fa-user"></i></div></div>`;
  $("#messageInput").val("").height("40px");
  $("#messageContainer").append(userHtml);
  
  // 봇 응답 대기 표시 (타이핑 애니메이션)
  let typingIndicator = `
    <div class="d-flex justify-content-start mb-4 typing-message">
      <div class="img_cont_msg">
        <img src="${botImagePath}" class="rounded-circle user_img_msg" />
      </div>
      <div class="msg_container typing-indicator">
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
      </div>
    </div>
  `;
  $("#messageContainer").append(typingIndicator);
  scrollToBottom();

  // 서버에 메시지 전송
  $.ajax({
    url: `/chats/${currentSessionId}/messages`,
    type: "POST",
    contentType: "application/json",
    data: JSON.stringify({ sender_role: "user", message: rawText }),
    success: function(res) {
      // 타이핑 표시 제거
      $(".typing-message").remove();
      
      // 봇 응답 메시지 표시
      const timeStr = new Date().toLocaleTimeString('ko-KR', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
      });

      let botMsg = res.message;
      let botHtml = `<div class="d-flex justify-content-start mb-4 bot-message-animation"><div class="img_cont_msg"><img src="${botImagePath}" class="rounded-circle user_img_msg" /></div><div class="msg_container" style="max-width:60%; padding:15px;">${botMsg}<span class="msg_time">${timeStr}</span></div></div>`;
      $("#messageContainer").append(botHtml);
      scrollToBottom();
    },
    error: function() {
      $(".typing-message").remove();
      alert("Failed to send message.");
    }
  });
}

// 메시지 전송 시작 함수
function sendMessage() {
  const textarea = $("#messageInput");
  const rawText = textarea.val().trim();
  if (!rawText) return;

  // 세션이 없는 경우 새로 생성 후 메시지 전송
  if (!currentSessionId) {
    createNewSession(() => {
      actuallySendMessage(rawText);
    });
  } else {
    actuallySendMessage(rawText);
  }
}

// DOM 로드 완료 후 이벤트 핸들러 설정
$(document).ready(function() {
  // 채팅 세션 선택 이벤트
  $(".session-button").on("click", function() {
    currentSessionId = $(this).data("session-id");
    loadMessages(currentSessionId);
  });

  const textarea = $("#messageInput");

  // 텍스트 입력 처리 (Shift+Enter: 줄바꿈, Enter: 전송)
  textarea.on("keydown", function(e) {
    if (e.key === "Enter") {
      if (e.shiftKey) {
        // Shift+Enter: 줄바꿈 삽입
        const cursorPos = this.selectionStart;
        const val = $(this).val();
        $(this).val(val.substring(0, cursorPos) + "\n" + val.substring(cursorPos));
        this.selectionStart = this.selectionEnd = cursorPos + 1;
        e.preventDefault();
      } else {
        // Enter: 메시지 전송
        e.preventDefault();
        sendMessage();
      }
    }
  });

  // 텍스트 입력창 자동 높이 조절
  textarea.on("input", function() {
    this.style.height = "auto";
    if (this.scrollHeight > 200) {
      this.style.height = "200px";
      this.style.overflowY = "scroll";
    } else {
      this.style.height = this.scrollHeight + "px";
      this.style.overflowY = "hidden";
    }
  });

  // 폼 제출 이벤트 처리
  $("#messageForm").on("submit", function(e) {
    e.preventDefault();
    sendMessage();
  });

  // 전송 버튼 클릭 이벤트
  $("#sendButton").on("click", function() {
    sendMessage();
  });

  // 프로필 드롭다운 메뉴 관련 이벤트
  $('.user-profile .icon-container').click(function(e) {
    e.stopPropagation();
    $('.dropdown-menu').toggle();
  });

  // 문서 클릭 시 드롭다운 메뉴 닫기
  $(document).click(function() {
    $('.dropdown-menu').hide();
  });

  // 드롭다운 메뉴 내부 클릭 이벤트 전파 방지
  $('.dropdown-menu').click(function(e) {
    e.stopPropagation();
  });
});
