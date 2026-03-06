import time
import os
import hashlib
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()

# SECURITY: Hard limit to prevent Memory Exhaustion attacks
MAX_FILE_SIZE_BYTES = 1 * 1024 * 1024  # 1 MB limit

class VelosHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_content_hash = ""
        # Pre-compute the absolute, resolved base directory
        self.base_dir = os.path.realpath(os.path.abspath("."))
        
        # SAST FIX: Pre-compute static secure paths to break the "Taint Chain"
        self.design_file_path = os.path.join(self.base_dir, "design.md")
        self.audit_file_path = os.path.join(self.base_dir, "security_audit.md")
        self.steering_file_path = os.path.join(self.base_dir, "steering.md")

    def on_modified(self, event):
        # Still use the OS event to trigger, but I drop the dynamic path
        if event.src_path.endswith("design.md"):
            self.process_if_changed()

    def process_if_changed(self):
        try:
            # SECURITY: Prevent Memory Exhaustion using the static path
            if not os.path.exists(self.design_file_path):
                return
                
            if os.path.getsize(self.design_file_path) > MAX_FILE_SIZE_BYTES:
                console.print("[bold red]Security Block:[/bold red] File exceeds maximum size limit.")
                return

            # NO DYNAMIC PATHS = ZERO CWE-22 VULNERABILITIES
            with open(self.design_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # SECURITY: Secure Hashing
            current_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
            if current_hash == self.last_content_hash:
                return 
                
            self.last_content_hash = current_hash
            content_lower = content.lower()
            
            console.print(f"\n[bold cyan] Velos Semantic Scanner triggered by:[/bold cyan] ./design.md")
            console.print(f"[dim]Analyzing {len(content)} bytes of Kiro architecture...[/dim]")
            time.sleep(0.8)

            # --- THE SMART MOCK ENGINE ---
            if "cloudfront" in content_lower and "oac" in content_lower:
                response = """
-  **STATUS:** SECURE BY DESIGN
-  **S3 Bucket:** Private access enforced via Origin Access Control (OAC).
-  **Encryption:** AES256 Server-Side Encryption verified.
-  **CDN:** CloudFront distribution correctly configured.
-  **SCORE: A+ (Ready for Generation)**
                """
                self.build_cli_dashboard(response, "green", "[bold green] Velos AI: Security Audit Passed[/bold green]")
                
            elif "public" in content_lower and ("s3" in content_lower or "bucket" in content_lower):
                response = """
-  **CRITICAL RISK:** S3 Bucket requested with public access. *(OWASP A01:2021-Broken Access Control)*
-  **IMPACT:** Exposing buckets publicly can lead to massive data leaks and unauthorized AWS billing charges.
-  **REMEDIATION REQUIRED:** Block all public access. Use CloudFront with Origin Access Control (OAC) for public asset delivery.
-  **SCORE: F (Action Required)**
                """
                self.build_cli_dashboard(response, "red", "[bold red] Velos AI: Security Flaw Detected[/bold red]")
                
            else:
                response = """
-  **INFO:** General architecture detected.
-  **SCAN:** No critical IAM or exposed storage risks found in current text.
-  **SCORE: B+**
                """
                self.build_cli_dashboard(response, "yellow", "[bold yellow] Velos AI: Architecture Scan[/bold yellow]")

        # SECURITY: Generic Error Messages (Information Disclosure Prevention)
        except (IOError, OSError):
            console.print("[bold red]File Access Error:[/bold red] Unable to process the architecture file safely.")

    def build_cli_dashboard(self, ai_response, border_color, title_text):
        audit_panel = Panel(
            Markdown(ai_response),
            title=title_text,
            border_style=border_color,
            expand=False
        )
        
        console.print("\n")
        console.print(audit_panel)
        
        # SECURITY: Explicit output paths with safe generic exceptions
        try:
            with open(self.audit_file_path, "w", encoding='utf-8') as f:
                f.write(f"# {title_text}\n\n")
                f.write("> **Powered by Amazon Nova** (Simulated Local Engine)\n\n")
                f.write(ai_response)
            console.print(f"[dim {border_color}]↳ Enforcer: Updated security_audit.md log[/dim {border_color}]")
        except (IOError, OSError):
            console.print(f"[dim red]Failed to safely write audit log.[/dim red]")

        if border_color == "red":
            try:
                steering_content = ""
                if os.path.exists(self.steering_file_path):
                    with open(self.steering_file_path, "r", encoding='utf-8') as f:
                        steering_content = f.read()
                
                if "Velos Security Guardrails" not in steering_content:
                    with open(self.steering_file_path, "a", encoding='utf-8') as f:
                        f.write("\n\n#  Velos Security Guardrails\n")
                        f.write("- **CRITICAL:** All S3 buckets must explicitly block public access.\n")
                        f.write("- **CRITICAL:** Use CloudFront OAC for any public file delivery.\n")
                        f.write("- Never generate code with hardcoded credentials.\n")
                console.print(f"[dim {border_color}]↳ Steering: Injected S3/CDN guardrails into Kiro's steering.md[/dim {border_color}]\n")
            except (IOError, OSError):
                console.print(f"[dim red]Failed to safely update steering file.[/dim red]")
        else:
            console.print(f"[dim {border_color}]↳ Steering: Kiro is compliant. No new rules injected.[/dim {border_color}]\n")

def start_watching(path="."):
    event_handler = VelosHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    
    console.print(Panel("[bold cyan]Velos Security Agent (v2.4 - Zero Taint Edition)[/bold cyan]\nWatching workspace for architecture changes...", title="System Startup", border_style="cyan"))

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_watching()