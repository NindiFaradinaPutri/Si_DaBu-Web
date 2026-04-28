//trigger question answer
document.getElementById("question-type").addEventListener("change", function () {
    renderConfig(this.value);
});

// initial render
renderConfig(document.getElementById("question-type").value);

//Render Config 
function renderConfig(type) {
    const container = document.getElementById("dynamic-config");

    switch (type) {

        case "short_text":
        case "long_text":
            container.innerHTML = `
        <div class="form-group">
          <label>Placeholder</label>
          <input type="text" id="placeholder" class="form-control"/>
        </div>
      `;
            break;

        case "number":
            container.innerHTML = `
        <div class="form-group">
          <label>Min</label>
          <input type="number" id="min"/>
          <label>Max</label>
          <input type="number" id="max"/>
        </div>
      `;
            break;

        case "single_choice":
        case "multiple_choice":
        case "dropdown":
            container.innerHTML = `
        <div class="form-group">
          <label>Options</label>
          <div id="options"></div>
          <button type="button" onclick="addOption()">+ Tambah Option</button>
        </div>
      `;
            addOption();
            addOption();
            break;

        case "rating":
            container.innerHTML = `
        <div class="form-group">
          <label>Max Rating</label>
          <input type="number" id="rating_max" value="5"/>
        </div>
      `;
            break;

        case "file_upload":
        case "image_upload":
            container.innerHTML = `
        <div class="form-group">
          <label>Allowed File Types</label>
          <input type="text" id="file_types" placeholder="jpg,png,pdf"/>
        </div>
      `;
            break;

        default:
            container.innerHTML = "";
    }
}

//Dynamic Options
function addOption(value = "") {
    const container = document.getElementById("options");

    const div = document.createElement("div");
    div.classList.add("option-item");

    div.innerHTML = `
    <input type="text" class="option-input" value="${value}" placeholder="Option" />
    <button type="button" onclick="this.parentElement.remove()">Hapus</button>
  `;

    container.appendChild(div);
}

//Handle Submit
document.getElementById("question-form").addEventListener("submit", function (e) {
    e.preventDefault();

    const type = document.getElementById("question-type").value;

    let data = {
        label: document.getElementById("label").value,
        type: type,
        required: document.getElementById("required").checked,
        config: {},
        options: []
    };

    // HANDLE CONFIG
    if (type === "short_text" || type === "long_text") {
        data.config.placeholder = document.getElementById("placeholder")?.value;
    }

    if (type === "number") {
        data.config.min = document.getElementById("min")?.value;
        data.config.max = document.getElementById("max")?.value;
    }

    if (type === "rating") {
        data.config.max = document.getElementById("rating_max")?.value;
    }

    if (type === "file_upload" || type === "image_upload") {
        data.config.types = document.getElementById("file_types")?.value;
    }

    // HANDLE OPTIONS
    if (["single_choice", "multiple_choice", "dropdown"].includes(type)) {
        document.querySelectorAll(".option-input").forEach(input => {
            if (input.value.trim()) {
                data.options.push(input.value.trim());
            }
        });
    }

    console.log("DATA KIRIM:", data);

    // AJAX ke backend Django
    fetch("/api/questions/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    });
});