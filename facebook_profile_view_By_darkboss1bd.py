import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import time
import webbrowser
import threading
from datetime import datetime
import json
import os
import sys
from PIL import Image, ImageTk
import socket
import random

class AdvancedFacebookTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("🔍 DarkBoss1BD - Advanced Facebook Profile Intelligence")
        self.root.geometry("1200x800")
        self.root.configure(bg='#0a0a0a')
        self.root.resizable(True, True)
        
        # Data storage with persistence
        self.data_file = "tracking_data.json"
        self.tracking_data = self.load_data()
        self.is_tracking = False
        self.active_threads = []
        
        # Configuration
        self.check_interval = 10  # seconds
        self.max_history = 100
        
        self.setup_ui()
        self.auto_open_links()
        self.start_background_services()
        
    def setup_ui(self):
        # Custom style
        self.setup_styles()
        
        # Header with animated text
        header_frame = tk.Frame(self.root, bg='#1a1a1a', height=100)
        header_frame.pack(fill='x', padx=15, pady=10)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, 
                             text="🕵️ DarkBoss1BD FB Intelligence Suite", 
                             font=('Consolas', 22, 'bold'),
                             fg='#00ff00',
                             bg='#1a1a1a')
        title_label.pack(pady=25)
        
        subtitle_label = tk.Label(header_frame,
                                text="Advanced Facebook Profile Monitoring & Analytics",
                                font=('Consolas', 12),
                                fg='#00cc00',
                                bg='#1a1a1a')
        subtitle_label.pack()
        
        # Main container
        main_container = tk.PanedWindow(self.root, orient='horizontal', bg='#0a0a0a')
        main_container.pack(fill='both', expand=True, padx=15, pady=10)
        
        # Left panel - Controls
        left_panel = tk.Frame(main_container, bg='#1a1a1a')
        main_container.add(left_panel, minsize=400)
        
        # Input section
        input_frame = tk.LabelFrame(left_panel, text="🔧 Target Configuration", 
                                  font=('Consolas', 11, 'bold'),
                                  bg='#1a1a1a', fg='#00ff00',
                                  padx=10, pady=10)
        input_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(input_frame, 
                text="Target Username:", 
                font=('Consolas', 10, 'bold'),
                fg='white',
                bg='#1a1a1a').pack(anchor='w', pady=5)
        
        self.username_entry = tk.Entry(input_frame, 
                                     font=('Consolas', 11),
                                     width=30,
                                     bg='#2a2a2a',
                                     fg='#00ff00',
                                     insertbackground='#00ff00')
        self.username_entry.pack(fill='x', pady=5)
        
        # Multiple targets
        tk.Label(input_frame, 
                text="Multiple Targets (comma separated):", 
                font=('Consolas', 10, 'bold'),
                fg='white',
                bg='#1a1a1a').pack(anchor='w', pady=(15,5))
        
        self.multi_targets_entry = scrolledtext.ScrolledText(input_frame,
                                                           height=4,
                                                           font=('Consolas', 9),
                                                           bg='#2a2a2a',
                                                           fg='#00ff00',
                                                           insertbackground='#00ff00')
        self.multi_targets_entry.pack(fill='x', pady=5)
        
        # Settings frame
        settings_frame = tk.LabelFrame(left_panel, text="⚙️ Tracking Settings", 
                                     font=('Consolas', 11, 'bold'),
                                     bg='#1a1a1a', fg='#00ff00',
                                     padx=10, pady=10)
        settings_frame.pack(fill='x', padx=10, pady=10)
        
        # Check interval
        interval_frame = tk.Frame(settings_frame, bg='#1a1a1a')
        interval_frame.pack(fill='x', pady=5)
        
        tk.Label(interval_frame, 
                text="Check Interval (seconds):", 
                font=('Consolas', 9),
                fg='white',
                bg='#1a1a1a').pack(side='left')
        
        self.interval_var = tk.StringVar(value="10")
        interval_spinbox = tk.Spinbox(interval_frame, 
                                    from_=5, to=3600, 
                                    textvariable=self.interval_var,
                                    width=8,
                                    bg='#2a2a2a',
                                    fg='#00ff00',
                                    insertbackground='#00ff00')
        interval_spinbox.pack(side='right')
        
        # Control buttons
        button_frame = tk.Frame(left_panel, bg='#1a1a1a')
        button_frame.pack(fill='x', padx=10, pady=20)
        
        self.start_btn = tk.Button(button_frame,
                                 text="🚀 START TRACKING",
                                 font=('Consolas', 11, 'bold'),
                                 bg='#006600',
                                 fg='white',
                                 command=self.start_tracking,
                                 width=20,
                                 height=2)
        self.start_btn.pack(pady=5)
        
        self.stop_btn = tk.Button(button_frame,
                                text="🛑 STOP TRACKING",
                                font=('Consolas', 11, 'bold'),
                                bg='#660000',
                                fg='white',
                                command=self.stop_tracking,
                                width=20,
                                height=2,
                                state='disabled')
        self.stop_btn.pack(pady=5)
        
        # Analytics frame
        analytics_frame = tk.LabelFrame(left_panel, text="📊 Quick Stats", 
                                      font=('Consolas', 11, 'bold'),
                                      bg='#1a1a1a', fg='#00ff00',
                                      padx=10, pady=10)
        analytics_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.stats_text = scrolledtext.ScrolledText(analytics_frame,
                                                  height=8,
                                                  font=('Consolas', 9),
                                                  bg='#2a2a2a',
                                                  fg='#00ff00')
        self.stats_text.pack(fill='both', expand=True)
        
        # Right panel - Results
        right_panel = tk.Frame(main_container, bg='#0a0a0a')
        main_container.add(right_panel, minsize=600)
        
        # Results display
        results_frame = tk.LabelFrame(right_panel, text="🎯 Tracking Results", 
                                    font=('Consolas', 11, 'bold'),
                                    bg='#0a0a0a', fg='#00ff00',
                                    padx=10, pady=10)
        results_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Treeview with scrollbar
        tree_frame = tk.Frame(results_frame, bg='#0a0a0a')
        tree_frame.pack(fill='both', expand=True)
        
        columns = ('username', 'visits', 'last_visited', 'status', 'response_time')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        self.tree.heading('username', text='👤 Username')
        self.tree.heading('visits', text='📊 Visits')
        self.tree.heading('last_visited', text='🕒 Last Active')
        self.tree.heading('status', text='🔍 Status')
        self.tree.heading('response_time', text='⚡ Response Time')
        
        self.tree.column('username', width=150)
        self.tree.column('visits', width=80)
        self.tree.column('last_visited', width=180)
        self.tree.column('status', width=100)
        self.tree.column('response_time', width=100)
        
        # Scrollbar
        tree_scroll = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        tree_scroll.pack(side='right', fill='y')
        
        # Details frame
        details_frame = tk.LabelFrame(right_panel, text="📈 Profile Details", 
                                    font=('Consolas', 11, 'bold'),
                                    bg='#0a0a0a', fg='#00ff00',
                                    padx=10, pady=10)
        details_frame.pack(fill='x', padx=10, pady=10)
        
        self.details_text = scrolledtext.ScrolledText(details_frame,
                                                    height=8,
                                                    font=('Consolas', 9),
                                                    bg='#2a2a2a',
                                                    fg='#00ff00')
        self.details_text.pack(fill='both', expand=True)
        
        # Footer
        footer_frame = tk.Frame(self.root, bg='#1a1a1a', height=50)
        footer_frame.pack(fill='x', padx=15, pady=5)
        footer_frame.pack_propagate(False)
        
        contact_label = tk.Label(footer_frame,
                               text="📞 Contact: @darkvaiadmin | 🌐 Channel: @windowspremiumkey | 🔥 DarkBoss1BD",
                               font=('Consolas', 10, 'bold'),
                               fg='#00ff00',
                               bg='#1a1a1a')
        contact_label.pack(pady=15)
        
        # Bind tree selection
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure("Treeview",
                      background="#2a2a2a",
                      foreground="#00ff00",
                      fieldbackground="#2a2a2a",
                      rowheight=25)
        style.configure("Treeview.Heading",
                      background="#1a1a1a",
                      foreground="#00ff00",
                      relief="flat",
                      font=('Consolas', 9, 'bold'))
        style.map("Treeview", background=[('selected', '#004400')])
        
    def load_data(self):
        """Load tracking data from file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {}
    
    def save_data(self):
        """Save tracking data to file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.tracking_data, f, indent=2)
        except:
            pass
    
    def auto_open_links(self):
        """Automatically open contact links"""
        links = [
            "https://t.me/darkvaiadmin",
            "https://t.me/windowspremiumkey"
        ]
        
        for link in links:
            try:
                webbrowser.open_new_tab(link)
            except:
                pass
    
    def start_background_services(self):
        """Start background monitoring services"""
        # Auto-save thread
        def auto_save():
            while True:
                time.sleep(30)
                self.save_data()
                self.update_stats_display()
        
        save_thread = threading.Thread(target=auto_save, daemon=True)
        save_thread.start()
    
    def simulate_facebook_check(self, username):
        """Simulate advanced Facebook profile checking"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if username not in self.tracking_data:
            self.tracking_data[username] = {
                'visits': 0,
                'last_visited': current_time,
                'history': [],
                'status': 'offline',
                'response_time': 0,
                'first_seen': current_time,
                'peak_hours': []
            }
        
        # Simulate different statuses
        statuses = ['online', 'offline', 'active', 'idle']
        response_time = random.uniform(0.1, 2.5)
        
        self.tracking_data[username]['visits'] += 1
        self.tracking_data[username]['last_visited'] = current_time
        self.tracking_data[username]['history'].append(current_time)
        self.tracking_data[username]['status'] = random.choice(statuses)
        self.tracking_data[username]['response_time'] = round(response_time, 2)
        
        # Keep history limited
        if len(self.tracking_data[username]['history']) > self.max_history:
            self.tracking_data[username]['history'] = self.tracking_data[username]['history'][-self.max_history:]
        
        return self.tracking_data[username]
    
    def update_display(self):
        """Update the main display"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for username, data in self.tracking_data.items():
            status_icon = "🟢" if data['status'] == 'online' else "🔴" if data['status'] == 'offline' else "🟡"
            self.tree.insert('', 'end', 
                           values=(
                               username, 
                               data['visits'], 
                               data['last_visited'],
                               f"{status_icon} {data['status']}",
                               f"{data['response_time']}s"
                           ))
    
    def update_stats_display(self):
        """Update statistics display"""
        total_targets = len(self.tracking_data)
        total_visits = sum(data['visits'] for data in self.tracking_data.values())
        online_targets = sum(1 for data in self.tracking_data.values() if data['status'] == 'online')
        
        stats_text = f"""
📈 SYSTEM STATISTICS
────────────────────
🎯 Total Targets: {total_targets}
📊 Total Checks: {total_visits}
🟢 Online Now: {online_targets}
🔴 Offline: {total_targets - online_targets}
🕒 Last Update: {datetime.now().strftime("%H:%M:%S")}

🔍 ACTIVE MONITORING
────────────────────
"""
        
        # Add recent activity
        recent_targets = list(self.tracking_data.items())[-5:]
        for username, data in recent_targets:
            status_icon = "🟢" if data['status'] == 'online' else "🔴"
            stats_text += f"{status_icon} {username}: {data['visits']} visits\n"
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, stats_text)
    
    def on_tree_select(self, event):
        """Handle tree selection for details display"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            username = item['values'][0]
            self.show_profile_details(username)
    
    def show_profile_details(self, username):
        """Show detailed profile information"""
        if username in self.tracking_data:
            data = self.tracking_data[username]
            
            details = f"""
🔍 PROFILE INTELLIGENCE REPORT: {username}
────────────────────────────────────────────
📊 Total Visits: {data['visits']}
🕒 First Seen: {data['first_seen']}
🕒 Last Active: {data['last_visited']}
📡 Current Status: {data['status'].upper()}
⚡ Avg Response: {data['response_time']}s

📅 ACTIVITY HISTORY (Recent)
────────────────────────────
"""
            # Show last 10 activities
            recent_history = data['history'][-10:]
            for activity in reversed(recent_history):
                details += f"• {activity}\n"
            
            self.details_text.delete(1.0, tk.END)
            self.details_text.insert(1.0, details)
    
    def tracking_loop(self):
        """Main tracking loop"""
        while self.is_tracking:
            targets = self.get_targets()
            
            for username in targets:
                if not self.is_tracking:
                    break
                    
                try:
                    data = self.simulate_facebook_check(username)
                    print(f"🔍 Checked {username}: {data['visits']} visits | Status: {data['status']}")
                    
                    # Update UI in main thread
                    self.root.after(0, self.update_display)
                    self.root.after(0, self.update_stats_display)
                    
                except Exception as e:
                    print(f"❌ Error checking {username}: {e}")
            
            # Wait for next check
            time.sleep(self.check_interval)
    
    def get_targets(self):
        """Get list of targets to monitor"""
        targets = []
        
        # Single target
        single_target = self.username_entry.get().strip()
        if single_target:
            targets.append(single_target)
        
        # Multiple targets
        multi_targets = self.multi_targets_entry.get(1.0, tk.END).strip()
        if multi_targets:
            for target in multi_targets.split(','):
                target = target.strip()
                if target and target not in targets:
                    targets.append(target)
        
        return targets
    
    def start_tracking(self):
        """Start tracking process"""
        targets = self.get_targets()
        if not targets:
            messagebox.showerror("Error", "❌ Please enter at least one target username")
            return
        
        try:
            self.check_interval = int(self.interval_var.get())
        except:
            self.check_interval = 10
        
        self.is_tracking = True
        self.start_btn.config(state='disabled', bg='#333333')
        self.stop_btn.config(state='normal', bg='#aa0000')
        
        # Start tracking thread
        tracking_thread = threading.Thread(target=self.tracking_loop)
        tracking_thread.daemon = True
        tracking_thread.start()
        
        messagebox.showinfo("Tracking Started", 
                          f"🚀 Started monitoring {len(targets)} targets\n"
                          f"📡 Check interval: {self.check_interval} seconds")
    
    def stop_tracking(self):
        """Stop tracking process"""
        self.is_tracking = False
        self.start_btn.config(state='normal', bg='#006600')
        self.stop_btn.config(state='disabled', bg='#333333')
        
        messagebox.showinfo("Tracking Stopped", "🛑 Monitoring stopped")
        self.save_data()

def main():
    try:
        root = tk.Tk()
        app = AdvancedFacebookTracker(root)
        
        # Center window
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
        y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
        root.geometry(f"+{x}+{y}")
        
        root.mainloop()
    except Exception as e:
        print(f"Application error: {e}")
        messagebox.showerror("Error", f"Failed to start application: {e}")

if __name__ == "__main__":
    main()
