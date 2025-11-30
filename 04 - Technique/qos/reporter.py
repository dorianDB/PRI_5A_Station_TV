"""
Station TV - QoS Reporter
Génération de rapports et graphiques de performance
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, Optional
from utils.logger import get_logger

logger = get_logger(__name__)

# Style des graphiques
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)


class QoSReporter:
    """
    Générateur de rapports QoS avec graphiques.
    """
    
    def __init__(self, output_dir: str = "output/reports"):
        """
        Initialise le générateur de rapports.
        
        Args:
            output_dir: Répertoire de sortie
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"QoSReporter initialisé (output_dir={output_dir})")
    
    def plot_cpu_usage(
        self, 
        cpu_csv_file: str, 
        output_file: Optional[str] = None
    ) -> bool:
        """
        Génère un graphique de l'utilisation CPU.
        
        Args:
            cpu_csv_file: Fichier CSV avec données CPU
            output_file: Fichier de sortie PNG (optionnel)
        
        Returns:
            True si succès, False sinon
        """
        try:
            # Lire les données
            df = pd.read_csv(cpu_csv_file)
            
            if df.empty:
                logger.warning("Fichier CPU vide")
                return False
            
            # Créer le graphique
            plt.figure(figsize=(14, 6))
            plt.plot(range(len(df)), df['CPU_Usage_Percent'], color='#2E86AB', linewidth=1.5)
            plt.fill_between(range(len(df)), df['CPU_Usage_Percent'], alpha=0.3, color='#2E86AB')
            
            plt.title('Utilisation CPU - Station TV', fontsize=16, fontweight='bold')
            plt.xlabel('Temps (échantillons)', fontsize=12)
            plt.ylabel('Utilisation CPU (%)', fontsize=12)
            plt.ylim(0, 100)
            plt.grid(True, alpha=0.3)
            
            # Ajouter des statistiques
            mean_cpu = df['CPU_Usage_Percent'].mean()
            max_cpu = df['CPU_Usage_Percent'].max()
            plt.axhline(y=mean_cpu, color='red', linestyle='--', label=f'Moyenne: {mean_cpu:.1f}%')
            plt.legend()
            
            # Sauvegarder
            if output_file is None:
                output_file = self.output_dir / "cpu_usage.png"
            
            plt.tight_layout()
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Graphique CPU généré: {output_file}")
            logger.info(f"  CPU moyen: {mean_cpu:.1f}%, CPU max: {max_cpu:.1f}%")
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du graphique CPU: {str(e)}")
            return False
    
    def plot_memory_usage(
        self, 
        memory_csv_file: str, 
        output_file: Optional[str] = None
    ) -> bool:
        """
        Génère un graphique de l'utilisation RAM.
        
        Args:
            memory_csv_file: Fichier CSV avec données RAM
            output_file: Fichier de sortie PNG (optionnel)
        
        Returns:
            True si succès, False sinon
        """
        try:
            # Lire les données
            df = pd.read_csv(memory_csv_file)
            
            if df.empty:
                logger.warning("Fichier RAM vide")
                return False
            
            # Créer le graphique
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
            
            # Graphique 1: Pourcentage
            ax1.plot(range(len(df)), df['Memory_Usage_Percent'], color='#A23B72', linewidth=1.5)
            ax1.fill_between(range(len(df)), df['Memory_Usage_Percent'], alpha=0.3, color='#A23B72')
            ax1.set_title('Utilisation RAM (%) - Station TV', fontsize=14, fontweight='bold')
            ax1.set_xlabel('Temps (échantillons)', fontsize=11)
            ax1.set_ylabel('Utilisation RAM (%)', fontsize=11)
            ax1.set_ylim(0, 100)
            ax1.grid(True, alpha=0.3)
            
            mean_mem = df['Memory_Usage_Percent'].mean()
            max_mem = df['Memory_Usage_Percent'].max()
            ax1.axhline(y=mean_mem, color='red', linestyle='--', label=f'Moyenne: {mean_mem:.1f}%')
            ax1.axhline(y=90, color='orange', linestyle=':', label='Seuil alerte: 90%')
            ax1.legend()
            
            # Graphique 2: Valeurs absolues (Go)
            if 'Memory_Used_GB' in df.columns and 'Memory_Total_GB' in df.columns:
                ax2.plot(range(len(df)), df['Memory_Used_GB'], color='#F18F01', linewidth=1.5, label='RAM utilisée')
                ax2.axhline(y=df['Memory_Total_GB'].iloc[0], color='gray', linestyle='--', label=f"RAM totale: {df['Memory_Total_GB'].iloc[0]:.1f} Go")
                ax2.fill_between(range(len(df)), df['Memory_Used_GB'], alpha=0.3, color='#F18F01')
                ax2.set_title('Utilisation RAM (Go) - Station TV', fontsize=14, fontweight='bold')
                ax2.set_xlabel('Temps (échantillons)', fontsize=11)
                ax2.set_ylabel('RAM utilisée (Go)', fontsize=11)
                ax2.grid(True, alpha=0.3)
                ax2.legend()
            
            # Sauvegarder
            if output_file is None:
                output_file = self.output_dir / "memory_usage.png"
            
            plt.tight_layout()
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Graphique RAM généré: {output_file}")
            logger.info(f"  RAM moyenne: {mean_mem:.1f}%, RAM max: {max_mem:.1f}%")
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du graphique RAM: {str(e)}")
            return False
    
    def generate_summary_report(
        self, 
        metrics_summary: Dict, 
        output_file: Optional[str] = None
    ) -> bool:
        """
        Génère un rapport texte avec résumé des métriques.
        
        Args:
            metrics_summary: Dictionnaire de métriques (depuis MetricsCalculator)
            output_file: Fichier de sortie (optionnel)
        
        Returns:
            True si succès, False sinon
        """
        try:
            if output_file is None:
                output_file = self.output_dir / "summary_report.txt"
            
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("RAPPORT QoS - STATION TV - TRANSCRIPTION AUDIO\n")
                f.write("=" * 80 + "\n\n")
                
                f.write("RÉSUMÉ DE LA SESSION\n")
                f.write("-" * 80 + "\n")
                f.write(f"Durée de la session: {metrics_summary.get('session_duration_hours', 0):.2f} heures\n")
                f.write(f"Nombre total de fichiers: {metrics_summary.get('total_files', 0)}\n")
                f.write(f"Fichiers réussis: {metrics_summary.get('successful_files', 0)}\n")
                f.write(f"Fichiers échoués: {metrics_summary.get('failed_files', 0)}\n")
                f.write(f"Taux de réussite: {metrics_summary.get('success_rate', 0)*100:.1f}%\n\n")
                
                f.write("PERFORMANCE\n")
                f.write("-" * 80 + "\n")
                f.write(f"Durée audio totale traitée: {metrics_summary.get('total_audio_duration_hours', 0):.2f} heures\n")
                f.write(f"Temps de traitement total: {metrics_summary.get('total_processing_time_hours', 0):.2f} heures\n")
                f.write(f"Throughput (débit): {metrics_summary.get('throughput', 0):.2f}× temps réel\n")
                f.write(f"Temps moyen par fichier: {metrics_summary.get('average_processing_time_seconds', 0):.2f} secondes\n\n")
                
                f.write("OBJECTIFS QoS\n")
                f.write("-" * 80 + "\n")
                throughput = metrics_summary.get('throughput', 0)
                if throughput >= 5:
                    f.write("✓ Throughput ≥ 5× (modèle small) : ATTEINT\n")
                elif throughput >= 1:
                    f.write("✓ Throughput ≥ 1× (modèle medium) : ATTEINT\n")
                else:
                    f.write("✗ Throughput insuffisant\n")
                
                success_rate = metrics_summary.get('success_rate', 0)
                if success_rate >= 0.99:
                    f.write("✓ Taux de réussite ≥ 99% : ATTEINT\n")
                else:
                    f.write(f"⚠ Taux de réussite {success_rate*100:.1f}% < 99%\n")
                
                f.write("\n" + "=" * 80 + "\n")
            
            logger.info(f"Rapport de synthèse généré: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du rapport: {str(e)}")
            return False
