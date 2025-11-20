// ----------------------------------------------------------------------
// task_list.js
// - 작업 목록 페이지 탭 전환 (일반 목록 / 관리자 승인 대기)
// ----------------------------------------------------------------------

document.addEventListener("DOMContentLoaded", () => {
    const tabUser = document.getElementById("tab-user");
    const tabAdmin = document.getElementById("tab-admin");
    const sectionUser = document.getElementById("section-user");
    const sectionAdmin = document.getElementById("section-admin");

    // 관리자 아닐 때는 탭이 없으므로 바로 종료
    if (!tabUser || !tabAdmin || !sectionUser || !sectionAdmin) {
        return;
    }

    // 사용자 탭
    tabUser.addEventListener("click", () => {
        tabUser.classList.add("tm-tab-active");
        tabAdmin.classList.remove("tm-tab-active");

        sectionUser.classList.remove("tm-hidden");
        sectionAdmin.classList.add("tm-hidden");
    });

    // 관리자 탭
    tabAdmin.addEventListener("click", () => {
        tabAdmin.classList.add("tm-tab-active");
        tabUser.classList.remove("tm-tab-active");

        sectionUser.classList.add("tm-hidden");
        sectionAdmin.classList.remove("tm-hidden");
    });
});
