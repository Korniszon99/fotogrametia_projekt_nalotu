# System Planowania Nalotów Fotogrametrycznych - Django

## Opis projektu

Aplikacja webowa Django do projektowania nalotów fotogrametrycznych dla zdjęć pionowych. System umożliwia:

- ✈️ **Obliczanie parametrów nalotu** - wysokość lotu, liczba szeregów, liczba zdjęć, pokrycia
- 📊 **Interaktywną wizualizację** - graficzny plan nalotu z trasami lotu i pozycjami zdjęć  
- 🎛️ **Intuicyjny interfejs GUI** - nowoczesny interfejs webowy z automatycznym odświeżaniem
- 📱 **Responsywność** - działa na komputerach, tabletach i telefonach

## Struktura projektu

```
photogrammetry_project/
├── photogrammetry_project/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── photogrammetry/
│   ├── migrations/
│   │   └── 0001_initial.py
│   ├── templates/
│   │   └── photogrammetry/
│   │       └── flight_planner.html
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── manage.py
└── requirements.txt
```

## Instalacja i uruchomienie

### Krok 1: Przygotowanie środowiska

```bash
# Utworzenie wirtualnego środowiska
python -m venv photogrammetry_env

# Aktywacja środowiska
# Windows:
photogrammetry_env\Scripts\activate
# Linux/Mac:
source photogrammetry_env/bin/activate
```

### Krok 2: Instalacja zależności

```bash
# Instalacja pakietów z requirements.txt
pip install -r requirements.txt
```

### Krok 3: Konfiguracja bazy danych

```bash
# Utworzenie migracji
python manage.py makemigrations

# Zastosowanie migracji
python manage.py migrate

# Utworzenie superużytkownika (opcjonalne)
python manage.py createsuperuser
```

### Krok 4: Uruchomienie serwera

```bash
# Uruchomienie serwera deweloperskiego
python manage.py runserver
```

Aplikacja będzie dostępna pod adresem: **http://127.0.0.1:8000/**

### Alternatywa:
Możesz użyć Dockera do uruchomienia aplikacji:

```bash
# Uruchomienie aplikacji w kontenerze Docker
docker-compose up --build
```
Aplikacja będzie dostępna pod adresem: **http://0.0.0.0:8000/**

## Użytkowanie aplikacji

### Parametry wejściowe

1. **Wielkość obszaru [m]**
   - Szerokość (Dx): wymiar obszaru w kierunku X
   - Wysokość (Dy): wymiar obszaru w kierunku Y

2. **GSD [m/pixel]**
   - Docelowa wielkość piksela terenowego (Ground Sample Distance)

3. **Model kamery**
   - Wybór z predefiniowanych kamer fotogrametrycznych
   - Zawiera parametry: ogniskowa, rozmiar matrycy, wielkość piksela

4. **Model samolotu**
   - Wybór z predefiniowanych samolotów
   - Zawiera parametry: prędkość przelotowa, maksymalna wysokość

### Wyniki obliczeń

System wyświetla następujące parametry:

- **Wysokość lotu [m]** - obliczona wysokość dla zadanego GSD
- **Zasięgi terenowe X/Y [m]** - rozmiary pojedynczego zdjęcia na terenie
- **Bazy zdjęć [m]** - odległości między centrami kolejnych zdjęć
- **Liczba szeregów** - nominalna i skorygowana
- **Pokrycia [%]** - wzdłużne (p) i poprzeczne (q)
- **Całkowita liczba zdjęć** - suma zdjęć we wszystkich szeregach
- **Czas lotu [min]** - szacowany czas wykonania nalotu

### Wizualizacja

Aplikacja generuje interaktywną wizualizację zawierającą:

- 🔴 **Obszar do sfotografowania** - czerwony prostokąt
- 🔵 **Zasięgi zdjęć** - niebieskie prostokąty
- ➡️ **Trasy lotu** - niebieskie linie
- 🔵 **Centra zdjęć** - niebieskie punkty
- 📊 **Parametry nalotu** - tabela z wynikami

## Funkcje automatyczne

- **Walidacja danych** - sprawdzanie poprawności wprowadzanych wartości
- **Automatyczne odświeżanie** - przeliczanie po zmianie parametrów (z opóźnieniem 1s)
- **Komunikaty błędów** - informowanie o problemach
- **Responsywny design** - dostosowanie do różnych rozmiarów ekranów



## Wymagania systemowe

- **Python**: 3.8+
- **Django**: 4.2+
- **Matplotlib**: 3.7+
- **NumPy**: 1.24+
- **Pillow**: 10.0+

## Architektura rozwiązania

### Backend (Django)
- **Models**: definicje kamer i samolotów
- **Views**: logika obliczeń i generowania wizualizacji
- **FlightPlanCalculator**: klasa do obliczeń parametrów nalotu

### Frontend
- **HTML5**: struktura interfejsu
- **CSS3**: nowoczesny design z gradientami i animacjami
- **JavaScript**: interaktywność i komunikacja AJAX

### Obliczenia fotogrametryczne
- Wysokość lotu: `W = (f × GSD × 1000) / pixel_size`
- Zasięgi terenowe: `L = (sensor_size × GSD × 1000) / pixel_size`
- Bazy zdjęć: `B = L × (1 - pokrycie)`
- Liczba szeregów: `n = ceil(obszar / baza)`

## Licencja

Projekt edukacyjny - Podstawy Fotogrametrii
Politechnika Warszawska - Wydział Geodezji i Kartografii