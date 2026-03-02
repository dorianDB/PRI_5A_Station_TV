# Station TV - Transcription Audio Haute Performance

**Système de transcription audio haute performance basé sur Whisper (OpenAI)**  
Développé pour la plateforme Station TV du LIFAT (Laboratoire d'Informatique Fondamentale et Appliquée de Tours)

---

## 📋 Vue d'ensemble

Ce projet permet la transcription automatique à grande échelle de flux audio issus de la TNT française. Il est conçu pour fonctionner sur une infrastructure haute performance (Dell Precision 5820 - 256 Go RAM - Xeon W-2295 36 threads).

### Caractéristiques principales

- ✅ **Transcription multi-process** optimisée avec répartition CPU intelligente
- ✅ **Support multi-modèles** Whisper (tiny → large)
- ✅ **Monitoring QoS** temps réel (CPU, RAM, throughput, WER)
- ✅ **Export multi-formats** (TXT, SRT, CSV, JSON)
- ✅ **Architecture modulaire** et extensible
- ✅ **Configuration centralisée** via fichiers YAML

---

## 🏗️ Architecture

```
stationtv/
├── config/                         # Configuration YAML
├── core/                           # Module de transcription Whisper
│   ├── transcription.py            # WhisperTranscriber
│   ├── models.py                   # ModelManager
│   └── affinity.py                 # CPUAffinityManager
├── qos/                            # Module QoS
│   ├── monitor.py                  # SystemMonitor (CPU, RAM)
│   ├── power_monitor.py            # PowerMonitor (consommation)
│   ├── metrics.py                  # MetricsCalculator
│   └── reporter.py                 # QoSReporter (graphiques)
├── utils/                          # Utilitaires
│   ├── logger.py                   # Système de logging
│   └── file_handler.py             # Gestion fichiers audio
├── docs/                           # Documentation
│   ├── BENCHMARK_GUIDE.md          # Guide de benchmark
│   ├── BENCHMARK_QUICKSTART.md     # Démarrage rapide benchmark
│   ├── POWER_MONITORING.md         # Monitoring consommation
│   └── STVD_NAMING_CONVENTION.md   # Convention de nommage
├── preprocessing/                  # Prétraitement audio (futur)
├── export/                         # Export et intégration (futur)
├── scripts/                        # Scripts principaux
│   ├── RunPipeline.py              # Pipeline complet automatique
│   ├── RunBatchWhisper.py          # Transcription batch multi-process
│   ├── ComputeQoS.py               # Génération rapports QoS
│   ├── BenchmarkModels.py          # Benchmark comparatif des modèles
│   ├── BasicTestWhisper.py         # Test unitaire rapide
│   ├── CheckBenchmarkSetup.py      # Vérification configuration benchmark
│   ├── CompareTranscriptions.py    # Comparaison de transcriptions
│   ├── GenerateExcelReport.py      # Rapport Excel des résultats
│   ├── PrepareTestFiles.py         # Préparation des fichiers de test
│   └── RunTests.py                 # Lancement des tests unitaires
└── RUN_PIPELINE.bat                # Lanceur Windows (double-clic)
```

---

## 🚀 Installation

### Prérequis

- **Python 3.11** (requis)
- **256 Go RAM** (recommandé pour modèles large)
- **CPU multi-cœurs** (18+ cœurs physiques)
- **FFmpeg** (pour prétraitement audio)

### Installation des dépendances

```powershell
# Créer un environnement virtuel avec Python 3.11
py -3.11 -m venv venv
.\venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
```

---

## ⚙️ Configuration

La configuration se fait via le fichier `config/default_config.yaml`.

**Paramètres principaux :**

```yaml
hardware:
  cpu_threads: 36                # Threads disponibles
  max_parallel_processes: 3      # Processus simultanés

whisper:
  model: "small"                 # Modèle (tiny/base/small/medium/large)
  language: "fr"                 # Langue
  output_formats:
    txt: true                    # Transcription texte
    srt: true                    # Sous-titres horodatés
    json: true                   # Format structuré

qos:
  enabled: true                  # Activer le monitoring
  monitoring_interval: 2         # Intervalle (secondes)

paths:
  input_audio_dir: "bdd"         # Répertoire audio TNT
  output_dir: "output"           # Répertoire de sortie
```

---

## 📖 Utilisation

### 1. Test unitaire d'un modèle

```powershell
python scripts/BasicTestWhisper.py --input fichier_test.mp3 --model small
```

### 2. Transcription batch multi-process

```powershell
# Scanner les fichiers audio
python scripts/RunBatchWhisper.py --scan-only

# Lancer la transcription batch
python scripts/RunBatchWhisper.py --config config/default_config.yaml
```

### 3. Génération des rapports QoS

```powershell
python scripts/ComputeQoS.py --session-dir test_output/reports
```

### 4. Benchmark comparatif des modèles

```powershell
python scripts/BenchmarkModels.py --config config/benchmark_config.yaml

# Specifier les modèles et répétitions
python scripts/BenchmarkModels.py --models tiny base small medium --repetitions 5
```

---

## 📊 Métriques QoS

Le système génère automatiquement :

- **Graphiques CPU/RAM/Power** (PNG haute résolution)
- **Métriques de performance** : throughput (RT factor), temps moyen/médian, taux de réussite
- **Word Error Rate (WER)** sur échantillons
- **Rapports textuels** détaillés
- **Export CSV** des résultats de benchmark (matrices RT par modèle)

**Objectifs de performance :**
- Throughput ≥ 5× (modèle small)
- Throughput ≥ 1× (modèle medium)
- Utilisation CPU > 85%
- Utilisation RAM < 90%
- Taux de réussite ≥ 99%

---

## 🔧 Développement

### Structure modulaire

Chaque module est indépendant et réutilisable :

- `core/` : Logique de transcription
- `qos/` : Supervision et métriques
- `utils/` : Fonctions utilitaires
- `scripts/` : Points d'entrée

### Logging

Le système utilise un logger centralisé :

```python
from utils.logger import setup_logger

logger = setup_logger("MonModule", level="INFO")
logger.info("Message informationnel")
logger.warning("Avertissement")
logger.error("Erreur")
```

---

## 📝 Références

- **WhisperTranscriptor.py** : Script original ayant servi de base
- **Whisper (OpenAI)** : https://github.com/openai/whisper
- **Station TV (LIFAT)** : Projet de recherche RFAI

---

## 👥 Auteurs

- **Dorian Brisson** - Étudiant 5A ISIE, Polytech Tours (2025-2026)
- **Encadrant** : M. Mathieu Delalandre (LIFAT)
- **Base de code** : T. Bourdeau (2024-2025)

---

## 📄 Licence

Projet académique - Polytech Tours / LIFAT
