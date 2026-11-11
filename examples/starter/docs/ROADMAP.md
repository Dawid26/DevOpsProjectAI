# Ścieżka DevOps — 12 etapów

Zasada: najpierw sam spróbuj → sprawdź wynik → wykonaj awarię kontrolowaną → opisz w README lub runbooku → commit. Dopiero potem kolejny etap.

| Etap | Nauka / zadanie | Dowód umiejętności na GitHubie |
|---|---|---|
| 01. Linux i Git | shell, uprawnienia, `grep`, `ss`, procesy, commit, branch | pierwsza historia Git, skrypt diagnostyczny |
| 02. Aplikacja + SQL | FastAPI, REST, PostgreSQL, CRUD, podstawy SQL | endpointy i schemat danych |
| 03. Docker i Compose | Dockerfile, image, port, network, volume, healthcheck | działający lokalny stack |
| 04. Networking / Nginx | DNS, porty, reverse proxy, HTTP, TLS lokalnie | dostęp przez proxy, diagram ruchu |
| 05. Redis / worker | kolejka, retry, idempotencja, dead letter concept | zadania asynchroniczne, awarie kolejki |
| 06. CI | pytest, lint, GitHub Actions, caching, zasady PR | zielony pipeline i ochrony jakości |
| 07. Images i CD | tagi, GHCR, SBOM, deployment, rollback | wersjonowane obrazy, workflow CD |
| 08. Kubernetes | kind, kubectl, ConfigMap, Secret, Service, Deployment, probe, HPA | manifesty i test skalowania |
| 09. Helm + monitoring | Helm, Prometheus, Grafana, Loki, alerty, SLI/SLO | dashboard, alert i runbook |
| 10. Terraform + AWS | IaC, state, IAM, VPC, EC2/ECR, opcjonalnie EKS | plan + mały deployment w chmurze |
| 11. Security | Trivy, least privilege, RBAC, secrets, scanning | raport skanowania, naprawa |
| 12. SRE / GitOps / backup | Argo CD, GitOps, backup/restore, chaos lab, postmortem | kontrolowana awaria, odzysk, opis |

**Koszty:** etap 01–09 wykonasz lokalnie. AWS jest opcjonalny i może generować opłaty, nawet gdy zasoby są bezczynne. Przed wdrożeniem ustal budżet i plan kasowania zasobów. Nie uruchamiaj EKS bez sprawdzenia kosztów.

## Jak mierzymy postęp?

- Każdy etap ma kryteria zaliczenia (działa, wiesz czemu, umiesz diagnozować).
- Przynajmniej jeden świadomie wywołany problem i naprawa.
- Commity w stylu: `feat(api): create incident endpoint`, `fix(compose): wait for healthy postgres`, `docs: add postgres outage runbook`.
- Nie kopiuj ślepo komend: najpierw przewiduj wynik.

## Backlog prawdziwego produktu

- Historia zmian incydentu i właściciel zgłoszenia.
- Autoryzacja i role `reader` / `operator` / `admin`.
- Alembic, paginacja, filtrowanie, rate limit.
- 12-factor app, logi strukturalne JSON, correlation ID.
- Zadanie w tle tworzące powiadomienie, retry i monitoring queue depth.
- SLO API i alert na podwyższone 5xx.
- Odtwarzanie bazy z backupu i pomiar RTO/RPO.

## Kolejne laboratoria z instrukcjami

- [LAB 02 — Linux, DNS i sieci](LAB-02.md)
- [LAB 03 — Nginx reverse proxy](LAB-03.md)
- [LAB 04 — filtrowanie API i testy](LAB-04.md)
- [LAB 05 — Bash i CI](LAB-05.md)
