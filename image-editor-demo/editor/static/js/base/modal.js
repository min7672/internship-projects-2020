// 공통 모달 열기
function tmOpenModal() {
    const backdrop = document.getElementById("tm-modal-backdrop");
    if (backdrop) backdrop.classList.remove("tm-hidden");
}

// 공통 모달 닫기
function tmCloseModal() {
    const backdrop = document.getElementById("tm-modal-backdrop");
    if (backdrop) backdrop.classList.add("tm-hidden");
}

document.addEventListener("DOMContentLoaded", () => {
    const backdrop = document.getElementById("tm-modal-backdrop");
    if (!backdrop) return;

    // 바깥 영역 클릭 시 닫기
    backdrop.addEventListener("click", (e) => {
        if (e.target === backdrop) tmCloseModal();
    });
});
