let questionIndex = 0;

// =========================
// DOM READY
// =========================
document.addEventListener("DOMContentLoaded", function () {

    // =========================
    // LOAD EXISTING QUESTIONS
    // =========================
    const questionElement =
        document.getElementById("questions-data");

    if (questionElement) {

        const existingQuestions = JSON.parse(
            JSON.parse(questionElement.textContent)
        );

        console.log("EXISTING QUESTIONS:", existingQuestions);

        if (existingQuestions.length > 0) {

            existingQuestions.forEach(q => {
                createQuestionItem(q);
            });

        }

    }

    // =========================
    // TOGGLE GOOGLE FORM
    // =========================
    const checkbox = document.getElementById("id_is_form");

    const urlWrapper =
        document.getElementById("form-url-wrapper");

    const engagementSection =
        document.getElementById("engagement-section");

    const btnSimpan =
        document.getElementById("btn-simpan");

    const btnaddquestion =
        document.getElementById("add-question-btn-2");

    if (!checkbox) {
        console.warn("Checkbox tidak ditemukan");
        return;
    }

    function toggleUI() {

        const inputs = engagementSection.querySelectorAll(
            "input, select, textarea"
        );

        const urlInput =
            document.getElementById("id_event-url_form");

        // =========================
        // GOOGLE FORM MODE
        // =========================
        if (checkbox.checked) {

            urlWrapper.style.display = "block";

            engagementSection.style.display = "none";

            btnSimpan.style.display = "none";
            
            btnaddquestion.style.display = "none";

            if (urlInput) {
                urlInput.required = true;
            }

            inputs.forEach(el => {
                el.required = false;
            });

        }

        // =========================
        // CUSTOM FORM MODE
        // =========================
        else {

            urlWrapper.style.display = "none";

            engagementSection.style.display = "block";

            btnSimpan.style.display = "block";

            btnaddquestion.style.display = "block";

            if (urlInput) {
                urlInput.required = false;
            }

            inputs.forEach(el => {

                if (
                    el.classList.contains("question-label")
                ) {
                    el.required = true;
                }

            });

        }

    }

    toggleUI();

    checkbox.addEventListener("change", toggleUI);

});

// =========================
// ADD QUESTION BUTTON
// =========================
document.getElementById("add-question-btn")
.addEventListener("click", function () {

    createQuestionItem();

});

document.getElementById("add-question-btn-2")
.addEventListener("click", function () {

    createQuestionItem();

});

// =========================
// QUESTION TYPE CHANGE
// =========================
document.addEventListener("change", function (e) {

    if (
        e.target.classList.contains("question-type")
    ) {

        renderConfig(e.target);

    }

});

// =========================
// RENDER CONFIG
// =========================
function renderConfig(selectElement) {

    const type = selectElement.value;

    const wrapper =
        selectElement.closest(".question-item");

    const container =
        wrapper.querySelector(".dynamic-config");

    switch (type) {

        case "single_choice":
        case "multiple_choice":
        case "dropdown":

            container.innerHTML = `
                <div class="form-group mt-3">

                    <label class="fw-bold mb-2">
                        Pilihan
                    </label>

                    <div class="options"></div>

                    <button
                        type="button"
                        class="add-option-btn btn btn-sm btn-primary mt-2">

                        + Tambah Pilihan

                    </button>

                </div>
            `;

            break;

        default:

            container.innerHTML = '';

            break;
    }
}

// =========================
// HANDLE OPTION BUTTON
// =========================
document.addEventListener("click", function (e) {

    // =========================
    // ADD OPTION
    // =========================
    if (
        e.target.classList.contains("add-option-btn")
    ) {

        const optionContainer = e.target
            .closest(".form-group")
            .querySelector(".options");

        addOption(optionContainer);

    }

    // =========================
    // REMOVE OPTION
    // =========================
    if (
        e.target.classList.contains("remove-option")
    ) {

        e.target.closest(".option-item").remove();

    }

});

// =========================
// ADD OPTION
// =========================
function addOption(
    container,
    value = "",
    optionId = null
) {

    if (!container) {

        console.error(
            "Container options tidak ditemukan!"
        );

        return;
    }

    const div = document.createElement("div");

    div.classList.add(
        "option-item",
        "d-flex",
        "gap-2",
        "mb-2",
        "align-items-center"
    );

    div.innerHTML = `

        <input
            type="hidden"
            class="option-id"
            value="${optionId || ''}"
        />

        <input
            type="text"
            class="form-control option-input"
            value="${value}"
            placeholder="Pilihan"
        />

        <button
            type="button"
            class="btn btn-danger btn-sm remove-option">

            Hapus

        </button>
    `;

    container.appendChild(div);
}

// =========================
// CREATE QUESTION ITEM
// =========================
function createQuestionItem(data = {}) {

    const container =
        document.getElementById("question-container");

    const template =
        document.getElementById("question-template");

    let clone = template.cloneNode(true);

    clone.classList.remove("d-none");

    clone.removeAttribute("id");

    // =========================
    // QUESTION ID
    // =========================
    if (data.id) {

        let hidden =
            document.createElement("input");

        hidden.type = "hidden";

        hidden.className = "question-id";

        hidden.value = data.id;

        clone.appendChild(hidden);
    }

    // =========================
    // LABEL
    // =========================
    const labelInput =
        clone.querySelector(".question-label");

    if (labelInput) {

        labelInput.value =
            data.label || "";

    }

    // =========================
    // TYPE
    // =========================
    const typeSelect =
        clone.querySelector(".question-type");

    if (typeSelect) {

        typeSelect.value =
            data.type || "short_text";

    }

    // =========================
    // REQUIRED
    // =========================
    const requiredCheckbox =
        clone.querySelector(".required-checkbox");

    if (requiredCheckbox) {

        requiredCheckbox.checked =
            data.required || false;

    }

    // =========================
    // RADIO UNIQUE
    // =========================
    let radios =
        clone.querySelectorAll(
            'input[type="radio"]'
        );

    radios.forEach((radio, i) => {

        radio.name =
            "correct_answer_" + questionIndex;

        radio.value =
            ["A", "B", "C", "D"][i];

    });

    // =========================
    // REMOVE QUESTION
    // =========================
    clone.querySelector(".remove-question")
        .addEventListener("click", function () {

            clone.remove();

        });

    // =========================
    // APPEND DULU
    // =========================
    container.appendChild(clone);

    // =========================
    // RENDER CONFIG
    // =========================
    renderConfig(typeSelect);

    // =========================
    // LOAD EXISTING OPTIONS
    // =========================
    if (
        data.options &&
        data.options.length > 0
    ) {

        const optionsContainer =
            clone.querySelector(".options");

        if (optionsContainer) {

            optionsContainer.innerHTML = "";

            data.options.forEach(opt => {

                addOption(
                    optionsContainer,
                    opt.value || "",
                    opt.id || ""
                );

            });

        }

    }

    questionIndex++;
}

// =========================
// HANDLE SUBMIT
// =========================
document.getElementById("event-form")
.addEventListener("submit", function (e) {

    e.preventDefault();

    const formElement = this;

    let formData = new FormData(formElement);

    const checkbox =
        document.getElementById("id_is_form");

    let questions = [];

    // =========================
    // CUSTOM FORM MODE
    // =========================
    if (!checkbox.checked) {

        document.querySelectorAll(
            "#question-container .question-item"
        ).forEach((item, index) => {

            const label =
                item.querySelector(".question-label")
                ?.value.trim() || "";

            const type =
                item.querySelector(".question-type")
                ?.value || "";

            const required =
                item.querySelector(".required-checkbox")
                ?.checked || false;

            let options = [];

            item.querySelectorAll(".option-input")
            .forEach(opt => {

                const value =
                    opt.value.trim();

                if (value !== "") {

                    options.push({

                        id: opt.closest(".option-item")
                            .querySelector(".option-id")
                            ?.value || null,

                        label: value,

                        value: value

                    });

                }

            });

            questions.push({

                id: item.querySelector(".question-id")
                    ?.value || null,

                label: label,

                type: type,

                required: required,

                order: index + 1,

                options: options

            });

        });

    }

    // =========================
    // APPEND QUESTIONS
    // =========================
    formData.append(
        "questions",
        JSON.stringify(questions)
    );

    console.log("QUESTIONS:", questions);

    // =========================
    // AJAX SUBMIT
    // =========================
    $.ajax({

    url: window.location.href,

    type: "POST",

    data: formData,

    processData: false,

    contentType: false,

    success: function (response) {

        console.log("RESPONSE:", response);

        // =========================
        // SUCCESS
        // =========================
        if (response.status === "success") {

            Swal.fire({

                icon: "success",

                title: "Berhasil",

                text: response.message,

                confirmButtonColor: "#E31E24"

            }).then(() => {

                window.location.href =
                    "/admin/profile/";

            });

        }

        // =========================
        // ERROR VALIDATION
        // =========================
        else {

            Swal.fire({

                icon: "error",

                title: "Gagal",

                text: response.message ||

                    "Terjadi kesalahan.",

                confirmButtonColor: "#E31E24"

            });

            console.log(
                "EVENT ERRORS:",
                response.event_errors
            );

            console.log(
                "PHOTO ERRORS:",
                response.photo_errors
            );

        }

    },

    // =========================
    // SERVER ERROR
    // =========================
    error: function (xhr) {

        console.log(xhr.responseText);

        Swal.fire({

            icon: "error",

            title: "Server Error",

            text: "Terjadi kesalahan pada server.",

            confirmButtonColor: "#E31E24"

        });

    }

});

});