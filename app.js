"use strict";

const architecture = {
  client: {
    label: "01 / HOST",
    title: "Klient",
    description: "Żądania HTTP wysyła curl lub Swagger UI. Domyślne mapowanie portu Compose wiąże API z adresem 127.0.0.1 na hoście.",
    meta: ["Adres na hoście", "127.0.0.1:8000"],
  },
  api: {
    label: "02 / WARSTWA API",
    title: "FastAPI",
    description: "API rejestruje incydenty, udostępnia ich listę i pozwala zmieniać status zgłoszenia. Dokumentacja OpenAPI jest dostępna pod /docs.",
    meta: ["Punkt wejścia", "api:8000"],
  },
  db: {
    label: "03 / BAZA DANYCH",
    title: "PostgreSQL",
    description: "Baza przechowuje zgłoszenia w tabeli incidents. API odnajduje kontener po nazwie db w wewnętrznym DNS Compose. Baza nie ma opublikowanego portu hosta.",
    meta: ["Adres w sieci Compose", "db:5432"],
  },
  probes: {
    label: "04 / DIAGNOSTYKA",
    title: "Health checks",
    description: "Compose sprawdza działanie procesu przez /health. Endpoint /ready wykonuje SELECT 1 i odpowiada HTTP 503, gdy PostgreSQL jest niedostępny.",
    meta: ["Punkty kontrolne", "/health · /ready"],
  },
  volume: {
    label: "05 / PAMIĘĆ TRWAŁA",
    title: "Wolumen PostgreSQL",
    description: "Nazwany wolumen przechowuje pliki bazy pomiędzy odtworzeniami kontenera. Polecenie docker compose down zatrzymuje stack i zachowuje wolumen.",
    meta: ["Wolumen Compose", "postgres_data"],
  },
};

const stages = [
  { id: "mvp", state: "base", title: "Lokalne MVP", stack: "FastAPI · PostgreSQL · Docker Compose · Pytest", goal: "Uruchomienie dwóch usług, utworzenie incydentu, zmiana statusu i kontrola /ready. W kodzie jest też podstawowy workflow GitHub Actions." },
  { id: "lab-02", state: "lab", title: "Linux, DNS i sieć kontenerów", stack: "LAB 02 · Docker DNS · curl · ss", goal: "Prześledzenie ruchu host → API → baza i udokumentowanie kontrolowanego błędu DNS." },
  { id: "lab-03", state: "lab", title: "Nginx jako reverse proxy", stack: "LAB 03 · Nginx · HTTP · 502", goal: "Wystawienie API lokalnie przez proxy na porcie 8080 i odtworzenie awarii 502 po zatrzymaniu API." },
  { id: "lab-04", state: "lab", title: "Filtrowanie API i testy", stack: "LAB 04 · SQLAlchemy · PostgreSQL · Pytest", goal: "Dodanie filtra severity po stronie bazy oraz testów poprawnych zapytań i błędu HTTP 422." },
  { id: "lab-05", state: "lab", title: "Bash i GitHub Actions", stack: "LAB 05 · Bash · GitHub Actions", goal: "Skrypt diagnostyczny z kodem wyjścia zależnym od /ready oraz dodatkowa kontrola składni przed pytest w istniejącym CI." },
  {
    id: "worker",
    state: "lab",
    title: "Redis i worker",
    stack: "LAB 06 · Redis · RQ · retry",
    goal: "Zleć powiadomienie przez API, przetwórz je w tle i sprawdź zachowanie kolejki podczas awarii.",
    guide: "https://github.com/Dawid26/DevOpsProjectAI/blob/main/docs/LAB-06.md",
  },
  {
    id: "cd",
    state: "lab",
    title: "Obrazy i wdrożenia",
    stack: "LAB 07 · Docker · GHCR · SBOM",
    goal: "Zbuduj obraz, zapisz go w GHCR, uruchom wybraną wersję i przećwicz powrót do poprzedniej.",
    guide: "https://github.com/Dawid26/DevOpsProjectAI/blob/main/docs/LAB-07.md",
  },
  { id: "k8s", state: "plan", title: "Kubernetes", stack: "kind · Deployment · Service", goal: "Przeniesienie aplikacji na lokalny klaster, konfiguracja sond i sprawdzenie skalowania." },
  { id: "etap-monitoring", state: "plan", title: "Helm i obserwowalność", stack: "Helm · Prometheus · Grafana · Loki", goal: "Dashboard, alert na wzrost błędów HTTP 5xx i runbook z krokami diagnozy." },
  { id: "terraform", state: "plan", title: "Terraform i AWS", stack: "IaC · IAM · VPC · AWS", goal: "Opis infrastruktury w kodzie i przygotowanie planu dla opcjonalnego wdrożenia w chmurze." },
  { id: "security", state: "plan", title: "Bezpieczeństwo", stack: "Trivy · RBAC · sekrety", goal: "Skan obrazu i ograniczenie uprawnień usług oraz dostępu do sekretów." },
  { id: "sre", state: "plan", title: "GitOps, backup i odzyskiwanie", stack: "Argo CD · PostgreSQL · postmortem", goal: "Odtworzenie danych z kopii po kontrolowanej awarii i udokumentowanie wyniku." },
];

const statusLabels = { base: "W kodzie", lab: "Ćwiczenie", plan: "W planie" };
const byId = (id) => document.getElementById(id);
const nodeButtons = [...document.querySelectorAll("[data-node]")];
const edges = [...document.querySelectorAll("[data-edge]")];
const filterButtons = [...document.querySelectorAll("[data-filter]")];
const scenarioButtons = [...document.querySelectorAll("[data-scenario]")];

function updatePressed(buttons, key, selected) {
  for (const button of buttons) {
    button.setAttribute("aria-pressed", String(button.dataset[key] === selected));
  }
}

function selectNode(key) {
  const node = architecture[key];
  updatePressed(nodeButtons, "node", key);
  for (const edge of edges) {
    edge.classList.toggle("active", edge.dataset.edge.split(" ").includes(key));
  }
  byId("node-label").textContent = node.label;
  byId("node-title").textContent = node.title;
  byId("node-description").textContent = node.description;
  byId("node-meta-label").textContent = node.meta[0];
  byId("node-meta-value").textContent = node.meta[1];
}

for (const button of nodeButtons) {
  button.addEventListener("click", () => selectNode(button.dataset.node));
}
selectNode("api");

function setScenario(scenario) {
  const databaseDown = scenario === "down";
  updatePressed(scenarioButtons, "scenario", scenario);
  const readiness = byId("readiness");
  readiness.classList.toggle("failure", databaseDown);
  byId("readiness-code").textContent = databaseDown ? "HTTP 503" : "HTTP 200";
  byId("scenario-note").textContent = databaseDown
    ? "API nadal odpowiada, ale /ready zgłasza niedostępność PostgreSQL."
    : "Proces API działa, a PostgreSQL odpowiada na zapytanie SELECT 1.";
}

for (const button of scenarioButtons) {
  button.addEventListener("click", () => setScenario(button.dataset.scenario));
}

byId("copy").addEventListener("click", async () => {
  const commands = byId("commands");
  const status = byId("copy-status");
  try {
    await navigator.clipboard.writeText(commands.textContent);
    status.textContent = "Skopiowano polecenia.";
  } catch {
    const range = document.createRange();
    range.selectNodeContents(commands);
    const selection = window.getSelection();
    selection.removeAllRanges();
    selection.addRange(range);
    status.textContent = "Polecenia zaznaczone. Użyj Ctrl+C lub ⌘C.";
  }
});

function renderStage(stage, index) {
  const row = document.createElement("li");
  row.id = stage.id;
  row.dataset.state = stage.state;

  const details = document.createElement("details");
  const summary = document.createElement("summary");

  const number = document.createElement("span");
  number.className = "stage-number";
  number.textContent = String(index + 1).padStart(2, "0");

  const title = document.createElement("span");
  title.className = "stage-title";
  title.textContent = stage.title;

  const status = document.createElement("span");
  status.className = "stage-status status-" + stage.state;
  status.textContent = statusLabels[stage.state];

  const icon = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  icon.setAttribute("class", "icon");
  icon.setAttribute("aria-hidden", "true");
  const use = document.createElementNS("http://www.w3.org/2000/svg", "use");
  use.setAttribute("href", "#i-plus");
  icon.append(use);
  summary.append(number, title, status, icon);

  const detail = document.createElement("div");
  detail.className = "stage-detail";
  const stack = document.createElement("p");
  const stackLabel = document.createElement("strong");
  stackLabel.textContent = stage.stack;
  stack.append(stackLabel);
  const goal = document.createElement("p");
  goal.textContent = stage.goal;
  detail.append(stack, goal);
  if (stage.guide) {
    const link = document.createElement("a");
    link.className = "text-link";
    link.href = stage.guide;
    link.textContent = "Otwórz instrukcję ćwiczenia";
    detail.append(link);
  }
  details.append(summary, detail);
  row.append(details);
  return row;
}

const stageRows = stages.map(renderStage);
byId("timeline").append(...stageRows);

function setFilter(filter) {
  updatePressed(filterButtons, "filter", filter);
  let visibleCount = 0;
  for (const row of stageRows) {
    row.hidden = filter !== "all" && row.dataset.state !== filter;
    if (!row.hidden) visibleCount++;
  }
  byId("filter-count").textContent = `${visibleCount} z ${stageRows.length} etapów`;
}

for (const button of filterButtons) {
  button.addEventListener("click", () => setFilter(button.dataset.filter));
}
setFilter("all");

byId("monitor-roadmap").addEventListener("click", () => {
  setFilter("plan");
  byId("etap-monitoring").querySelector("details").open = true;
});
