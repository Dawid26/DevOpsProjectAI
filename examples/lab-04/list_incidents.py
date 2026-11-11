# Zastąp funkcję list_incidents w api/app/main.py tą wersją.
# Dodaj też Severity do importu z .schemas. Pozostałe importy już są w main.py.
@app.get("/incidents", response_model=list[IncidentRead])
def list_incidents(db: DbSession, severity: Severity | None = None):
    query = select(Incident)
    if severity is not None:
        query = query.where(Incident.severity == severity)
    return db.scalars(query.order_by(Incident.id.desc())).all()
