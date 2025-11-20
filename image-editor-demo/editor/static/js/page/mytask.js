// ----------------------------------------------------------------------
// mytask.js
// "나의 작업" 페이지 전용 JS
// - 작업 시나리오 슬라이드 모달
// - 작업 페이지 이동
// ----------------------------------------------------------------------

document.addEventListener("DOMContentLoaded", function () {

    // 슬라이드 이미지 목록 (템플릿에서 Django static 경로 주입)
    const slides = window.MYTASK_SLIDES || [];

    let currentSlideIndex = 0;
    let currentWorkUrl = null;

    const workButtons = document.querySelectorAll(".tm-btn-start-work");
    const modalStartBtn = document.getElementById("tm-work-modal-start");
    const slideImg = document.getElementById("tm-slide-image");
    const slidePrevBtn = document.getElementById("tm-slide-prev");
    const slideNextBtn = document.getElementById("tm-slide-next");
    const slideIndicator = document.getElementById("tm-slide-indicator");

    // -------------------------------------------------------------
    // 슬라이드 업데이트
    // -------------------------------------------------------------
    function updateSlide() {
        if (!slides.length) return;
        slideImg.src = slides[currentSlideIndex];
        slideIndicator.textContent =
            (currentSlideIndex + 1) + " / " + slides.length;
    }

    // -------------------------------------------------------------
    // "작업하러 가기" 버튼 → 모달 오픈
    // -------------------------------------------------------------
    workButtons.forEach(function (btn) {
        btn.addEventListener("click", function () {
            currentWorkUrl = btn.dataset.workUrl || null;
            currentSlideIndex = 0;
            updateSlide();
            tmOpenModal(); // base.html의 공용 모달 함수
        });
    });

    // -------------------------------------------------------------
    // 슬라이드 이전/다음
    // -------------------------------------------------------------
    if (slidePrevBtn) {
        slidePrevBtn.addEventListener("click", function () {
            currentSlideIndex =
                (currentSlideIndex - 1 + slides.length) % slides.length;
            updateSlide();
        });
    }

    if (slideNextBtn) {
        slideNextBtn.addEventListener("click", function () {
            currentSlideIndex = (currentSlideIndex + 1) % slides.length;
            updateSlide();
        });
    }

    // -------------------------------------------------------------
    // 모달 안 "작업 페이지로 이동"
    // -------------------------------------------------------------
    if (modalStartBtn) {
        modalStartBtn.addEventListener("click", function () {
            if (currentWorkUrl) {
                window.location.href = currentWorkUrl;
            }
        });
    }
});
