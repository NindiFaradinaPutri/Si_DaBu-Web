let questionIndex = 0;

// ADD QUESTION
document.getElementById("add-question-btn").addEventListener("click", function () {

    const container = document.getElementById("question-container");
    const template = document.getElementById("question-template");

    let clone = template.cloneNode(true);

    clone.classList.remove("d-none");
    clone.removeAttribute("id");

     let inputs = clone.querySelectorAll('input[type="text"]');
    inputs.forEach(input => {
        input.id = "label_" + questionIndex;
        input.name = "label_" + questionIndex;
    });


    // SET RADIO NAME BIAR TIDAK TABRAKAN
    let radios = clone.querySelectorAll('input[type="radio"]');
    radios.forEach((radio, i) => {
        radio.name = "correct_answer_" + questionIndex;
        radio.value = ["A", "B", "C", "D"][i];
    });

    // REMOVE BUTTON
    clone.querySelector(".remove-question").addEventListener("click", function () {
        clone.remove();
    });

    container.appendChild(clone);

    clone.querySelectorAll('[name="question"]').forEach(el => {
        el.required = true;
    });

    questionIndex++;
});

//trigger question answer
document.addEventListener("change", function (e) {
    if (e.target.classList.contains("question-type")) {
        renderConfig(e.target);
    }
});

//Render Config 
function renderConfig(selectElement) {
    const type = selectElement.value;

    //Cari container dalam question yang sama
    const wrapper = selectElement.closest(".question-item");
    const container = wrapper.querySelector(".dynamic-config");

    switch (type) {

        case "single_choice":
        case "multiple_choice":
        case "dropdown":
            container.innerHTML = `
                <div class="form-group">
                  <label>Pilihan</label>
                  <div class="options"></div>
                  <button type="button" onclick="addOption()" class="add-option-btn">+ Tambah Pilihan</button>
                </div>
              `;

            console.log("wrapper:", wrapper);
            console.log("container:", container);
            console.log("options:", container.querySelector(".options"));

            const optionsContainer = container.querySelector(".options");
            console.log("optionsContainer:", optionsContainer);

            if (optionsContainer) {
                addOption(optionsContainer);
            }

            break;

        case "short_text":
        case "long_text":
        case "rating":
        case "file_upload":
        case "image_upload":
        default:
            container.innerHTML = '';
            break;
    }
}

document.addEventListener("click", function (e) {
    if (e.target.classList.contains("add-option-btn")) {
        const optionContainer = e.target.previousElementSibling;
        addOption(optionContainer);
    } else if (e.target.classList.contains("remove-option")) {
        e.target.parentElement.remove();
    }
});

//Dynamic Options
function addOption(container, value = "") {
    if (!container) {
        console.error("Container options tidak ditemukan!");
        return;
    }

    const div = document.createElement("div");

    div.innerHTML = `
    <input type="text" class="option-input" value="${value}" placeholder="Pilihan" />
    <button type="button" onclick="this.parentElement.remove()">Hapus</button>
  `;

    container.appendChild(div);
}

//Handle Submit
document.addEventListener("submit", function (e) {
    if (!e.target.classList.contains("question-form")) return;

    e.preventDefault();

    const form = e.target;

    const type = form.querySelector(".question-type").value;

    let data = {
        label: form.querySelector(".label").value,
        type: type,
        required: form.querySelector(".required").checked,
        config: {},
        options: []
    };

    if (["single_choice", "multiple_choice", "dropdown"].includes(type)) {
        form.querySelectorAll(".option-input").forEach(input => {
            if (input.value.trim()) {
                data.options.push(input.value.trim());
            }
        });
    }

    console.log("DATA:", data);
});


document.addEventListener("DOMContentLoaded", function () {
    const checkbox = document.querySelector("#id_is_form");
    const urlWrapper = document.querySelector("#form-url-wrapper");
    const engagementSection = document.querySelector("#engagement-section");

    function toggleFormMode() {
    const inputs = engagementSection.querySelectorAll("input, select, textarea");

    if (checkbox.checked) {
        urlWrapper.style.display = "block";
        engagementSection.style.display = "none";

        // ❗ disable validation
        inputs.forEach(el => el.required = false);

    } else {
        urlWrapper.style.display = "none";
        engagementSection.style.display = "block";

        // ❗ aktifkan lagi kalau perlu
        inputs.forEach(el => {
            if (el.classList.contains("label-input")) {
                el.required = true;
            }
        });
    }
}

    toggleFormMode(); // initial load
    checkbox.addEventListener("change", toggleFormMode);
});