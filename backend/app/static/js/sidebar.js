// sidebar.js

// EXPANDER MENU
const showMenu = (toggleId, navbarId, bodyId) => {
    // DOM 요소 가져오기
    const toggle = document.getElementById(toggleId),        // 토글 버튼
          navbar = document.getElementById(navbarId),        // 네비게이션 바
          bodypadding = document.getElementById(bodyId);     // 본문 영역
  
    // 요소들이 존재하는 경우에만 이벤트 리스너 추가
    if (toggle && navbar) {
      // 토글 버튼 클릭 시 사이드바 확장/축소
      toggle.addEventListener("click", () => {
        // 네비게이션 바에 'expander' 클래스 토글
        navbar.classList.toggle("expander");
        // 본문 영역에 'body-pd' 클래스 토글 (패딩 조정)
        bodypadding.classList.toggle("body-pd");
      });
    }
};
  
// 초기 사이드바 메뉴 설정 실행
showMenu("nav-toggle", "navbar", "body-pd");
  
// 접을 수 있는 메뉴 아이템 처리
const linkCollapse = document.getElementsByClassName("collapse__link");
var i;
  
// 모든 접을 수 있는 메뉴 아이템에 이벤트 리스너 추가
for (i = 0; i < linkCollapse.length; i++) {
    linkCollapse[i].addEventListener("click", function () {
      // 클릭된 메뉴의 하위 메뉴 요소
      const collapseMenu = this.nextElementSibling;
      // 하위 메뉴 표시/숨김 토글
      collapseMenu.classList.toggle("showCollapse");
  
      // 화살표 아이콘 회전 처리
      const rotate = this.querySelector(".collapse__link");
      rotate.classList.toggle("rotate");
    });
}
  