# Guide d'Automatisation - Station TV

## 🚀 Pipeline Automatique Complet

### 📋 Ce qui est automatisé

Le pipeline automatique exécute **4 étapes** :

1. ✅ **Scan des fichiers audio** (liste dans CSV)
2. ✅ **Transcription batch** avec monitoring QoS
3. ✅ **Génération rapports QoS** (graphiques CPU/RAM)
4. ✅ **Tests unitaires** (optionnel)

---

## 🖥️ Méthode 1 : Double-clic (Le plus simple)

### Sur Windows

**Double-cliquez sur** : `RUN_PIPELINE.bat`

C'est tout ! Le script :
- Active l'environnement virtuel
- Lance le pipeline complet
- Affiche la progression
- Génère tous les rapports

---

## ⌨️ Méthode 2 : Ligne de commande

### Sur Windows (PowerShell)

```powershell
cd C:\Users\Dorian\Desktop\stationtv
py -3.11 scripts/RunPipeline.py
```

### Sur Linux/Ubuntu

```bash
cd /chemin/vers/stationtv
python3.11 scripts/RunPipeline.py
```

---

## ⚙️ Configuration pour la Machine DELL

### Avant le premier lancement

**1. Copier le projet sur la DELL**
```powershell
# Depuis votre PC
robocopy "C:\Users\Dorian\Desktop\stationtv" "\\DELL-SERVER\stationtv" /E /Z
```

**2. Sur la DELL, installer Python 3.11 et dépendances**
```powershell
# Vérifier Python (doit être 3.11.x)
py -3.11 --version

# Installer les dépendances
cd C:\stationtv
pip install -r requirements.txt
```

**3. Configurer les chemins dans `config/default_config.yaml`**
```yaml
paths:
  input_audio_dir: "D:/TNT/bdd"  # Adapter selon la DELL
  output_dir: "D:/Station TV/output"
  
hardware:
  cpu_threads: 36
  max_parallel_processes: 6  # Ajuster selon capacité
  
whisper:
  model: "medium"  # Pour qualité optimale
```

---

## 🔄 Fonctionnement du Pipeline

### Étape 1 : Scan (1-2 min)
```
▶️  Scan des fichiers audio
✅ Fichiers trouvés: 150 fichiers (588 heures)
📄 CSV généré: fichiers_audio.csv
```

**Pause interactive** : Vous pouvez vérifier le CSV

### Étape 2 : Transcription (plusieurs heures)
```
▶️  Transcription batch avec monitoring QoS
⚙️  Processus 1/6 : 25 fichiers (98h audio)
⚙️  Processus 2/6 : 25 fichiers (98h audio)
...
📊 Monitoring CPU/RAM en temps réel
✅ Transcriptions générées dans le dossier source
```

### Étape 3 : Rapports QoS (30 sec)
```
▶️  Génération graphiques et rapports QoS
📊 cpu_usage.png créé
📊 memory_usage.png créé
✅ Rapports disponibles dans test_output/reports/
```

### Étape 4 : Tests (optionnel, 1 min)
```
▶️  Exécution des tests unitaires
✅ 15/15 tests passés
```

---

## 📊 Résultats Générés

Après exécution complète :

```
stationtv/
├── bdd/
│   ├── fichier1.mp3
│   ├── fichier1_transcript_wm.txt      ← Transcription TXT
│   ├── fichier1_transcript_st_wm.srt   ← Sous-titres SRT
│   └── ...
├── fichiers_audio.csv                   ← Liste des fichiers
├── test_output/
│   ├── reports/
│   │   ├── cpu_usage.png               ← Graphique CPU
│   │   ├── memory_usage.png            ← Graphique RAM
│   │   ├── power_usage.png             ← Graphique consommation énergétique
│   │   ├── monitoring_cpu.csv
│   │   ├── monitoring_memory.csv
│   │   └── monitoring_power.csv
│   └── trackers/
│       ├── Tracker1.txt                ← Progression processus 1
│       ├── Tracker2.txt
│       └── ...
```

## 🔧 Options Avancées

### Lancer seulement certaines étapes

**Scan uniquement** :
```powershell
python scripts/RunBatchWhisper.py --scan-only
```

**Transcription uniquement** :
```powershell
python scripts/RunBatchWhisper.py
```

**QoS uniquement** :
```powershell
python scripts/ComputeQoS.py --session-dir test_output/reports
```

**Benchmark comparatif des modèles** :
```powershell
python scripts/BenchmarkModels.py --config config/benchmark_config.yaml
# Ou avec paramètres explicites
python scripts/BenchmarkModels.py --models tiny base small medium --repetitions 5
```

**Générer un rapport Excel des résultats de benchmark** :
```powershell
python scripts/GenerateExcelReport.py
```

**Vérifier la configuration avant benchmark** :
```powershell
python scripts/CheckBenchmarkSetup.py
```

---

## 📝 Logs et Suivi

### Pendant l'exécution

- **Console** : Affiche la progression en temps réel
- **Trackers** : `test_output/trackers/TrackerN.txt` (par processus)
- **Logs** : `test_output/logs/stationtv.log`

### Monitoring à distance

Si vous lancez sur DELL en session à distance :

```powershell
# Lancer en arrière-plan
start /B python scripts/RunPipeline.py > pipeline.log 2>&1

# Suivre la progression
Get-Content pipeline.log -Wait
```

---

## ⚠️ Gestion des Erreurs

### Si le pipeline s'arrête

Le pipeline est **robuste** :
- ✅ Chaque fichier est traité indépendamment
- ✅ Un échec sur 1 fichier n'arrête pas les autres
- ✅ Les résultats partiels sont sauvegardés

**Pour reprendre** :
1. Vérifier `fichiers_audio.csv`
2. Supprimer les lignes déjà traitées
3. Relancer `RUN_PIPELINE.bat`

---

## 🎯 Checklist Déploiement DELL

- [ ] **Python 3.11** installé (obligatoire)
- [ ] Dépendances installées (`pip install -r requirements.txt`)
- [ ] Chemins configurés dans `default_config.yaml`
- [ ] FFmpeg installé (pour preprocessing)
- [ ] 256 Go RAM disponible
- [ ] Espace disque suffisant (588h ≈ 100-200 Go de transcriptions)
- [ ] Firewall autorise Python
- [ ] Session utilisateur avec privilèges suffisants

---

## 💡 Conseils pour Session Longue

### Sur Windows Server (DELL)

**1. Éviter déconnexion automatique**
```powershell
# Désactiver veille
powercfg /change standby-timeout-ac 0
powercfg /change monitor-timeout-ac 0
```

**2. Utiliser Task Scheduler** (pour lancement automatisé)
```
1. Ouvrir Task Scheduler
2. Créer une tâche basique
3. Déclencheur: Horaire (ex: chaque nuit à 22h)
4. Action: Démarrer RUN_PIPELINE.bat
5. Envoyer email à la fin (optionnel)
```

**3. Notifications par email** (optionnel)

Ajouter à la fin de `RunPipeline.py` :
```python
# Envoyer email de notification
import smtplib
# ... code d'envoi d'email
```

---

## 📞 Support

**En cas de problème** :
1. Consulter `test_output/logs/stationtv.log`
2. Vérifier les trackers dans `test_output/trackers/`
3. Relire `README.md` et les guides dans `docs/`

**Documentation disponible** :
- `README.md` : Documentation générale
- `docs/BENCHMARK_GUIDE.md` : Guide complet du benchmark
- `docs/BENCHMARK_QUICKSTART.md` : Démarrage rapide benchmark
- `docs/POWER_MONITORING.md` : Monitoring consommation énergétique
- `docs/STVD_NAMING_CONVENTION.md` : Convention de nommage des fichiers

---

## ✅ Résumé

**Pour lancer sur DELL** :
1. Copier le projet
2. Installer dépendances
3. Configurer `default_config.yaml`
4. **Double-cliquer `RUN_PIPELINE.bat`**
5. Attendre 3-6 jours selon config
6. Récupérer les transcriptions !

C'est tout ! 🚀
