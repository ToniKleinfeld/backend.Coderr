# TODO.md

## ✅ Allgemeine Projektstruktur

- [x] Projektordner mit dem Namen `core` erstellen
- [x] Separate Apps mit sinnvollem Suffix/Präfix (z. B. `auth_app`, `kanban_app`)
- [x] Jede App enthält `api/`-Ordner für views, serializers, etc.

## ✅ Endpoints

- [x] Alle laut Dokumentation spezifizierten Endpunkte erstellen
- [x] Routen ressourcenorientiert definieren (z. B. `/api/boards/42/`)

## ✅ Models

- [x] Modelle im PascalCase benennen
- [x] Felder im snake_case
- [x] Sinnvolle `__str__()` Methoden und `Meta` Optionen setzen
- [x] Keine Logik in Models
- [x] Beziehungen korrekt mit `on_delete` und `related_name` definieren

## ✅ Serializers

- [x] ModelSerializers verwenden
- [x] Felder explizit angeben (`fields = [...]`, kein `__all__`)
- [x] Validierungsmethoden implementieren, falls notwendig

## ✅ Views

- [x] `ModelViewSet` für Standard-CRUD-Endpunkte
- [x] `APIView` oder `GenericAPIView` für individuelle Endpunkte
- [x] `queryset` und `serializer_class` als Properties
- [x] `get_queryset()` bei dynamischem Verhalten
- [x] Permissions explizit mit `permission_classes`

## ✅ URLs

- [x] Jede App hat eigene `urls.py`
- [x] Zentrales Routing in `core/urls.py`
- [x] Ressourcengerechte URL-Struktur

## ✅ Permissions & Authentifizierung

- [x] Jede App hat eigene `permissions.py` (falls nötig)
- [x] Authentifizierungsmechanismen einbauen (z. B. Token, Session)
- [x] Kombinierte Permissions nutzen (z. B. `IsAuthenticated & IsOwner`)
- [x] Keine offenen Endpunkte ohne triftigen Grund

## ✅ Clean Code & Dokumentation

- [x] Jede Methode/Funktion hat eine Aufgabe und max. 14 Zeilen
- [x] Kein toter Code oder `print()` Befehle
- [x] Einhaltung von PEP8
- [ ] Kommentare und ggf. Docstrings ergänzen

## ✅ GitHub Setup

- [x] Aussagekräftige `README.md` (auf Englisch) erstellen
- [x] `requirements.txt` hinzufügen
- [x] Nur Backend-Code im Repo (Frontend separat)
- [x] Keine Datenbank-Dateien commiten

## ✅ Testing

- [x] Testabdeckung ≥ 95 % mit Postman-Tests
- [x] Kritische Logik zu 100 % getestet

## ✅ Best Practices

- [x] Imports gruppiert: Standard, Third-party, lokal
- [x] Klare Trennung: Models = Datenstruktur, Serializers = Validierung, Views = Logik
- [x] Korrekte HTTP-Statuscodes zurückgeben
