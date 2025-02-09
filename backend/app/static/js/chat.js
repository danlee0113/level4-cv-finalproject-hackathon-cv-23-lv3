// 봇 아이콘 이미지 (필요 시 사용)
const botImagePath = "/static/images/chart-icon.png";

let userId = "";  // 실제 값은 HTML에서 설정
let currentSessionId = null; // 현재 세션 ID

// 스크롤 하단으로 이동
function scrollToBottom() {
  const messageBody = document.getElementById("messageContainer");
  messageBody.scrollTop = messageBody.scrollHeight;
}

// 특정 세션의 메시지 불러오기
function loadMessages(sessionId) {
  $.ajax({
    url: `/chats/${sessionId}/messages`,
    type: "GET",
    success: function(data) {
      $("#messageContainer").empty();
      data.forEach(msg => {
        // UTC 시간을 로컬 시간으로 변환
        const date = new Date(msg.created_at + 'Z');
        const timeStr = date.toLocaleTimeString('ko-KR', {
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
          hour12: false
        });
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

// 새 세션 생성
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
      // 세션 목록 최상단에 추가
      $("#sessionList").prepend(`
        <li class="session-item">
          <button class="session-button" data-session-id="${currentSessionId}">
            <i class="far fa-comment-alt nav__icon"></i>
            새로운 채팅
          </button>
        </li>
      `);
      // 새 버튼에 이벤트 리스너 추가
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

// 실제 메시지 전송
function actuallySendMessage(rawText) {
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
  
  // 타이핑 표시기 추가
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

  // 서버 POST
  $.ajax({
    url: `/chats/${currentSessionId}/messages`,
    type: "POST",
    contentType: "application/json",
    data: JSON.stringify({ sender_role: "user", message: rawText }),
    success: function(res) {
      // 타이핑 표시기 제거
      $(".typing-message").remove();
      
      const timeStr = new Date().toLocaleTimeString('ko-KR', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
      });

      // 봇 메시지 표시 (애니메이션 클래스 추가)
      let botMsg = res.message;
      let botHtml = `<div class="d-flex justify-content-start mb-4 bot-message-animation"><div class="img_cont_msg"><img src="${botImagePath}" class="rounded-circle user_img_msg" /></div><div class="msg_container" style="max-width:60%; padding:15px;">${botMsg}<span class="msg_time">${timeStr}</span></div></div>`;
      

      //  // marked 라이브러리를 사용하여 Markdown -> HTML 변환
      // let renderedHTML = marked(botMsg); 

      //  // 변환된 HTML을 그대로 삽입하여 메시지 구성
      // let botHtml = `<div class="d-flex justify-content-start mb-4 bot-message-animation"><div class="img_cont_msg"><img src="${botImagePath}" class="rounded-circle user_img_msg" /></div><div class="msg_container" style="max-width:60%; padding:15px;">${renderedHTML}<span class="msg_time">${timeStr}</span></div></div>`;

      $("#messageContainer").append(botHtml);
      scrollToBottom();
    },
    error: function() {
      $(".typing-message").remove();
      alert("Failed to send message.");
    }
  });
}

// 메시지 전송 함수
function sendMessage() {
  const textarea = $("#messageInput");
  const rawText = textarea.val().trim();
  if (!rawText) return;

  if (!currentSessionId) {
    // 세션이 없으면 새 세션 생성 후 메시지 전송
    createNewSession(() => {
      actuallySendMessage(rawText);
    });
  } else {
    actuallySendMessage(rawText);
  }
}

// DOM 로드 완료 후 실행
$(document).ready(function() {
  // 세션 클릭 -> 메시지 로드
  $(".session-button").on("click", function() {
    currentSessionId = $(this).data("session-id");
    loadMessages(currentSessionId);
  });

  const textarea = $("#messageInput");

  // Shift+Enter -> 줄바꿈, Enter -> 전송
  textarea.on("keydown", function(e) {
    if (e.key === "Enter") {
      if (e.shiftKey) {
        const cursorPos = this.selectionStart;
        const val = $(this).val();
        $(this).val(val.substring(0, cursorPos) + "\n" + val.substring(cursorPos));
        this.selectionStart = this.selectionEnd = cursorPos + 1;
        e.preventDefault();
      } else {
        e.preventDefault();
        sendMessage();
      }
    }
  });

  // textarea 자동 높이 조절
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

  // 폼 제출(엔터) -> 메시지 전송 (백업)
  $("#messageForm").on("submit", function(e) {
    e.preventDefault();
    sendMessage();
  });

  // 전송 버튼 클릭
  $("#sendButton").on("click", function() {
    sendMessage();
  });

  // 프로필 이미지 클릭 시 드롭다운 토글
  $('.user-profile .icon-container').click(function(e) {
    e.stopPropagation();
    $('.dropdown-menu').toggle();
  });

  // 문서의 다른 부분 클릭 시 드롭다운 닫기
  $(document).click(function() {
    $('.dropdown-menu').hide();
  });

  // 드롭다운 메뉴 클릭 시 이벤트 전파 중단
  $('.dropdown-menu').click(function(e) {
    e.stopPropagation();
  });
});
