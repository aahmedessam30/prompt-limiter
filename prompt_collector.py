import sys
import argparse
import re
from typing import Dict, Any, Optional

# Configuration constants
USER_PREFERENCES = {
    "default_interface": "terminal",  # Options: "terminal", "gui"
}

AVAILABLE_INTERFACES = {
    "terminal": "Terminal Interface (Textual) - Best for developers",
    "gui": "Graphical Interface (Tkinter) - User-friendly with buttons and RTL support",
}

# Check for optional dependencies and import them conditionally
try:
    from textual.app import App, ComposeResult
    from textual.widgets import Static, TextArea
    from textual.containers import Container, Vertical
    from textual.screen import ModalScreen
    from textual.binding import Binding
    from textual import events
    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, scrolledtext
    import pyperclip
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False
    pyperclip = None


class TextAnalysisHelper:
    """Enhanced Arabic text processing and Right-to-Left language detection."""

    @staticmethod
    def contains_arabic_characters(text: str) -> bool:
        """
        Determine if text contains Arabic characters.
        
        Args:
            text: Input text to analyze
            
        Returns:
            True if text has significant Arabic content (>30%), False otherwise
        """
        if not text.strip():
            return False

        arabic_character_count = 0
        total_meaningful_characters = 0

        for character in text:
            if character.strip() and not character.isspace():
                total_meaningful_characters += 1
                # Check if character is in Arabic Unicode ranges
                if "\u0600" <= character <= "\u06ff" or "\u0750" <= character <= "\u077f":
                    arabic_character_count += 1

        return (total_meaningful_characters > 0 and 
                (arabic_character_count / total_meaningful_characters) > 0.3)

    @staticmethod
    def count_words_in_text(text: str) -> int:
        """
        Count words in text, handling both Arabic and non-Arabic languages.
        
        Args:
            text: Input text to count words in
            
        Returns:
            Total word count
        """
        if not TextAnalysisHelper.contains_arabic_characters(text):
            return len(text.split())

        # Arabic word pattern - sequences of Arabic characters
        arabic_word_pattern = r"[\u0600-\u06FF\u0750-\u077F]+"
        arabic_words = re.findall(arabic_word_pattern, text)

        # Extract and count non-Arabic words
        text_without_arabic = re.sub(arabic_word_pattern, " ", text)
        non_arabic_words = [word for word in text_without_arabic.split() if word.strip()]

        return len(arabic_words) + len(non_arabic_words)

    @staticmethod
    def get_comprehensive_text_statistics(text: str) -> Dict[str, Any]:
        """
        Get detailed text analysis including language detection and statistics.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with text statistics and language information
        """
        is_arabic_text = TextAnalysisHelper.contains_arabic_characters(text)
        word_count = TextAnalysisHelper.count_words_in_text(text)
        character_count = len(text)
        line_count = len(text.splitlines())

        return {
            "is_arabic": is_arabic_text,
            "word_count": word_count,
            "char_count": character_count,
            "line_count": line_count,
            "is_rtl": is_arabic_text,  # Right-to-left if Arabic
        }


# Textual Terminal Interface Classes
if TEXTUAL_AVAILABLE:

    class InteractiveInputModal(ModalScreen):
        """Fullscreen interactive modal with multiline text input - keyboard only"""

        BINDINGS = [
            Binding("ctrl+s", "send", "Send Text", priority=True),
            Binding("ctrl+a", "select_all", "Select All", priority=True),
            Binding("ctrl+c", "copy", "Copy", priority=True),
            Binding("ctrl+v", "paste", "Paste", priority=True),
            Binding("escape", "cancel", "Cancel", priority=True),
            Binding("ctrl+enter", "send", "Send Text", priority=True),
            Binding("ctrl+q", "cancel", "Cancel", priority=True),
        ]

        CSS = """
        InteractiveInputModal {
            align: center middle;
        }
        #input_area {
            height: 1fr;
            border: solid $accent;
            margin: 1;
            background: $surface;
        }
        #status_bar {
            height: 2;
            background: $primary;
            color: $text;
            margin: 1;
            padding: 0;
            text-align: center;
            dock: bottom;
        }
        #modal_title {
            text-align: center;
            margin: 1;
            color: $accent;
            background: $primary;
            height: 2;
            padding: 0;
            dock: top;
        }
        """

        def __init__(self):
            super().__init__()
            self.result_text = ""

        def compose(self) -> ComposeResult:
            yield Static("FULLSCREEN TEXT EDITOR", id="modal_title")
            yield TextArea(text="", id="input_area")
            yield Static(
                "START TYPING - Ctrl+S=SEND | Esc=CANCEL | Ctrl+C=Copy | Ctrl+V=Paste",
                id="status_bar",
            )

        def on_mount(self):
            """Focus the text area when modal opens"""
            self.query_one("#input_area", TextArea).focus()

        def action_send(self):
            """Send the text and close modal"""
            textarea = self.query_one("#input_area", TextArea)
            self.result_text = textarea.text
            if self.result_text.strip():  # Only send if there's actual content
                self.dismiss(self.result_text)
            else:
                self.update_status("ERROR: No text to send! Type something first.")

        def action_cancel(self):
            """Cancel and close modal"""
            self.dismiss(None)

        def action_select_all(self):
            """Select all text in the textarea"""
            textarea = self.query_one("#input_area", TextArea)
            textarea.select_all()
            self.update_status("SUCCESS: All text selected!")

        def action_copy(self):
            """Copy all text to clipboard"""
            textarea = self.query_one("#input_area", TextArea)
            text_to_copy = (
                textarea.selected_text if textarea.selected_text else textarea.text
            )
            if text_to_copy:
                try:
                    if pyperclip:
                        pyperclip.copy(text_to_copy)
                        if textarea.selected_text:
                            self.update_status(
                                "SUCCESS: Selected text copied to clipboard!"
                            )
                        else:
                            self.update_status("SUCCESS: All text copied to clipboard!")
                    else:
                        self.update_status("ERROR: pyperclip not available!")
                except Exception as e:
                    self.update_status(f"ERROR: Copy failed - {str(e)}")
            else:
                self.update_status("ERROR: No text to copy!")

        def action_paste(self):
            """Paste text from clipboard"""
            textarea = self.query_one("#input_area", TextArea)
            try:
                if pyperclip:
                    clipboard_text = pyperclip.paste()
                    if clipboard_text:
                        textarea.insert(clipboard_text)
                        self.update_status("SUCCESS: Text pasted from clipboard!")
                    else:
                        self.update_status("ERROR: Clipboard is empty!")
                else:
                    self.update_status("ERROR: pyperclip not available!")
            except Exception as e:
                self.update_status(f"ERROR: Paste failed - {str(e)}")

        def update_status(self, message: str = ""):
            """Update the status bar"""
            try:
                textarea = self.query_one("#input_area", TextArea)
                lines = len(textarea.text.split("\n"))
                chars = len(textarea.text)
                if message:
                    status_text = f"{message} | Lines: {lines} | Chars: {chars}"
                elif chars == 0:
                    # Show initial message when no text
                    status_text = "START TYPING - Ctrl+S=SEND | Esc=CANCEL | Ctrl+C=Copy | Ctrl+V=Paste"
                else:
                    status_text = f"Lines: {lines} | Characters: {chars} | Ctrl+S=Send | Esc=Cancel"
                status_bar = self.query_one("#status_bar", Static)
                status_bar.update(status_text)
            except Exception:
                # If there's an error, just show basic info
                try:
                    status_bar = self.query_one("#status_bar", Static)
                    status_bar.update("START TYPING - Ctrl+S=SEND | Esc=CANCEL")
                except:
                    pass

        def on_text_area_changed(self, event: TextArea.Changed):
            """Update status when text changes"""
            self.update_status()

    class MainApp(App):
        """Direct fullscreen text editor - opens immediately"""

        def __init__(self):
            super().__init__()
            self.user_input = ""

        def compose(self) -> ComposeResult:
            # Don't yield anything - we'll open the modal immediately
            return []

        def on_mount(self):
            """Immediately open the text editor when app starts"""
            self.open_text_editor()

        def open_text_editor(self):
            """Open the text editor modal"""

            def handle_result(result):
                if result:
                    self.user_input = result
                    # Just print success message - no file saving
                    print(f"\n{'='*60}")
                    print("📝 USER INPUT RECEIVED")
                    print(f"{'='*60}")

                    # Get comprehensive text analysis
                    text_stats = TextAnalysisHelper.get_comprehensive_text_statistics(result)
                    print(f"📊 Text Analysis:")
                    print(f"   Lines: {text_stats['line_count']}")
                    print(f"   Characters: {text_stats['char_count']}")
                    print(f"   Words: {text_stats['word_count']}")
                    if text_stats["is_arabic"]:
                        print(f"   Language: Arabic/RTL detected")

                    print(f"📋 Content:")
                    print("-" * 60)
                    print(result)
                    print("-" * 60)
                    print("✅ Task completed successfully!")
                    self.exit()
                else:
                    # No message for cancelled input
                    self.exit()

            self.push_screen(InteractiveInputModal(), handle_result)


class EnhancedTkinterInterface:
    """Modern Tkinter-based GUI interface with Arabic/RTL support."""

    def __init__(self):
        self.user_input_result = None
        self.root_window = None

    def create_user_interface(self):
        """Create and configure the tkinter interface with improved layout."""
        self.root_window = tk.Tk()
        self.root_window.title("Enhanced User Input Interface")
        self.root_window.geometry("900x700") 

        # Configure better font support for international text
        try:
            self.root_window.option_add("*Font", "Arial 12")
        except Exception:
            pass

        # Main frame container
        main_container = ttk.Frame(self.root_window)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Application title
        title_label = ttk.Label(
            main_container, 
            text="Enhanced User Input Interface", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 10))

        # Text input area with scrolling - REDUCED HEIGHT
        text_input_frame = ttk.Frame(main_container)
        text_input_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.text_input_area = scrolledtext.ScrolledText(
            text_input_frame,
            wrap=tk.WORD,
            width=80,
            height=20,  # REDUCED from 25 to 18 to ensure buttons are visible
            font=("Arial", 12),
        )
        self.text_input_area.pack(fill=tk.BOTH, expand=False)  # Changed from expand=True to False

        # Status information display
        self.status_display_label = ttk.Label(main_container, text="Ready to type...")
        self.status_display_label.pack(pady=(5, 10))

        # RTL language toggle control
        self.rtl_mode_enabled = tk.BooleanVar()
        rtl_toggle_checkbox = ttk.Checkbutton(
            main_container,
            text="Enable RTL (Right-to-Left Text Direction)",
            variable=self.rtl_mode_enabled,
            command=self.toggle_text_direction,
        )
        rtl_toggle_checkbox.pack(pady=(0, 10))

        # Text manipulation buttons - ALWAYS VISIBLE NOW
        button_container = ttk.Frame(main_container)
        button_container.pack(fill=tk.X, pady=(0, 10), side=tk.BOTTOM)  # Added side=tk.BOTTOM

        ttk.Button(button_container, text="Copy Text", command=self.copy_text_to_clipboard).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        ttk.Button(button_container, text="Paste Text", command=self.paste_text_from_clipboard).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        ttk.Button(button_container, text="Clear All", command=self.clear_all_text).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        ttk.Button(button_container, text="Select All", command=self.select_all_text).pack(
            side=tk.LEFT, padx=(0, 5)
        )

        # Submit and Cancel action buttons - ALWAYS VISIBLE NOW
        action_button_container = ttk.Frame(main_container)
        action_button_container.pack(fill=tk.X, side=tk.BOTTOM)  # Added side=tk.BOTTOM

        ttk.Button(action_button_container, text="Cancel", command=self.cancel_input).pack(
            side=tk.RIGHT, padx=(5, 0)
        )
        ttk.Button(action_button_container, text="Submit", command=self.submit_input).pack(
            side=tk.RIGHT
        )

        # Event bindings for keyboard shortcuts
        self.text_input_area.bind("<KeyRelease>", self.handle_text_change_event)
        self.text_input_area.bind("<Control-Return>", lambda e: self.submit_input())
        self.text_input_area.bind("<Control-a>", lambda e: self.select_all_text())
        self.text_input_area.bind("<Control-A>", lambda e: self.select_all_text())
        self.root_window.bind("<Control-s>", lambda e: self.submit_input())
        self.root_window.bind("<Escape>", lambda e: self.cancel_input())

        # Set focus and handle window closing
        self.text_input_area.focus_set()
        self.root_window.protocol("WM_DELETE_WINDOW", self.cancel_input)

    def toggle_text_direction(self):
        """Toggle between LTR and RTL text direction with proper Arabic support."""
        try:
            if self.rtl_mode_enabled.get():
                # Enable RTL mode
                self.text_input_area.config(wrap=tk.WORD)
                self.text_input_area.tag_configure("rtl_text", justify=tk.RIGHT)
                self.text_input_area.tag_add("rtl_text", "1.0", tk.END)
                self.text_input_area.configure(insertofftime=0)
            else:
                # Enable LTR mode
                self.text_input_area.config(wrap=tk.WORD)
                self.text_input_area.tag_configure("ltr_text", justify=tk.LEFT)
                self.text_input_area.tag_add("ltr_text", "1.0", tk.END)
                self.text_input_area.configure(insertofftime=0)
        except Exception as e:
            print(f"Text direction toggle error: {e}")

    def handle_text_change_event(self, event=None):
        """Handle text change events and auto-apply RTL for Arabic text."""
        current_text = self.text_input_area.get("1.0", tk.END).rstrip("\n")
        text_statistics = TextAnalysisHelper.get_comprehensive_text_statistics(current_text)

        status_message = f"Lines: {text_statistics['line_count']} | Characters: {text_statistics['char_count']}"
        if text_statistics["word_count"] > 0:
            status_message += f" | Words: {text_statistics['word_count']}"
        if text_statistics["is_arabic"]:
            status_message += " | Arabic detected"
            # Auto-enable RTL for Arabic text
            if not self.rtl_mode_enabled.get():
                self.rtl_mode_enabled.set(True)
                self.toggle_text_direction()

        # Apply appropriate text formatting
        if text_statistics["is_arabic"] and self.rtl_mode_enabled.get():
            self.text_input_area.tag_add("rtl_text", "1.0", tk.END)
        elif not text_statistics["is_arabic"]:
            self.text_input_area.tag_add("ltr_text", "1.0", tk.END)

        self.status_display_label.config(text=status_message)

    def copy_text_to_clipboard(self):
        """Copy all text content to system clipboard."""
        try:
            text_content = self.text_input_area.get("1.0", tk.END).rstrip("\n")
            if pyperclip and text_content:
                pyperclip.copy(text_content)
                self.status_display_label.config(text="Text copied to clipboard!")
                self.root_window.after(2000, lambda: self.handle_text_change_event())
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy text: {e}")

    def paste_text_from_clipboard(self):
        """Paste text content from system clipboard."""
        try:
            if pyperclip:
                clipboard_content = pyperclip.paste()
                if clipboard_content:
                    self.text_input_area.insert(tk.INSERT, clipboard_content)
                    self.handle_text_change_event()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to paste text: {e}")

    def clear_all_text(self):
        """Clear all text from the input area."""
        self.text_input_area.delete("1.0", tk.END)
        self.handle_text_change_event()

    def select_all_text(self):
        """Select all text in the input area with improved Arabic support."""
        try:
            # Clear existing selection and select all
            self.text_input_area.tag_remove(tk.SEL, "1.0", tk.END)
            self.text_input_area.tag_add(tk.SEL, "1.0", tk.END)
            self.text_input_area.mark_set(tk.INSERT, "1.0")
            self.text_input_area.see(tk.INSERT)
            
            self.status_display_label.config(text="All text selected! Use Ctrl+C to copy.")
            self.text_input_area.focus_set()
            return "break"
        except Exception as e:
            print(f"Select all text error: {e}")
            return "break"

    def submit_input(self):
        """Submit the entered text and close interface."""
        text_content = self.text_input_area.get("1.0", tk.END).rstrip("\n")
        if text_content.strip():
            self.user_input_result = text_content.strip()
        self.root_window.quit()
        self.root_window.destroy()

    def cancel_input(self):
        """Cancel input and close interface without saving."""
        self.user_input_result = None
        self.root_window.quit()
        self.root_window.destroy()

    def run_interface(self):
        """Run the GUI interface and return the user input result."""
        if not (tk and ttk and scrolledtext):
            return None
        try:
            self.create_user_interface()
            self.root_window.mainloop()
            return self.user_input_result
        except Exception:
            return None


class UserInterfaceManager:
    """Main interface manager with enhanced user preferences and selection capabilities."""

    def __init__(self):
        self.current_user_input = None
        self.selected_interface_type = USER_PREFERENCES["default_interface"]

    def update_default_interface_preference(self, interface_type: str):
        """
        Update the default interface preference and persist to configuration.
        
        Args:
            interface_type: The interface type to set as default
        """
        if interface_type in AVAILABLE_INTERFACES:
            # Update in-memory preference
            USER_PREFERENCES["default_interface"] = interface_type
            self.selected_interface_type = interface_type

            # Attempt to persist the preference to the file
            try:
                # Read current file content
                with open(__file__, "r", encoding="utf-8") as file:
                    file_content = file.read()

                # Update the default_interface configuration line
                pattern = r'(\s*"default_interface":\s*")[^"]*(".*)'
                replacement = f"\\g<1>{interface_type}\\g<2>"
                updated_content = re.sub(pattern, replacement, file_content)

                # Write updated content back to file
                with open(__file__, "w", encoding="utf-8") as file:
                    file.write(updated_content)

                print(f"✅ Default interface permanently set to: {AVAILABLE_INTERFACES[interface_type]}")
                print(f"📝 Configuration saved to {__file__}")
            except Exception as persistence_error:
                print(f"⚠️ Settings updated for this session only. Failed to persist: {persistence_error}")
                print(f"✅ Default interface set to: {AVAILABLE_INTERFACES[interface_type]} (session only)")
        else:
            print(f"❌ Invalid interface type. Available options: {list(AVAILABLE_INTERFACES.keys())}")

    def display_available_interface_options(self):
        """Display all available interface options with current selection highlighted."""
        print("\n📋 Available Interface Options:")
        print("=" * 60)
        for interface_key, interface_description in AVAILABLE_INTERFACES.items():
            selection_indicator = "👉" if interface_key == self.selected_interface_type else "  "
            print(f"{selection_indicator} {interface_key}: {interface_description}")
        print(f"\n🔧 Current default interface: {self.selected_interface_type}")
        print("=" * 60)

    def get_available_interface_types(self):
        """
        Get list of currently available interface types based on installed dependencies.
        
        Returns:
            List of available interface type strings
        """
        available_interfaces = []

        if TEXTUAL_AVAILABLE:
            available_interfaces.append("terminal")
        if TKINTER_AVAILABLE:
            available_interfaces.append("gui")

        return available_interfaces

    def launch_terminal_interface(self):
        """Launch the Textual-based terminal interface."""
        if not TEXTUAL_AVAILABLE:
            print("❌ Textual library not available. Install with: pip install textual")
            return None

        try:
            terminal_app = MainApp()
            terminal_app.title = "Enhanced Fullscreen Text Editor"
            terminal_app.sub_title = "Keyboard-driven unlimited text input interface"
            terminal_app.run()
            return terminal_app.user_input
        except Exception as terminal_error:
            print(f"❌ Terminal interface error: {terminal_error}")
            return None

    def launch_gui_interface(self):
        """Launch the Tkinter-based GUI interface."""
        if not TKINTER_AVAILABLE:
            print("❌ Tkinter not available. GUI interface cannot be launched.")
            return None

        gui_interface = EnhancedTkinterInterface()
        return gui_interface.run_interface()

    def launch_simple_interface(self):
        """Simple interfaces are deprecated and no longer supported."""
        print("❌ Simple interface has been removed. Please use 'terminal' or 'gui' interface.")
        return None

    def run_selected_interface(self):
        """Run the appropriate interface based on current selection and availability."""
        interface_type = self.selected_interface_type

        # Validate interface availability and fallback if necessary
        available_interfaces = self.get_available_interface_types()
        if interface_type not in available_interfaces:
            if available_interfaces:
                interface_type = available_interfaces[0]
                print(f"⚠️ Selected interface '{self.selected_interface_type}' not available. Using '{interface_type}' instead.")
            else:
                print("❌ No interfaces available. Please install required dependencies.")
                return None

        # Launch the appropriate interface
        if interface_type == "terminal":
            return self.launch_terminal_interface()
        elif interface_type == "gui":
            return self.launch_gui_interface()
        else:
            print(f"❌ Unknown interface type: {interface_type}")
            return None


def run_enhanced_user_input_application():
    """
    Enhanced main function with improved argument parsing and user preferences.
    """
    argument_parser = argparse.ArgumentParser(
        description="Enhanced User Input Interface with multilingual support and user preferences",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Available Interface Types:
{chr(10).join(f"  {key}: {desc}" for key, desc in AVAILABLE_INTERFACES.items())}

Current Default Interface: {USER_PREFERENCES['default_interface']}

Usage Examples:
  python prompt_collector.py                          # Use default interface
  python prompt_collector.py --interface gui          # Override with GUI for this session
  python prompt_collector.py --show-interfaces        # Display available interfaces
  python prompt_collector.py --set-default terminal   # Set terminal as permanent default
        """,
    )

    argument_parser.add_argument(
        "--interface",
        choices=list(AVAILABLE_INTERFACES.keys()),
        help="Override default interface for this session only",
    )

    argument_parser.add_argument(
        "--set-default",
        choices=list(AVAILABLE_INTERFACES.keys()),
        help="Set and persist default interface preference",
    )

    argument_parser.add_argument(
        "--show-interfaces",
        action="store_true",
        help="Display available interfaces and current default setting",
    )

    parsed_arguments = argument_parser.parse_args()
    interface_manager = UserInterfaceManager()

    # Handle default interface preference setting
    if parsed_arguments.set_default:
        interface_manager.update_default_interface_preference(parsed_arguments.set_default)
        return

    # Display interface information if requested
    if parsed_arguments.show_interfaces:
        interface_manager.display_available_interface_options()
        return

    # Override interface selection if specified
    if parsed_arguments.interface:
        interface_manager.selected_interface_type = parsed_arguments.interface

    # Run the selected interface and return result
    user_input_result = interface_manager.run_selected_interface()
    return user_input_result


if __name__ == "__main__":
    try:
        run_enhanced_user_input_application()
    except KeyboardInterrupt:
        # Clean exit on user interrupt (Ctrl+C)
        sys.exit(1)
    except Exception:
        # Clean exit on any unexpected error
        sys.exit(1)
