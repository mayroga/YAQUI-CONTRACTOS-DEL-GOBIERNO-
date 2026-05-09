/* =========================================================
   KAMIZEN GOV AI
   static/app.js
   GOV CONTRACT HUNTER + PROPOSAL BUILDER
========================================================= */

/* =========================================================
   GLOBAL STATE
========================================================= */

const state = {
    contracts: [],
    selectedContract: null,
    loading: false,
    lastOCRText: "",
    context: {},
    logs: [],
    autoScan: false
};

/* =========================================================
   ELEMENTS
========================================================= */

const screen = document.getElementById("screen");

const searchInput = document.getElementById("searchInput");

const searchBtn = document.getElementById("searchBtn");

const resultsContainer = document.getElementById("results");

const detailsContainer = document.getElementById("details");

const proposalContainer = document.getElementById("proposal");

const logContainer = document.getElementById("logs");

const scanBtn = document.getElementById("scanBtn");

const uploadInput = document.getElementById("uploadInput");

const autoScanToggle = document.getElementById("autoScanToggle");

const contextBox = document.getElementById("contextBox");

/* =========================================================
   LOGGER
========================================================= */

function log(message) {

    const now = new Date().toLocaleTimeString();

    state.logs.unshift(`[${now}] ${message}`);

    if (state.logs.length > 100) {
        state.logs.pop();
    }

    renderLogs();
}

function renderLogs() {

    if (!logContainer) return;

    logContainer.innerHTML = "";

    state.logs.forEach(item => {

        const div = document.createElement("div");

        div.className = "log-item";

        div.textContent = item;

        logContainer.appendChild(div);

    });
}

/* =========================================================
   LOADING
========================================================= */

function setLoading(value) {

    state.loading = value;

    document.body.classList.toggle("loading", value);

}

/* =========================================================
   API
========================================================= */

async function api(path, method = "GET", body = null) {

    try {

        const options = {
            method,
            headers: {
                "Content-Type": "application/json"
            }
        };

        if (body) {
            options.body = JSON.stringify(body);
        }

        const response = await fetch(path, options);

        const data = await response.json();

        return data;

    } catch (err) {

        console.error(err);

        log("API ERROR");

        return null;
    }
}

/* =========================================================
   SEARCH CONTRACTS
========================================================= */

async function searchContracts(query) {

    if (!query || query.length < 2) {
        return;
    }

    setLoading(true);

    log(`Searching contracts: ${query}`);

    const data = await api(
        `/api/contracts/search?q=${encodeURIComponent(query)}`
    );

    setLoading(false);

    if (!data) {
        log("No response from server");
        return;
    }

    state.contracts = data.results || [];

    renderContracts();

    log(`${state.contracts.length} contracts found`);
}

/* =========================================================
   RENDER CONTRACTS
========================================================= */

function renderContracts() {

    if (!resultsContainer) return;

    resultsContainer.innerHTML = "";

    if (!state.contracts.length) {

        resultsContainer.innerHTML = `
            <div class="empty">
                No contracts found
            </div>
        `;

        return;
    }

    state.contracts.forEach(item => {

        const contract = item.contract;

        const card = document.createElement("div");

        card.className = "contract-card";

        card.innerHTML = `
            <div class="contract-top">

                <div class="contract-title">
                    ${contract.title}
                </div>

                <div class="contract-score">
                    ${item.score}
                </div>

            </div>

            <div class="contract-agency">
                ${contract.agency}
            </div>

            <div class="contract-level ${item.level.toLowerCase()}">
                ${item.level}
            </div>

            <div class="contract-desc">
                ${contract.description}
            </div>

            <div class="contract-keywords">
                ${item.keywords.map(k => `
                    <span class="tag">${k}</span>
                `).join("")}
            </div>
        `;

        card.onclick = () => {
            selectContract(item);
        };

        resultsContainer.appendChild(card);

    });
}

/* =========================================================
   SELECT CONTRACT
========================================================= */

function selectContract(item) {

    state.selectedContract = item;

    renderDetails();

    renderProposal();

    log(`Selected: ${item.contract.title}`);
}

/* =========================================================
   DETAILS
========================================================= */

function renderDetails() {

    if (!detailsContainer) return;

    const item = state.selectedContract;

    if (!item) {

        detailsContainer.innerHTML = `
            <div class="empty">
                Select a contract
            </div>
        `;

        return;
    }

    const c = item.contract;

    detailsContainer.innerHTML = `
        <div class="details-section">

            <h2>${c.title}</h2>

            <div class="details-grid">

                <div>
                    <strong>Agency</strong>
                    <p>${c.agency}</p>
                </div>

                <div>
                    <strong>Score</strong>
                    <p>${item.score}</p>
                </div>

                <div>
                    <strong>Level</strong>
                    <p>${item.level}</p>
                </div>

                <div>
                    <strong>NAICS</strong>
                    <p>${c.naics.join(", ")}</p>
                </div>

                <div>
                    <strong>Posted</strong>
                    <p>${c.posted_date}</p>
                </div>

                <div>
                    <strong>Due</strong>
                    <p>${c.due_date}</p>
                </div>

            </div>

            <div class="details-description">

                <strong>Description</strong>

                <p>${c.description}</p>

            </div>

        </div>
    `;
}

/* =========================================================
   PROPOSAL
========================================================= */

function renderProposal() {

    if (!proposalContainer) return;

    const item = state.selectedContract;

    if (!item) {

        proposalContainer.innerHTML = `
            <div class="empty">
                No proposal generated
            </div>
        `;

        return;
    }

    const proposal = item.proposal_outline;

    proposalContainer.innerHTML = `
        <div class="proposal-box">

            <h2>
                ${proposal.proposal_title}
            </h2>

            <div class="proposal-sections">

                ${proposal.sections.map(section => `
                    <div class="proposal-item">
                        ${section}
                    </div>
                `).join("")}

            </div>

            <button id="generateProposalBtn">
                Generate Full Proposal
            </button>

        </div>
    `;

    const btn = document.getElementById(
        "generateProposalBtn"
    );

    if (btn) {

        btn.onclick = async () => {
            await generateProposal();
        };
    }
}

/* =========================================================
   GENERATE FULL PROPOSAL
========================================================= */

async function generateProposal() {

    const item = state.selectedContract;

    if (!item) return;

    setLoading(true);

    log("Generating proposal...");

    const data = await api(
        "/api/proposal/generate",
        "POST",
        {
            contract: item.contract
        }
    );

    setLoading(false);

    if (!data) {
        return;
    }

    proposalContainer.innerHTML = `
        <div class="generated-proposal">

            <h2>
                Proposal Generated
            </h2>

            <pre>
${JSON.stringify(data, null, 2)}
            </pre>

        </div>
    `;

    log("Proposal generated");
}

/* =========================================================
   CONTEXT DETECTOR
========================================================= */

function getContextTopic() {

    if (!screen) {
        return {};
    }

    const text = screen.innerText || "";

    const lower = text.toLowerCase();

    const context = {

        tags: [],
        agencies: [],
        probable_naics: []

    };

    if (lower.includes("student")) {

        context.tags.push("education");

        context.probable_naics.push("611710");

    }

    if (lower.includes("training")) {

        context.tags.push("training");

        context.probable_naics.push("611430");

    }

    if (lower.includes("software")) {

        context.tags.push("software");

        context.probable_naics.push("541511");

    }

    if (lower.includes("resilience")) {

        context.tags.push("resilience");

    }

    if (lower.includes("defense")) {

        context.agencies.push(
            "Department of Defense"
        );

    }

    if (lower.includes("veteran")) {

        context.agencies.push("VA");

    }

    if (lower.includes("school")) {

        context.agencies.push(
            "Department of Education"
        );

    }

    return context;
}

/* =========================================================
   CONTEXT RENDER
========================================================= */

function renderContext() {

    if (!contextBox) return;

    const context = getContextTopic();

    state.context = context;

    contextBox.innerHTML = `
        <div class="context-section">

            <h3>Context Detection</h3>

            <div class="context-group">

                <strong>Tags</strong>

                <div class="chips">
                    ${context.tags.map(t => `
                        <span class="chip">${t}</span>
                    `).join("")}
                </div>

            </div>

            <div class="context-group">

                <strong>Agencies</strong>

                <div class="chips">
                    ${context.agencies.map(t => `
                        <span class="chip">${t}</span>
                    `).join("")}
                </div>

            </div>

            <div class="context-group">

                <strong>NAICS</strong>

                <div class="chips">
                    ${context.probable_naics.map(t => `
                        <span class="chip">${t}</span>
                    `).join("")}
                </div>

            </div>

        </div>
    `;
}

/* =========================================================
   OCR IMAGE
========================================================= */

async function runOCR(file) {

    if (!file) return;

    log("Running OCR...");

    setLoading(true);

    const formData = new FormData();

    formData.append("file", file);

    try {

        const response = await fetch(
            "/api/ocr",
            {
                method: "POST",
                body: formData
            }
        );

        const data = await response.json();

        setLoading(false);

        if (!data) {
            return;
        }

        state.lastOCRText = data.text || "";

        if (screen) {

            screen.innerText =
                state.lastOCRText;

        }

        renderContext();

        log("OCR completed");

    } catch (err) {

        console.error(err);

        setLoading(false);

        log("OCR failed");

    }
}

/* =========================================================
   AUTO SCAN
========================================================= */

function startAutoScan() {

    setInterval(() => {

        if (!state.autoScan) return;

        renderContext();

    }, 3000);
}

/* =========================================================
   EVENTS
========================================================= */

if (searchBtn) {

    searchBtn.onclick = () => {

        const query = searchInput.value.trim();

        searchContracts(query);

    };
}

if (searchInput) {

    searchInput.addEventListener(
        "keydown",
        e => {

            if (e.key === "Enter") {

                searchContracts(
                    searchInput.value.trim()
                );

            }
        }
    );
}

if (scanBtn) {

    scanBtn.onclick = () => {

        uploadInput.click();

    };
}

if (uploadInput) {

    uploadInput.onchange = async e => {

        const file = e.target.files[0];

        if (!file) return;

        await runOCR(file);

    };
}

if (autoScanToggle) {

    autoScanToggle.onchange = e => {

        state.autoScan = e.target.checked;

        log(
            `Auto Scan: ${
                state.autoScan
                    ? "ON"
                    : "OFF"
            }`
        );
    };
}

/* =========================================================
   INITIALIZE
========================================================= */

function init() {

    log("KAMIZEN GOV AI READY");

    renderContext();

    startAutoScan();

    searchContracts("training");
}

window.onload = init;
