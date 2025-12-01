import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
from results_visualizer import VotingResultsVisualizer

class ResultsDashboard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("📊 Biometric Voting Results Dashboard")
        self.root.geometry("800x600")
        self.root.configure(bg="lightgray")
        
        self.visualizer = VotingResultsVisualizer()
        self.create_widgets()
    
    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self.root, bg="darkblue", height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        header_label = tk.Label(header_frame, 
                               text="📊 Biometric Voting Results Dashboard 📊", 
                               font=("Arial", 18, "bold"), fg="white", bg="darkblue")
        header_label.pack(expand=True)
        
        # Main content frame
        main_frame = tk.Frame(self.root, bg="lightgray")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Statistics frame
        stats_frame = tk.LabelFrame(main_frame, text="📈 Quick Statistics", 
                                   font=("Arial", 12, "bold"), bg="white")
        stats_frame.pack(fill="x", pady=(0, 20))
        
        self.stats_text = tk.Text(stats_frame, height=8, font=("Courier", 10))
        self.stats_text.pack(fill="x", padx=10, pady=10)
        
        # Buttons frame
        buttons_frame = tk.LabelFrame(main_frame, text="🎨 Generate Visualizations", 
                                     font=("Arial", 12, "bold"), bg="white")
        buttons_frame.pack(fill="x", pady=(0, 20))
        
        # Create button grid
        button_data = [
            ("📊 Vote Distribution", self.plot_vote_dist, "lightgreen"),
            ("🔍 Verification Scores", self.plot_verification, "lightblue"),
            ("👁️ Biometric Analysis", self.plot_biometric, "lightyellow"),
            ("⏰ Time Analysis", self.plot_time, "lightcoral"),
            ("📋 Full Report", self.generate_report, "lightpink"),
            ("🎨 All Charts", self.generate_all, "lightcyan")
        ]
        
        for i, (text, command, color) in enumerate(button_data):
            row = i // 3
            col = i % 3
            btn = tk.Button(buttons_frame, text=text, font=("Arial", 10, "bold"),
                           width=20, height=2, bg=color, command=command)
            btn.grid(row=row, column=col, padx=10, pady=10)
        
        # Progress frame
        progress_frame = tk.Frame(main_frame, bg="lightgray")
        progress_frame.pack(fill="x")
        
        self.progress_var = tk.StringVar()
        self.progress_label = tk.Label(progress_frame, textvariable=self.progress_var,
                                      font=("Arial", 10), bg="lightgray")
        self.progress_label.pack()
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.pack(fill="x", pady=10)
        
        # Load initial stats
        self.update_stats()
    
    def update_stats(self):
        """Update statistics display"""
        try:
            df = self.visualizer.prepare_combined_data()
            
            if df.empty:
                stats_text = "No voting data available yet.\nStart voting to see statistics!"
            else:
                total_votes = len(df)
                vote_counts = df['party'].value_counts()
                avg_score = df['verification_score'].mean()
                
                stats_text = f"📊 CURRENT STATISTICS\n"
                stats_text += f"{'='*40}\n"
                stats_text += f"Total Votes: {total_votes}\n"
                stats_text += f"Average Score: {avg_score:.3f}\n\n"
                stats_text += f"Party-wise Results:\n"
                for party, count in vote_counts.items():
                    percentage = (count/total_votes)*100
                    stats_text += f"  {party}: {count} ({percentage:.1f}%)\n"
            
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(1.0, stats_text)
            
        except Exception as e:
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(1.0, f"Error loading statistics: {str(e)}")
    
    def start_progress(self, message):
        """Start progress indication"""
        self.progress_var.set(message)
        self.progress_bar.start()
        self.root.update()
    
    def stop_progress(self, message="Ready"):
        """Stop progress indication"""
        self.progress_bar.stop()
        self.progress_var.set(message)
        self.root.update()
    
    def plot_vote_dist(self):
        self.start_progress("Generating vote distribution charts...")
        try:
            self.visualizer.plot_vote_distribution()
            self.stop_progress("✅ Vote distribution charts generated!")
            self.update_stats()
        except Exception as e:
            self.stop_progress("❌ Error generating charts")
            messagebox.showerror("Error", f"Failed to generate charts: {str(e)}")
    
    def plot_verification(self):
        self.start_progress("Analyzing verification scores...")
        try:
            self.visualizer.plot_verification_scores()
            self.stop_progress("✅ Verification analysis completed!")
        except Exception as e:
            self.stop_progress("❌ Error in analysis")
            messagebox.showerror("Error", f"Failed to analyze scores: {str(e)}")
    
    def plot_biometric(self):
        self.start_progress("Generating biometric analysis...")
        try:
            self.visualizer.plot_biometric_analysis()
            self.stop_progress("✅ Biometric analysis completed!")
        except Exception as e:
            self.stop_progress("❌ Error in biometric analysis")
            messagebox.showerror("Error", f"Failed to analyze biometrics: {str(e)}")
    
    def plot_time(self):
        self.start_progress("Analyzing time patterns...")
        try:
            self.visualizer.plot_time_analysis()
            self.stop_progress("✅ Time analysis completed!")
        except Exception as e:
            self.stop_progress("❌ Error in time analysis")
            messagebox.showerror("Error", f"Failed to analyze time patterns: {str(e)}")
    
    def generate_report(self):
        self.start_progress("Generating comprehensive report...")
        try:
            self.visualizer.generate_comprehensive_report()
            self.stop_progress("✅ Comprehensive report generated!")
        except Exception as e:
            self.stop_progress("❌ Error generating report")
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
    
    def generate_all(self):
        self.start_progress("Generating all visualizations...")
        try:
            self.visualizer.create_all_visualizations()
            self.stop_progress("✅ All visualizations completed!")
            self.update_stats()
            messagebox.showinfo("Success", "All visualizations generated successfully!\nCheck the 'results/' folder.")
        except Exception as e:
            self.stop_progress("❌ Error generating visualizations")
            messagebox.showerror("Error", f"Failed to generate all visualizations: {str(e)}")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    dashboard = ResultsDashboard()
    dashboard.run()
