import sys
import os
from prompt_toolkit import PromptSession
from prompt_toolkit.application import Application
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.styles import Style
from prompt_toolkit.shortcuts import print_formatted_text

# Define style for prompt_toolkit
style = Style.from_dict({
    'promptname': 'fg:#ffffff',  # White for prompt names (e.g., "Path:")
    'prompttext': 'fg:#00b7eb',  # Sky blue for outer dots (◇, ◆, └)
    'output-dot': 'fg:#00ff00',  # Green for dots in final output
    'output-header': 'fg:#ffffff',  # White for headers in final output
    'output-done': 'fg:#00ff00 blink',  # Green blinking for "Done"
    # Main options (bold for selected, light colors)
    'install': 'fg:#99ff99 bold',   # Light Green
    'uninstall': 'fg:#ff6666 bold', # Light Red
    'upgrade': 'fg:#66ffff bold',   # Light Cyan
    'downgrade': 'fg:#ff99ff bold', # Light Magenta
    'manage': 'fg:#cccccc bold',    # Light White
    'start': 'fg:#9999ff bold',     # Light Bright Blue
    'restart': 'fg:#ffff66 bold',   # Light Yellow
    'reinstall': 'fg:#66cccc bold', # Light Bright Cyan
    # Main options (very light for unselected)
    'install-light': 'fg:#ccffcc',   # Very Light Green
    'uninstall-light': 'fg:#ff9999', # Very Light Red
    'upgrade-light': 'fg:#99ffff',   # Very Light Cyan
    'downgrade-light': 'fg:#ffccff', # Very Light Magenta
    'manage-light': 'fg:#e6e6e6',    # Very Light White
    'start-light': 'fg:#ccccff',     # Very Light Bright Blue
    'restart-light': 'fg:#ffff99',   # Very Light Yellow
    'reinstall-light': 'fg:#99cccc', # Very Light Bright Cyan
    # Sub-options (bold for selected, light colors)
    'root': 'fg:#ff6666 bold',     # Light Red
    'non-root': 'fg:#99ff99 bold', # Light Green
    'yes': 'fg:#ff6666 bold',      # Light Red
    'no': 'fg:#99ff99 bold',       # Light Green
    '1.0.0': 'fg:#66ffff bold',    # Light Cyan
    '2.0.0': 'fg:#ff99ff bold',    # Light Magenta
    'latest': 'fg:#cccccc bold',   # Light White
    'current-to-next-version': 'fg:#66ffff bold',      # Light Cyan
    'current-to-next-2-versions': 'fg:#ff99ff bold',   # Light Magenta
    'current-to-prev-version': 'fg:#66ffff bold',      # Light Cyan
    'current-to-prev-2-versions': 'fg:#ff99ff bold',   # Light Magenta
    # Sub-options (very light for unselected)
    'root-light': 'fg:#ff9999',     # Very Light Red
    'non-root-light': 'fg:#ccffcc', # Very Light Green
    'yes-light': 'fg:#ff9999',      # Very Light Red
    'no-light': 'fg:#ccffcc',       # Light Green
    '1.0.0-light': 'fg:#99ffff',    # Very Light Cyan
    '2.0.0-light': 'fg:#ffccff',    # Very Light Magenta
    'latest-light': 'fg:#e6e6e6',   # Very Light White
    'current-to-next-version-light': 'fg:#99ffff',      # Very Light Cyan
    'current-to-next-2-versions-light': 'fg:#ffccff',   # Very Light Magenta
    'current-to-prev-version-light': 'fg:#99ffff',      # Very Light Cyan
    'current-to-prev-2-versions-light': 'fg:#ffccff',   # Very Light Magenta
    # Other elements
    'dot-selected': 'fg:#00ff00',  # Green
    'dot-unselected': 'fg:#4444ff', # Blue
    'default': 'fg:#ffffff',       # White
})

# Color mapping for main options (for print, light colors)
MAIN_COLOR_MAP = {
    "Install": "#99ff99",    # Light Green
    "Uninstall": "#ff6666",  # Light Red
    "Upgrade": "#66ffff",    # Light Cyan
    "Downgrade": "#ff99ff",  # Light Magenta
    "Manage": "#cccccc",     # Light White
    "Start": "#9999ff",      # Light Bright Blue
    "Restart": "#ffff66",    # Light Yellow
    "Reinstall": "#66cccc",  # Light Bright Cyan
}

# Color mapping for sub-options (for print, light colors)
SUB_COLOR_MAP = {
    "Root": "#ff6666",       # Light Red
    "Non-root": "#99ff99",   # Light Green
    "Yes": "#ff6666",        # Light Red
    "No": "#99ff99",         # Light Green
    "1.0.0": "#66ffff",      # Light Cyan
    "2.0.0": "#ff99ff",      # Light Magenta
    "Latest": "#cccccc",     # Light White
    "4.0.0": "#66ffff",      # Light Cyan
    "5.0.0": "#ff99ff",   # Light Magenta
    "V2.0.0": "#66ffff",  # Light Cyan
    "V1.0.0": "#ff99ff" # Light Magenta
}

# Prompt session for text input
prompt_session = PromptSession(style=style)

def select_menu(prompt, options, color_map):
    """
    Display an interactive menu with a movable selection dot and colored options.
    Returns the selected option.
    """
    selected_index = 0
    max_index = len(options) - 1
    menu_height = len(options) + 2  # Prompt, options, and bottom line

    def get_menu_text():
        """Generate formatted text for the menu using prompt_toolkit styles."""
        option_style_map = {
            "Install": "install",
            "Uninstall": "uninstall",
            "Upgrade": "upgrade",
            "Downgrade": "downgrade",
            "Manage": "manage",
            "Start": "start",
            "Restart": "restart",
            "Reinstall": "reinstall",
            "Root": "root",
            "Non-root": "non-root",
            "Yes": "yes",
            "No": "no",
            "1.0.0": "1.0.0",
            "2.0.0": "2.0.0",
            "Latest": "latest",
            "4.0.0": "current-to-next-version",
            "5.0.0": "current-to-next-2-versions",
            "V2.0.0": "current-to-prev-version",
            "V1.0.0": "current-to-prev-2-versions",
        }
        option_light_style_map = {
            "Install": "install-light",
            "Uninstall": "uninstall-light",
            "Upgrade": "upgrade-light",
            "Downgrade": "downgrade-light",
            "Manage": "manage-light",
            "Start": "start-light",
            "Restart": "restart-light",
            "Reinstall": "reinstall-light",
            "Root": "root-light",
            "Non-root": "non-root-light",
            "Yes": "yes-light",
            "No": "no-light",
            "1.0.0": "1.0.0-light",
            "2.0.0": "2.0.0-light",
            "Latest": "latest-light",
            "4.0.0": "current-to-next-version-light",
            "5.0.0": "current-to-next-2-versions-light",
            "V2.0.0": "current-to-prev-version-light",
            "V1.0.0": "current-to-prev-2-versions-light",
        }
        lines = []
        # Prompt line
        lines.append(('class:prompttext', '◆  '))  # Sky blue dot
        lines.append(('class:promptname', f"{prompt}\n"))  # White header
        # Options with selection dots
        for i, option in enumerate(options):
            dot_style = 'dot-selected' if i == selected_index else 'dot-unselected'
            option_style = option_style_map.get(option, 'default') if i == selected_index else option_light_style_map.get(option, 'default')
            lines.append(('', '│  '))
            lines.append(('class:' + dot_style, '●' if i == selected_index else '○'))
            lines.append(('', ' '))
            lines.append(('class:' + option_style, option))
            lines.append(('', '\n'))
        # Bottom line
        lines.append(('class:prompttext', '└'))  # Sky blue dot
        return lines

    # Create a FormattedTextControl to display the menu
    control = FormattedTextControl(FormattedText(get_menu_text()))

    # Window to render the control
    window = Window(content=control)

    # Define key bindings
    kb = KeyBindings()

    @kb.add('up')
    def _(event):
        """Move selection up."""
        nonlocal selected_index
        if selected_index > 0:
            selected_index -= 1
            control.text = FormattedText(get_menu_text())  # Update display

    @kb.add('down')
    def _(event):
        """Move selection down."""
        nonlocal selected_index
        if selected_index < max_index:
            selected_index += 1
            control.text = FormattedText(get_menu_text())  # Update display

    @kb.add('enter')
    def _(event):
        """Confirm selection and exit."""
        event.app.exit(result=options[selected_index])

    @kb.add('c-c')  # Handle Ctrl+C
    def _(event):
        """Exit application on Ctrl+C."""
        event.app.exit(result=None)

    # Create and configure the application
    app = Application(
        layout=Layout(window),
        key_bindings=kb,
        full_screen=False,
        style=style  # Ensure style is applied
    )

    # Run the application and get the selected option
    selected = app.run()
    if selected is None:  # Handle cancellation (e.g., Ctrl+C)
        raise KeyboardInterrupt

    # Move cursor up to overwrite the menu and clear it
    sys.stdout.write(f"\033[{menu_height}A\033[J")
    sys.stdout.flush()

    # Print the selection using prompt_toolkit styles
    print_formatted_text(FormattedText([
        ('class:output-dot', '◇  '),
        ('class:output-header', f"{prompt}"),
        ('', '\n'),
        ('', '│  '),
        ('class:dot-selected', '●'),
        ('', ' '),
        (f'fg:{color_map.get(selected, "#ffffff")}', selected),
        ('', '\n'),
        ('', '│'),
        ('', '\n')
    ]), style=style, end='')
    sys.stdout.flush()
    return selected

def run_agent_management():
    """Run the agent management process with interactive menus."""
    # Step 1: Path
    print_formatted_text(FormattedText([('', '│'), ('', '\n')]), style=style, end='')
    sys.stdout.flush()
    install_path = prompt_session.prompt(
        [('class:prompttext', '◇  '), ('class:promptname', 'Path:\n'), ('class:default', '│  ')],
        default="./my-agent",
        style=style,
    ).strip()
    if not install_path:
        install_path = "./my-agent"
    print_formatted_text(FormattedText([('', '│'), ('', '\n')]), style=style, end='')
    sys.stdout.flush()

    # Step 2: Non-root user
    non_root_options = ["Yes", "No"]
    non_root_choice = select_menu("Non-root user:", non_root_options, SUB_COLOR_MAP)
    non_root_user = None
    if non_root_choice == "Yes":
        print_formatted_text(FormattedText([('', '│'), ('', '\n')]), style=style, end='')
        sys.stdout.flush()
        non_root_user = prompt_session.prompt(
            [('class:prompttext', '◇  '), ('class:promptname', 'Non-root user name:\n'), ('class:default', '│  ')],
            default="user",
            style=style,
        ).strip()
        if not non_root_user:
            non_root_user = "user"
        print_formatted_text(FormattedText([('', '│'), ('', '\n')]), style=style, end='')
        sys.stdout.flush()

    # Step 3: Action selection
    main_options = ["Install", "Uninstall", "Upgrade", "Downgrade", "Manage", "Start", "Restart", "Reinstall"]
    action = select_menu("Select action:", main_options, MAIN_COLOR_MAP)

    # Step 4: Handle selected action
    if action in ["Install", "Reinstall"]:
        user_type_options = ["Root", "Non-root"]
        user_type = select_menu("Select user type:", user_type_options, SUB_COLOR_MAP)
        # Ask for non-root user name only if "Non-root" is selected and not already provided
        if user_type == "Non-root" and non_root_user is None:
            print_formatted_text(FormattedText([('', '│'), ('', '\n')]), style=style, end='')
            sys.stdout.flush()
            non_root_user = prompt_session.prompt(
                [('class:prompttext', '◇  '), ('class:promptname', 'Non-root user name:\n'), ('class:default', '│  ')],
                default="user",
                style=style,
            ).strip()
            if not non_root_user:
                non_root_user = "user"
            print_formatted_text(FormattedText([('', '│'), ('', '\n')]), style=style, end='')
            sys.stdout.flush()
        version_options = ["1.0.0", "2.0.0", "Latest"]
        version = select_menu("Select version:", version_options, SUB_COLOR_MAP)
        user_info = f" as {user_type}" + (f" (user: {non_root_user})" if user_type == "Non-root" else "")
        print_formatted_text(FormattedText([
            (f'fg:{MAIN_COLOR_MAP[action]}', f"│  {action}ing to {install_path}{user_info} with version {version}..."),
            ('', '\n')
        ]), style=style, end='')
        sys.stdout.flush()

    elif action == "Uninstall":
        confirm_options = ["Yes", "No"]
        confirm = select_menu("Confirm uninstallation:", confirm_options, SUB_COLOR_MAP)
        if confirm == "Yes":
            print_formatted_text(FormattedText([
                (f'fg:{MAIN_COLOR_MAP[action]}', f"│  Uninstalling from {install_path} and deleting all files..."),
                ('', '\n')
            ]), style=style, end='')
            sys.stdout.flush()
        else:
            print_formatted_text(FormattedText([
                (f'fg:{MAIN_COLOR_MAP[action]}', f"│  Uninstallation cancelled."),
                ('', '\n')
            ]), style=style, end='')
            sys.stdout.flush()

    elif action in ["Upgrade", "Downgrade"]:
        if action == "Upgrade":
            options = ["4.0.0", "5.0.0"]
        else:
            options = ["V2.0.0", "V1.0.0"]
        choice = select_menu(f"Select {action.lower()} option:", options, SUB_COLOR_MAP)
        print_formatted_text(FormattedText([
            (f'fg:{MAIN_COLOR_MAP[action]}', f"│  {action}ing {install_path} to {choice}..."),
            ('', '\n')
        ]), style=style, end='')
        sys.stdout.flush()

    elif action == "Manage":
        print_formatted_text(FormattedText([
            (f'fg:{MAIN_COLOR_MAP[action]}', f"│  Managing agent at {install_path}... (feature not implemented)"),
            ('', '\n')
        ]), style=style, end='')
        sys.stdout.flush()

    elif action in ["Start", "Restart"]:
        print_formatted_text(FormattedText([
            (f'fg:{MAIN_COLOR_MAP[action]}', f"│  {action}ing agent at {install_path}..."),
            ('', '\n')
        ]), style=style, end='')
        sys.stdout.flush()

    # Final "Done" with line break and larger ┗
    print_formatted_text(FormattedText([
        ('', '\n'),
        ('class:output-dot', '┗  '),
        ('class:output-done', 'Done.'),
        ('', '\n')
    ]), style=style, end='')
    sys.stdout.flush()

def main():
    """Main entry point with exception handling."""
    try:
        run_agent_management()
    except KeyboardInterrupt:
        print_formatted_text(FormattedText([
            ('', '\n'),
            ('class:output-dot', '┗  '),
            ('class:output-done', 'Cancelled'),
            ('', '\n')
        ]), style=style, end='')
        sys.stdout.flush()
        sys.exit(1)
    except EOFError:
        print_formatted_text(FormattedText([
            ('', '\n'),
            ('class:output-dot', '┗  '),
            ('class:output-done', 'Exited'),
            ('', '\n')
        ]), style=style, end='')
        sys.stdout.flush()
        sys.exit(0)

if __name__ == "__main__":
    main()
