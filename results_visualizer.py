import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import json
import os
import numpy as np
from datetime import datetime
import matplotlib.dates as mdates
from collections import Counter

# Set style for better looking plots
plt.style.use('default')  # Changed from seaborn-v0_8 for compatibility
sns.set_palette("husl")

class VotingResultsVisualizer:
    def __init__(self):
        self.votes_file = "data/votes.json"
        self.voted_users_file = "voted_users.json"
        self.ensure_directories()
        self.load_data()
    
    def ensure_directories(self):
        """Create necessary directories if they don't exist"""
        os.makedirs("data", exist_ok=True)
        os.makedirs("results", exist_ok=True)
    
    def load_data(self):
        """Load voting data from JSON files with error handling"""
        # Load CLI votes
        self.cli_votes = {}
        if os.path.exists(self.votes_file):
            try:
                with open(self.votes_file, "r") as f:
                    content = f.read().strip()
                    if content:  # Check if file is not empty
                        self.cli_votes = json.loads(content)
                    else:
                        print(f"[INFO] {self.votes_file} is empty, initializing with empty dict")
            except json.JSONDecodeError as e:
                print(f"[WARNING] Error reading {self.votes_file}: {e}. Initializing with empty dict")
                self.cli_votes = {}
            except Exception as e:
                print(f"[ERROR] Unexpected error reading {self.votes_file}: {e}")
                self.cli_votes = {}
        else:
            print(f"[INFO] {self.votes_file} does not exist, initializing with empty dict")
        
        # Load GUI votes
        self.gui_votes = {}
        if os.path.exists(self.voted_users_file):
            try:
                with open(self.voted_users_file, "r") as f:
                    content = f.read().strip()
                    if content:  # Check if file is not empty
                        self.gui_votes = json.loads(content)
                    else:
                        print(f"[INFO] {self.voted_users_file} is empty, initializing with empty dict")
            except json.JSONDecodeError as e:
                print(f"[WARNING] Error reading {self.voted_users_file}: {e}. Initializing with empty dict")
                self.gui_votes = {}
            except Exception as e:
                print(f"[ERROR] Unexpected error reading {self.voted_users_file}: {e}")
                self.gui_votes = {}
        else:
            print(f"[INFO] {self.voted_users_file} does not exist, initializing with empty dict")
        
        print(f"[INFO] Loaded {len(self.cli_votes)} CLI votes and {len(self.gui_votes)} GUI votes")
    
    def create_sample_data(self):
        """Create sample data for demonstration purposes"""
        sample_data = {
            "user1": {
                "choice": "1",
                "verification_score": 0.85,
                "face_verified": True,
                "iris_verified": True,
                "timestamp": "2024-01-15T10:30:00"
            },
            "user2": {
                "choice": "2",
                "verification_score": 0.92,
                "face_verified": True,
                "iris_verified": True,
                "timestamp": "2024-01-15T11:45:00"
            },
            "user3": {
                "choice": "1",
                "verification_score": 0.78,
                "face_verified": True,
                "iris_verified": True,
                "timestamp": "2024-01-15T12:15:00"
            },
            "user4": {
                "choice": "3",
                "verification_score": 0.88,
                "face_verified": True,
                "iris_verified": True,
                "timestamp": "2024-01-15T13:20:00"
            },
            "user5": {
                "choice": "2",
                "verification_score": 0.75,
                "face_verified": True,
                "iris_verified": True,
                "timestamp": "2024-01-15T14:10:00"
            }
        }
        
        # Save sample data
        with open(self.votes_file, "w") as f:
            json.dump(sample_data, f, indent=2)
        
        print("[INFO] Sample data created for demonstration")
        self.cli_votes = sample_data
    
    def prepare_combined_data(self):
        """Combine and prepare data from both voting methods"""
        combined_data = []
        
        # Process CLI votes
        for user, vote_data in self.cli_votes.items():
            if isinstance(vote_data, dict):
                combined_data.append({
                    'user': user,
                    'party': self.get_party_name(vote_data.get('choice', 'Unknown')),
                    'verification_score': vote_data.get('verification_score', 0),
                    'timestamp': vote_data.get('timestamp', ''),
                    'method': 'CLI',
                    'face_verified': vote_data.get('face_verified', False),
                    'iris_verified': vote_data.get('iris_verified', False)
                })
        
        # Process GUI votes
        for user, vote_data in self.gui_votes.items():
            if isinstance(vote_data, dict):
                combined_data.append({
                    'user': user,
                    'party': vote_data.get('party', 'Unknown'),
                    'verification_score': vote_data.get('verification_score', 0),
                    'timestamp': vote_data.get('timestamp', ''),
                    'method': 'GUI',
                    'face_verified': True,  # GUI requires both
                    'iris_verified': True
                })
        
        return pd.DataFrame(combined_data)
    
    def get_party_name(self, choice):
        """Convert choice number to party name"""
        party_map = {
            '1': 'BJP',
            '2': 'Congress',
            '3': 'AAP',
            '4': 'Others'
        }
        return party_map.get(str(choice), 'Unknown')
    
    def plot_vote_distribution(self):
        """Create pie chart and bar chart for vote distribution"""
        df = self.prepare_combined_data()
        
        if df.empty:
            print("[WARNING] No voting data available. Creating sample data...")
            self.create_sample_data()
            df = self.prepare_combined_data()
        
        if df.empty:
            print("[ERROR] Still no data available")
            return
        
        # Count votes per party
        vote_counts = df['party'].value_counts()
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Pie Chart
        colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
        wedges, texts, autotexts = ax1.pie(vote_counts.values, 
                                          labels=vote_counts.index,
                                          autopct='%1.1f%%',
                                          startangle=90,
                                          colors=colors[:len(vote_counts)],
                                          explode=tuple([0.1 if i == 0 else 0 for i in range(len(vote_counts))]))
        ax1.set_title('Vote Distribution (Pie Chart)', fontsize=14, fontweight='bold')
        
        # Bar Chart
        bars = ax2.bar(vote_counts.index, vote_counts.values, color=colors[:len(vote_counts)])
        ax2.set_title('Vote Distribution (Bar Chart)', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Number of Votes')
        ax2.set_xlabel('Political Parties')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('results/vote_distribution.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # Print statistics
        total_votes = len(df)
        print(f"\n📊 VOTING STATISTICS")
        print(f"{'='*40}")
        print(f"Total Votes Cast: {total_votes}")
        for party, count in vote_counts.items():
            percentage = (count/total_votes)*100
            print(f"{party}: {count} votes ({percentage:.1f}%)")
    
    def plot_verification_scores(self):
        """Plot verification score distribution"""
        df = self.prepare_combined_data()
        
        if df.empty:
            print("[WARNING] No voting data available. Creating sample data...")
            self.create_sample_data()
            df = self.prepare_combined_data()
        
        if df.empty:
            print("[ERROR] Still no data available")
            return
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # Histogram of verification scores
        ax1.hist(df['verification_score'], bins=20, alpha=0.7, color='skyblue', edgecolor='black')
        ax1.set_title('Distribution of Verification Scores', fontsize=12, fontweight='bold')
        ax1.set_xlabel('Verification Score')
        ax1.set_ylabel('Frequency')
        ax1.axvline(df['verification_score'].mean(), color='red', linestyle='--', 
                   label=f'Mean: {df["verification_score"].mean():.2f}')
        ax1.legend()
        
        # Box plot by party
        if len(df['party'].unique()) > 1:
            df.boxplot(column='verification_score', by='party', ax=ax2)
            ax2.set_title('Verification Scores by Party')
            ax2.set_xlabel('Political Party')
            ax2.set_ylabel('Verification Score')
        else:
            ax2.text(0.5, 0.5, 'Insufficient data for party comparison', 
                    ha='center', va='center', transform=ax2.transAxes)
            ax2.set_title('Verification Scores by Party (Insufficient Data)')
        
        # Verification scores by method
        method_data = []
        method_labels = []
        for method in df['method'].unique():
            method_scores = df[df['method'] == method]['verification_score'].tolist()
            if method_scores:
                method_data.append(method_scores)
                method_labels.append(method)
        
        if method_data:
            ax3.boxplot(method_data, labels=method_labels)
            ax3.set_title('Verification Scores by Voting Method')
            ax3.set_ylabel('Verification Score')
        else:
            ax3.text(0.5, 0.5, 'No method data available', 
                    ha='center', va='center', transform=ax3.transAxes)
            ax3.set_title('Verification Scores by Voting Method (No Data)')
        
        # Scatter plot: Score vs Time (if timestamps available)
        df_with_time = df[df['timestamp'] != ''].copy()
        if not df_with_time.empty:
            try:
                df_with_time['datetime'] = pd.to_datetime(df_with_time['timestamp'])
                scatter = ax4.scatter(df_with_time['datetime'], df_with_time['verification_score'],
                                    c=df_with_time['party'].astype('category').cat.codes, cmap='viridis')
                ax4.set_title('Verification Scores Over Time')
                ax4.set_xlabel('Time')
                ax4.set_ylabel('Verification Score')
                plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45)
            except Exception as e:
                ax4.text(0.5, 0.5, f'Error parsing timestamps: {e}', 
                        ha='center', va='center', transform=ax4.transAxes)
                ax4.set_title('Verification Scores Over Time (Error)')
        else:
            ax4.text(0.5, 0.5, 'No timestamp data available', 
                    ha='center', va='center', transform=ax4.transAxes)
            ax4.set_title('Verification Scores Over Time (No Data)')
        
        plt.tight_layout()
        plt.savefig('results/verification_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_biometric_analysis(self):
        """Analyze biometric verification success rates"""
        df = self.prepare_combined_data()
        
        if df.empty:
            print("[WARNING] No voting data available. Creating sample data...")
            self.create_sample_data()
            df = self.prepare_combined_data()
        
        if df.empty:
            print("[ERROR] Still no data available")
            return
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # Biometric verification success rates
        face_success = df['face_verified'].sum()
        iris_success = df['iris_verified'].sum()
        total = len(df)
        
        biometric_data = ['Face Verification', 'Iris Verification']
        success_rates = [face_success/total*100, iris_success/total*100]
        
        bars1 = ax1.bar(biometric_data, success_rates, color=['lightblue', 'lightcoral'])
        ax1.set_title('Biometric Verification Success Rates', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Success Rate (%)')
        ax1.set_ylim(0, 100)
        
        # Add percentage labels
        for bar, rate in zip(bars1, success_rates):
            ax1.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 1,
                    f'{rate:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        # Verification method distribution
        method_counts = df['method'].value_counts()
        ax2.pie(method_counts.values, labels=method_counts.index, autopct='%1.1f%%',
               colors=['lightgreen', 'orange'])
        ax2.set_title('Voting Method Distribution')
        
        # Score ranges analysis
        score_ranges = pd.cut(df['verification_score'], 
                             bins=[0, 0.5, 0.7, 0.85, 1.0],
                             labels=['Low (0-0.5)', 'Medium (0.5-0.7)', 
                                   'High (0.7-0.85)', 'Very High (0.85-1.0)'])
        range_counts = score_ranges.value_counts()
        
        bars3 = ax3.bar(range_counts.index, range_counts.values, 
                       color=['red', 'orange', 'lightblue', 'green'])
        ax3.set_title('Verification Score Ranges')
        ax3.set_ylabel('Number of Votes')
        ax3.tick_params(axis='x', rotation=45)
        
        # Security level analysis
        df['security_level'] = df['verification_score'].apply(
            lambda x: 'High' if x >= 0.8 else 'Medium' if x >= 0.6 else 'Low'
        )
        security_counts = df['security_level'].value_counts()
        
        colors_security = {'High': 'green', 'Medium': 'orange', 'Low': 'red'}
        bars4 = ax4.bar(security_counts.index, security_counts.values,
                       color=[colors_security.get(level, 'gray') for level in security_counts.index])
        ax4.set_title('Security Level Distribution')
        ax4.set_ylabel('Number of Votes')
        
        plt.tight_layout()
        plt.savefig('results/biometric_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_time_analysis(self):
        """Analyze voting patterns over time"""
        df = self.prepare_combined_data()
        df_time = df[df['timestamp'] != ''].copy()
        
        if df_time.empty:
            print("[WARNING] No timestamp data available. Creating sample data...")
            self.create_sample_data()
            df = self.prepare_combined_data()
            df_time = df[df['timestamp'] != ''].copy()
        
        if df_time.empty:
            print("[WARNING] Still no timestamp data available")
            # Create a simple time analysis chart with available data
            fig, ax = plt.subplots(1, 1, figsize=(10, 6))
            ax.text(0.5, 0.5, 'No timestamp data available for time analysis\nVotes were recorded but without timestamps', 
                    ha='center', va='center', transform=ax.transAxes, fontsize=14)
            ax.set_title('Time Analysis - No Data Available')
            plt.savefig('results/time_analysis.png', dpi=300, bbox_inches='tight')
            plt.show()
            return
        
        try:
            df_time['datetime'] = pd.to_datetime(df_time['timestamp'])
            df_time['hour'] = df_time['datetime'].dt.hour
            df_time['day'] = df_time['datetime'].dt.day
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # Voting by hour
            hourly_votes = df_time['hour'].value_counts().sort_index()
            ax1.plot(hourly_votes.index, hourly_votes.values, marker='o', linewidth=2, markersize=6)
            ax1.set_title('Voting Pattern by Hour of Day')
            ax1.set_xlabel('Hour of Day')
            ax1.set_ylabel('Number of Votes')
            ax1.grid(True, alpha=0.3)
            
            # Cumulative votes over time
            df_time_sorted = df_time.sort_values('datetime')
            df_time_sorted['cumulative_votes'] = range(1, len(df_time_sorted) + 1)
            
            ax2.plot(df_time_sorted['datetime'], df_time_sorted['cumulative_votes'], 
                    linewidth=3, color='green')
            ax2.set_title('Cumulative Votes Over Time')
            ax2.set_xlabel('Time')
            ax2.set_ylabel('Cumulative Number of Votes')
            ax2.grid(True, alpha=0.3)
            plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
            
            plt.tight_layout()
            plt.savefig('results/time_analysis.png', dpi=300, bbox_inches='tight')
            plt.show()
            
        except Exception as e:
            print(f"[ERROR] Error in time analysis: {e}")
            fig, ax = plt.subplots(1, 1, figsize=(10, 6))
            ax.text(0.5, 0.5, f'Error processing timestamp data: {e}', 
                    ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Time Analysis - Error')
            plt.savefig('results/time_analysis.png', dpi=300, bbox_inches='tight')
            plt.show()
    
    def generate_comprehensive_report(self):
        """Generate a comprehensive statistical report"""
        df = self.prepare_combined_data()
        
        if df.empty:
            print("[WARNING] No voting data available. Creating sample data...")
            self.create_sample_data()
            df = self.prepare_combined_data()
        
        if df.empty:
            print("[WARNING] No voting data available for report")
            return
        
        print("\n" + "="*60)
        print("📊 COMPREHENSIVE BIOMETRIC VOTING SYSTEM REPORT")
        print("="*60)
        
        # Basic Statistics
        total_votes = len(df)
        unique_voters = df['user'].nunique()
        
        print(f"\n📈 BASIC STATISTICS:")
        print(f"   Total Votes Cast: {total_votes}")
        print(f"   Unique Voters: {unique_voters}")
        print(f"   Average Verification Score: {df['verification_score'].mean():.3f}")
        print(f"   Minimum Verification Score: {df['verification_score'].min():.3f}")
        print(f"   Maximum Verification Score: {df['verification_score'].max():.3f}")
        print(f"   Standard Deviation: {df['verification_score'].std():.3f}")
        
        # Party-wise results
        print(f"\n🗳️ PARTY-WISE RESULTS:")
        vote_counts = df['party'].value_counts()
        for party, count in vote_counts.items():
            percentage = (count/total_votes)*100
            print(f"   {party}: {count} votes ({percentage:.1f}%)")
        
        # Security Analysis
        high_security = len(df[df['verification_score'] >= 0.8])
        medium_security = len(df[(df['verification_score'] >= 0.6) & (df['verification_score'] < 0.8)])
        low_security = len(df[df['verification_score'] < 0.6])
        
        print(f"\n🔐 SECURITY ANALYSIS:")
        print(f"   High Security (≥0.8): {high_security} votes ({high_security/total_votes*100:.1f}%)")
        print(f"   Medium Security (0.6-0.8): {medium_security} votes ({medium_security/total_votes*100:.1f}%)")
        print(f"   Low Security (<0.6): {low_security} votes ({low_security/total_votes*100:.1f}%)")
        
        # Biometric Success Rates
        face_success_rate = df['face_verified'].sum() / total_votes * 100
        iris_success_rate = df['iris_verified'].sum() / total_votes * 100
        
        print(f"\n👁️ BIOMETRIC VERIFICATION RATES:")
        print(f"   Face Verification Success: {face_success_rate:.1f}%")
        print(f"   Iris Verification Success: {iris_success_rate:.1f}%")
        print(f"   Both Biometrics Success: {min(face_success_rate, iris_success_rate):.1f}%")
        
        # Method Analysis
        method_counts = df['method'].value_counts()
        print(f"\n💻 VOTING METHOD ANALYSIS:")
        for method, count in method_counts.items():
            percentage = (count/total_votes)*100
            print(f"   {method}: {count} votes ({percentage:.1f}%)")
        
        print("\n" + "="*60)
    
    def create_all_visualizations(self):
        """Create all visualizations and save them"""
        # Create results directory
        os.makedirs('results', exist_ok=True)
        
        print("🎨 Generating all visualizations...")
        
        try:
            self.plot_vote_distribution()
            print("✅ Vote distribution completed")
        except Exception as e:
            print(f"❌ Error in vote distribution: {e}")
        
        try:
            self.plot_verification_scores()
            print("✅ Verification scores completed")
        except Exception as e:
            print(f"❌ Error in verification scores: {e}")
        
        try:
            self.plot_biometric_analysis()
            print("✅ Biometric analysis completed")
        except Exception as e:
            print(f"❌ Error in biometric analysis: {e}")
        
        try:
            self.plot_time_analysis()
            print("✅ Time analysis completed")
        except Exception as e:
            print(f"❌ Error in time analysis: {e}")
        
        try:
            self.generate_comprehensive_report()
            print("✅ Comprehensive report completed")
        except Exception as e:
            print(f"❌ Error in comprehensive report: {e}")
        
        print("\n✅ All visualizations completed!")
        print("📁 Charts saved in 'results/' folder")

def main():
    try:
        visualizer = VotingResultsVisualizer()
        
        print("📊 Biometric Voting System - Results Analyzer")
        print("=" * 50)
        
        while True:
            print("\nSelect visualization option:")
            print("1. Vote Distribution (Pie & Bar Charts)")
            print("2. Verification Score Analysis")
            print("3. Biometric Analysis")
            print("4. Time-based Analysis")
            print("5. Comprehensive Report")
            print("6. Generate All Visualizations")
            print("7. Create Sample Data")
            print("8. Exit")
            
            choice = input("\nEnter your choice (1-8): ")
            
            if choice == '1':
                visualizer.plot_vote_distribution()
            elif choice == '2':
                visualizer.plot_verification_scores()
            elif choice == '3':
                visualizer.plot_biometric_analysis()
            elif choice == '4':
                visualizer.plot_time_analysis()
            elif choice == '5':
                visualizer.generate_comprehensive_report()
            elif choice == '6':
                visualizer.create_all_visualizations()
            elif choice == '7':
                visualizer.create_sample_data()
                print("✅ Sample data created!")
            elif choice == '8':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please try again.")
                
    except Exception as e:
        print(f"❌ Error starting application: {e}")

if __name__ == "__main__":
    main()
