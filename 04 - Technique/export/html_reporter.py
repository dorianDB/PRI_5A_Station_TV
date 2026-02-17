"""
Station TV - HTML Reporter
Génération de rapports HTML statiques pour les transcriptions audio.
"""

import base64
import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd
from utils.logger import get_logger

logger = get_logger(__name__)


class HTMLTranscriptionReporter:
    """
    Générateur de rapports HTML statiques pour les transcriptions.
    """
    
    def __init__(self, output_dir: str = "output/reports"):
        """
        Initialise le générateur de rapports HTML.
        
        Args:
            output_dir: Répertoire de sortie pour les rapports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"HTMLTranscriptionReporter initialisé (output_dir={output_dir})")
    
    def _image_to_base64(self, image_path: str) -> Optional[str]:
        """
        Convertit une image en base64 pour inclusion dans le HTML.
        
        Args:
            image_path: Chemin vers l'image
            
        Returns:
            String base64 ou None si erreur
        """
        try:
            with open(image_path, 'rb') as img_file:
                encoded = base64.b64encode(img_file.read()).decode('utf-8')
                ext = Path(image_path).suffix.lower()
                mime_type = {
                    '.png': 'image/png',
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.gif': 'image/gif'
                }.get(ext, 'image/png')
                
                return f"data:{mime_type};base64,{encoded}"
        except Exception as e:
            logger.error(f"Erreur conversion image en base64: {str(e)}")
            return None
    
    def _parse_srt_file(self, srt_path: str) -> List[Dict]:
        """
        Parse un fichier SRT et retourne la liste des segments.
        
        Args:
            srt_path: Chemin du fichier SRT
            
        Returns:
            Liste de segments avec timestamps
        """
        segments = []
        try:
            with open(srt_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Séparer par blocs (segments)
            blocks = content.strip().split('\n\n')
            
            for block in blocks:
                lines = block.strip().split('\n')
                if len(lines) >= 3:
                    # Index (première ligne)
                    index = lines[0]
                    # Timestamps (deuxième ligne)
                    timestamps = lines[1]
                    # Texte (reste)
                    text = ' '.join(lines[2:])
                    
                    segments.append({
                        'index': index,
                        'timestamps': timestamps,
                        'text': text
                    })
            
            logger.info(f"SRT parsé: {len(segments)} segments trouvés")
            return segments
            
        except Exception as e:
            logger.error(f"Erreur lors du parsing SRT: {str(e)}")
            return []
    
    def _read_metrics_csv(self, csv_path: str) -> Optional[pd.DataFrame]:
        """
        Lit un fichier CSV de métriques.
        
        Args:
            csv_path: Chemin du fichier CSV
            
        Returns:
            DataFrame ou None si erreur
        """
        try:
            if not Path(csv_path).exists():
                return None
            return pd.read_csv(csv_path)
        except Exception as e:
            logger.error(f"Erreur lecture CSV {csv_path}: {str(e)}")
            return None
    
    def _generate_html_template(
        self,
        title: str,
        transcription_text: str,
        segments: List[Dict],
        metadata: Dict,
        metrics: Dict,
        graph_images: Dict[str, str]
    ) -> str:
        """
        Génère le template HTML complet.
        
        Args:
            title: Titre du rapport
            transcription_text: Texte complet de la transcription
            segments: Liste des segments avec timestamps
            metadata: Métadonnées (fichier, modèle, langue, etc.)
            metrics: Métriques de performance
            graph_images: Dictionnaire {nom: base64_image}
            
        Returns:
            HTML complet
        """
        
        # Préparer les segments HTML
        segments_html = ""
        for seg in segments:
            segments_html += f"""
            <div class="segment">
                <div class="segment-time">{seg['timestamps']}</div>
                <div class="segment-text">{seg['text']}</div>
            </div>
            """
        
        # Préparer les graphiques
        graphs_html = ""
        for name, base64_img in graph_images.items():
            if base64_img:
                graphs_html += f"""
                <div class="graph-container">
                    <img src="{base64_img}" alt="{name}" class="graph-image">
                </div>
                """
        
        # Métriques principales
        metrics_cards = f"""
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Durée Audio</div>
                <div class="metric-value">{metrics.get('audio_duration', 'N/A')}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Temps de Traitement</div>
                <div class="metric-value">{metrics.get('processing_time', 'N/A')}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Throughput</div>
                <div class="metric-value">{metrics.get('throughput', 'N/A')}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">CPU Moyen</div>
                <div class="metric-value">{metrics.get('cpu_avg', 'N/A')}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">RAM Moyenne</div>
                <div class="metric-value">{metrics.get('memory_avg', 'N/A')}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Énergie Totale</div>
                <div class="metric-value">{metrics.get('energy_total', 'N/A')}</div>
            </div>
        </div>
        """
        
        html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        :root {{
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-tertiary: #334155;
            --text-primary: #f1f5f9;
            --text-secondary: #cbd5e1;
            --accent-primary: #3b82f6;
            --accent-secondary: #8b5cf6;
            --accent-success: #10b981;
            --shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }}
        
        [data-theme="light"] {{
            --bg-primary: #ffffff;
            --bg-secondary: #f8fafc;
            --bg-tertiary: #e2e8f0;
            --text-primary: #0f172a;
            --text-secondary: #475569;
        }}
        
        body {{
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
            color: var(--text-primary);
            line-height: 1.6;
            min-height: 100vh;
            padding: 2rem;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        header {{
            background: var(--bg-secondary);
            padding: 2rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            box-shadow: var(--shadow);
            position: relative;
        }}
        
        h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.5rem;
        }}
        
        .subtitle {{
            color: var(--text-secondary);
            font-size: 1rem;
        }}
        
        .theme-toggle {{
            position: absolute;
            top: 2rem;
            right: 2rem;
            background: var(--bg-tertiary);
            border: none;
            color: var(--text-primary);
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s;
        }}
        
        .theme-toggle:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(59, 130, 246, 0.3);
        }}
        
        .section {{
            background: var(--bg-secondary);
            padding: 2rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            box-shadow: var(--shadow);
        }}
        
        .section-title {{
            font-size: 1.75rem;
            font-weight: 600;
            margin-bottom: 1.5rem;
            color: var(--text-primary);
            border-left: 4px solid var(--accent-primary);
            padding-left: 1rem;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        
        .metric-card {{
            background: linear-gradient(135deg, var(--bg-tertiary) 0%, var(--bg-secondary) 100%);
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
            transition: transform 0.3s, box-shadow 0.3s;
        }}
        
        .metric-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(59, 130, 246, 0.2);
        }}
        
        .metric-label {{
            font-size: 0.875rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 0.5rem;
        }}
        
        .metric-value {{
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-success));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .transcription-box {{
            background: var(--bg-tertiary);
            padding: 2rem;
            border-radius: 12px;
            font-size: 1.1rem;
            line-height: 1.8;
            white-space: pre-wrap;
            max-height: 500px;
            overflow-y: auto;
            position: relative;
        }}
        
        .copy-btn {{
            position: absolute;
            top: 1rem;
            right: 1rem;
            background: var(--accent-primary);
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s;
        }}
        
        .copy-btn:hover {{
            background: var(--accent-secondary);
            transform: scale(1.05);
        }}
        
        .segment {{
            background: var(--bg-tertiary);
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            border-left: 3px solid var(--accent-primary);
            transition: all 0.3s;
        }}
        
        .segment:hover {{
            background: var(--bg-primary);
            transform: translateX(5px);
        }}
        
        .segment-time {{
            font-size: 0.875rem;
            color: var(--accent-primary);
            font-weight: 600;
            margin-bottom: 0.5rem;
        }}
        
        .segment-text {{
            color: var(--text-primary);
        }}
        
        .graph-container {{
            margin: 2rem 0;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: var(--shadow);
        }}
        
        .graph-image {{
            width: 100%;
            height: auto;
            display: block;
        }}
        
        .metadata-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
        }}
        
        .metadata-item {{
            background: var(--bg-tertiary);
            padding: 1rem;
            border-radius: 8px;
        }}
        
        .metadata-label {{
            font-size: 0.875rem;
            color: var(--text-secondary);
            margin-bottom: 0.25rem;
        }}
        
        .metadata-value {{
            font-weight: 600;
            color: var(--text-primary);
        }}
        
        .collapsible {{
            cursor: pointer;
            user-select: none;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        
        .collapsible::after {{
            content: '▼';
            transition: transform 0.3s;
        }}
        
        .collapsible.active::after {{
            transform: rotate(-180deg);
        }}
        
        .collapsible-content {{
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease-out;
        }}
        
        .collapsible-content.active {{
            max-height: 5000px;
        }}
        
        @media (max-width: 768px) {{
            body {{
                padding: 1rem;
            }}
            
            h1 {{
                font-size: 2rem;
            }}
            
            .metrics-grid {{
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            }}
            
            .theme-toggle {{
                position: static;
                margin-top: 1rem;
                width: 100%;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{title}</h1>
            <div class="subtitle">Généré le {datetime.now().strftime("%d/%m/%Y à %H:%M:%S")}</div>
            <button class="theme-toggle" onclick="toggleTheme()">🌓 Changer le thème</button>
        </header>
        
        <!-- Métriques -->
        <section class="section">
            <h2 class="section-title">📊 Métriques de Performance</h2>
            {metrics_cards}
        </section>
        
        <!-- Métadonnées -->
        <section class="section">
            <h2 class="section-title">ℹ️ Métadonnées</h2>
            <div class="metadata-grid">
                <div class="metadata-item">
                    <div class="metadata-label">Fichier Source</div>
                    <div class="metadata-value">{metadata.get('filename', 'N/A')}</div>
                </div>
                <div class="metadata-item">
                    <div class="metadata-label">Modèle Whisper</div>
                    <div class="metadata-value">{metadata.get('model', 'N/A')}</div>
                </div>
                <div class="metadata-item">
                    <div class="metadata-label">Langue</div>
                    <div class="metadata-value">{metadata.get('language', 'N/A')}</div>
                </div>
                <div class="metadata-item">
                    <div class="metadata-label">Date de Transcription</div>
                    <div class="metadata-value">{metadata.get('date', 'N/A')}</div>
                </div>
            </div>
        </section>
        
        <!-- Texte complet -->
        <section class="section">
            <h2 class="section-title">📝 Transcription Complète</h2>
            <div class="transcription-box" id="transcription-text">
                <button class="copy-btn" onclick="copyTranscription()">📋 Copier</button>
{transcription_text}
            </div>
        </section>
        
        <!-- Segments -->
        {f'''<section class="section">
            <h2 class="section-title collapsible" onclick="toggleSection('segments')">⏱️ Segments Détaillés</h2>
            <div class="collapsible-content" id="segments">
                {segments_html}
            </div>
        </section>''' if segments else ''}
        
        <!-- Graphiques -->
        {f'''<section class="section">
            <h2 class="section-title collapsible" onclick="toggleSection('graphs')">📈 Graphiques de Monitoring</h2>
            <div class="collapsible-content" id="graphs">
                {graphs_html}
            </div>
        </section>''' if graph_images else ''}
    </div>
    
    <script>
        function toggleTheme() {{
            const root = document.documentElement;
            const currentTheme = root.getAttribute('data-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            root.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
        }}
        
        function copyTranscription() {{
            const text = document.getElementById('transcription-text').textContent;
            navigator.clipboard.writeText(text).then(() => {{
                const btn = event.target;
                const originalText = btn.textContent;
                btn.textContent = '✓ Copié !';
                setTimeout(() => {{
                    btn.textContent = originalText;
                }}, 2000);
            }});
        }}
        
        function toggleSection(id) {{
            const content = document.getElementById(id);
            const header = event.currentTarget;
            content.classList.toggle('active');
            header.classList.toggle('active');
        }}
        
        // Charger le thème sauvegardé
        const savedTheme = localStorage.getItem('theme') || 'dark';
        document.documentElement.setAttribute('data-theme', savedTheme);
    </script>
</body>
</html>"""
        
        return html_content
    
    def generate_report(
        self,
        transcription_dir: str,
        audio_filename: str,
        output_file: Optional[str] = None
    ) -> bool:
        """
        Génère un rapport HTML complet pour une transcription.
        
        Args:
            transcription_dir: Répertoire contenant les fichiers de transcription
            audio_filename: Nom du fichier audio (sans extension)
            output_file: Chemin du fichier HTML de sortie (optionnel)
            
        Returns:
            True si succès, False sinon
        """
        try:
            transcription_dir = Path(transcription_dir)
            
            # Chercher les fichiers de transcription
            txt_file = list(transcription_dir.glob(f"*{audio_filename}*.txt"))
            srt_file = list(transcription_dir.glob(f"*{audio_filename}*.srt"))
            
            if not txt_file:
                logger.error(f"Aucun fichier TXT trouvé pour {audio_filename}")
                return False
            
            # Lire le texte complet
            with open(txt_file[0], 'r', encoding='utf-8') as f:
                transcription_text = f.read()
            
            # Parser les segments SRT si disponible
            segments = []
            if srt_file:
                segments = self._parse_srt_file(str(srt_file[0]))
            
            # Lire les métriques CSV
            cpu_df = self._read_metrics_csv(str(transcription_dir / "monitoring_cpu.csv"))
            memory_df = self._read_metrics_csv(str(transcription_dir / "monitoring_memory.csv"))
            power_df = self._read_metrics_csv(str(transcription_dir / "monitoring_power.csv"))
            
            # Calculer les métriques
            metrics = {
                'audio_duration': 'N/A',
                'processing_time': 'N/A',
                'throughput': 'N/A',
                'cpu_avg': f"{cpu_df['CPU_Usage_Percent'].mean():.1f}%" if cpu_df is not None else 'N/A',
                'memory_avg': f"{memory_df['Memory_Usage_Percent'].mean():.1f}%" if memory_df is not None else 'N/A',
                'energy_total': f"{power_df['Energy_kWh'].iloc[-1]:.3f} kWh" if power_df is not None and len(power_df) > 0 else 'N/A'
            }
            
            # Charger les graphiques
            graph_images = {}
            for graph_name in ['cpu_usage.png', 'memory_usage.png', 'power_usage.png']:
                graph_path = transcription_dir / graph_name
                if graph_path.exists():
                    graph_images[graph_name] = self._image_to_base64(str(graph_path))
            
            # Métadonnées
            metadata = {
                'filename': audio_filename,
                'model': 'small',  # À extraire du nom de fichier ou config
                'language': 'fr',
                'date': datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            }
            
            # Générer le HTML
            html = self._generate_html_template(
                title=f"Rapport de Transcription - {audio_filename}",
                transcription_text=transcription_text,
                segments=segments,
                metadata=metadata,
                metrics=metrics,
                graph_images=graph_images
            )
            
            # Sauvegarder
            if output_file is None:
                output_file = self.output_dir / f"{audio_filename}_report.html"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html)
            
            logger.info(f"Rapport HTML généré: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du rapport: {str(e)}")
            return False


if __name__ == "__main__":
    # Test
    reporter = HTMLTranscriptionReporter()
    reporter.generate_report(
        transcription_dir="test_output/reports",
        audio_filename="test_audio",
        output_file="test_output/transcription_report.html"
    )
