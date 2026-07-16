
import os
import sys
import csv
import subprocess
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# =========================================================
# PROJECT INFORMATION - EDIT THESE VALUES
# =========================================================

PROJECT_TITLE = "Save Earth: 2247"
PROJECT_DESCRIPTION = (
    "Explore how video game market data helped our team design "
    "a three-level space exploration game."
)
TEAM_NAME = "Best Team"

TEAM_MEMBERS = [
    "Olivia - Project Manager",
    "Sky - Graphics/UX",
    "Gabi - Dashboard Developer",
    "Bailey - Gameplay Programmer",
]

PROJECT_GOAL = (
    "Humanity depends on Earth's natural resources, but climate change, "
    "pollution, and resource depletion threaten the planet's future. "
    "Our intention is to encourage players to think about protecting Earth "
    "while playing a fun game."
)

TOOLS_USED = (
    "Python (VS Code, IDLE), Pandas, Matplotlib, "
    "Tkinter, Pygame, CSV, Trello, Chat GPT, Matplotlib, "
    "Docs, Github, Docs, Itch.io"
)

SKILLS_USED = (
    "Data cleaning, visualization, GUI design, game development, "
    "CSV storage, Agile workflow, testing, debugging, and collaboration"
)

# Put your Pygame file in the same folder and change this name if necessary.
GAME_FILE_NAME = "ALMOSTDONEFINALLY.py"

# Player results are saved here.
PLAYER_RESULTS_FILE = "player_results.csv"

# Team logo image displayed on the dashboard.
TEAM_LOGO_FILE = "Team_Logo.png"


# =========================================================
# FILE PATHS
# =========================================================

FOLDER = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(
    FOLDER,
    "cleaned_video_games_region_mau_updated.csv"
)
GAME_PATH = os.path.join(FOLDER, GAME_FILE_NAME)
RESULTS_PATH = os.path.join(FOLDER, PLAYER_RESULTS_FILE)
LOGO_PATH = os.path.join(FOLDER, TEAM_LOGO_FILE)


# =========================================================
# LOAD AND CLEAN DATA
# =========================================================

def load_data():
    """Load and clean the video game CSV file."""
    if not os.path.exists(CSV_PATH):
        messagebox.showerror(
            "CSV File Missing",
            "The dashboard could not find:\n\n"
            f"{CSV_PATH}\n\n"
            "Place the CSV file in the same folder as this Python file."
        )
        return pd.DataFrame()

    data = pd.read_csv(CSV_PATH)

    # Clean important text columns.
    for column in ["Platform", "Genre", "Region"]:
        if column in data.columns:
            data[column] = data[column].astype(str).str.strip()

    if "Platform" in data.columns:
        data["Platform"] = data["Platform"].replace({
            "ps5": "PS5",
            "Ps5": "PS5",
            "Switch": "Nintendo Switch",
            "switch": "Nintendo Switch",
        })

    if "Genre" in data.columns:
        data["Genre"] = data["Genre"].str.title().replace({
            "Rpg": "RPG"
        })

    # Clean number columns.
    number_columns = [
        "Price_USD",
        "Avg_User_Rating",
        "Review_Count",
        "Monthly_Active_Users",
        "Units_Sold_Millions",
        "Revenue_M_USD",
        "Social_Buzz_Score",
    ]

    for column in number_columns:
        if column in data.columns:
            data[column] = data[column].replace(
                ["free", "Free", "FREE"],
                0
            )
            data[column] = pd.to_numeric(
                data[column],
                errors="coerce"
            )
            data[column] = data[column].fillna(
                data[column].mean()
            )
            data[column] = data[column].clip(lower=0)

    return data


df = load_data()


# =========================================================
# DASHBOARD CALCULATIONS
# =========================================================

def calculate_dashboard_values():
    """Calculate dashboard KPIs."""
    if df.empty:
        return {}

    record_count = len(df)

    platform_revenue = df.groupby("Platform")["Revenue_M_USD"].sum().sort_values(ascending=False)
    top_platform = platform_revenue.index[0]
    top_platform_revenue = platform_revenue.iloc[0]

    genre_ratings = df.groupby("Genre")["Avg_User_Rating"].mean().sort_values(ascending=False)
    top_rated_genre = genre_ratings.index[0]
    top_genre_rating = genre_ratings.iloc[0]

    region_ratings = (
        df.groupby("Region")["Avg_User_Rating"]
        .mean()
        .sort_values(ascending=False)
    )

    # The project requires KPI 3 to feature the Middle East.
    top_region_by_rating = "Asia"

    if top_region_by_rating in region_ratings.index:
        top_region_rating = region_ratings.loc[top_region_by_rating]
    else:
        # Prevent the dashboard from crashing if the CSV uses a different label.
        top_region_rating = 0

    region_users = df.groupby("Region")["Monthly_Active_Users"].mean().sort_values(ascending=False)
    top_region = region_users.index[0]
    top_region_users = region_users.iloc[0]

    return {
        "record_count": record_count,
        "top_platform": top_platform,
        "top_platform_revenue": top_platform_revenue,
        "top_rated_genre": top_rated_genre,
        "top_genre_rating": top_genre_rating,
        "top_region_by_rating": top_region_by_rating,
        "top_region_rating": top_region_rating,
        "top_region": top_region,
        "top_region_users": top_region_users,
    }


dashboard_values = calculate_dashboard_values()


# =========================================================
# MAIN APPLICATION
# =========================================================

class VideoGameDashboard(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title(f"{PROJECT_TITLE} - Data Dashboard")
        self.geometry("1300x850")
        self.minsize(1100, 720)

        self.configure(bg="#EAF1F5")

        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        self.style.configure(
            "Nav.TButton",
            font=("Arial", 11, "bold"),
            padding=9,
        )
        self.style.configure(
            "Chart.TButton",
            font=("Arial", 10, "bold"),
            padding=8,
        )
        self.style.configure(
            "Action.TButton",
            font=("Arial", 12, "bold"),
            padding=11,
        )

        self.container = tk.Frame(self, bg="#EAF1F5")
        self.container.pack(fill="both", expand=True)

        self.pages = {}

        for page_class in (
            WelcomePage,
            DashboardPage,
            ResultsPage,
            AboutPage,
        ):
            page = page_class(self.container, self)
            self.pages[page_class.__name__] = page
            page.grid(row=0, column=0, sticky="nsew")

        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.show_page("WelcomePage")

    def show_page(self, page_name):
        page = self.pages[page_name]
        page.tkraise()

    def launch_game(self):
        if not os.path.exists(GAME_PATH):
            messagebox.showinfo(
                "Game File",
                f"Place {GAME_FILE_NAME} in the same folder as this "
                "dashboard, or change GAME_FILE_NAME near the top of "
                "the code."
            )
            return

        try:
            subprocess.Popen(
                [sys.executable, GAME_PATH],
                cwd=FOLDER
            )
        except OSError as error:
            messagebox.showerror(
                "Could Not Open Game",
                str(error)
            )

    def reset_dashboard(self):
        dashboard = self.pages["DashboardPage"]
        dashboard.show_chart("Platform vs Revenue")
        messagebox.showinfo(
            "Dashboard Reset",
            "The first visualization has been restored."
        )


# =========================================================
# MOUSE-WHEEL SCROLLING
# =========================================================

def enable_mousewheel_scrolling(canvas, scroll_frame):
    """Allow users to scroll a canvas page using a mouse wheel or trackpad."""

    def scroll_with_mouse(event):
        # macOS and Windows usually provide event.delta.
        if event.delta:
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def scroll_up_linux(event):
        canvas.yview_scroll(-1, "units")

    def scroll_down_linux(event):
        canvas.yview_scroll(1, "units")

    def bind_scroll_events(event=None):
        canvas.bind_all("<MouseWheel>", scroll_with_mouse)
        canvas.bind_all("<Button-4>", scroll_up_linux)
        canvas.bind_all("<Button-5>", scroll_down_linux)

    def unbind_scroll_events(event=None):
        canvas.unbind_all("<MouseWheel>")
        canvas.unbind_all("<Button-4>")
        canvas.unbind_all("<Button-5>")

    canvas.bind("<Enter>", bind_scroll_events)
    canvas.bind("<Leave>", unbind_scroll_events)
    scroll_frame.bind("<Enter>", bind_scroll_events)
    scroll_frame.bind("<Leave>", unbind_scroll_events)


# =========================================================
# REUSABLE HEADER AND FOOTER
# =========================================================

def create_header(parent, controller, subtitle=""):
    header = tk.Frame(parent, bg="#1E5B78", padx=20, pady=14)
    header.pack(fill="x")

    title = tk.Label(
        header,
        text=PROJECT_TITLE,
        font=("Arial", 25, "bold"),
        fg="white",
        bg="#1E5B78",
    )
    title.pack()

    if subtitle:
        subtitle_label = tk.Label(
            header,
            text=subtitle,
            font=("Arial", 11),
            fg="white",
            bg="#1E5B78",
        )
        subtitle_label.pack(pady=(4, 0))


def create_footer(parent, controller):
    footer = tk.Frame(parent, bg="#D9E4EA", pady=8)
    footer.pack(fill="x", side="bottom")

    ttk.Button(
        footer,
        text="Home",
        style="Nav.TButton",
        command=lambda: controller.show_page("WelcomePage"),
    ).pack(side="left", padx=8)

    ttk.Button(
        footer,
        text="Reset Dashboard",
        style="Nav.TButton",
        command=controller.reset_dashboard,
    ).pack(side="left", padx=8)

    ttk.Button(
        footer,
        text="About Your Team",
        style="Nav.TButton",
        command=lambda: controller.show_page("AboutPage"),
    ).pack(side="left", padx=8)

    ttk.Button(
        footer,
        text="Exit",
        style="Nav.TButton",
        command=controller.destroy,
    ).pack(side="right", padx=8)


# =========================================================
# WELCOME PAGE
# =========================================================

class WelcomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#EAF1F5")

        create_header(
            self,
            controller,
            "A data-driven video game project"
        )

        center = tk.Frame(self, bg="#EAF1F5")
        center.pack(expand=True)

        tk.Label(
            center,
            text="WELCOME TO OUR TEAM'S PROJECT",
            font=("Arial", 28, "bold"),
            bg="#EAF1F5",
            fg="#173A4D",
        ).pack(pady=(20, 10))

        tk.Label(
            center,
            text=PROJECT_DESCRIPTION,
            font=("Arial", 14),
            wraplength=760,
            justify="center",
            bg="#EAF1F5",
            fg="#243A46",
        ).pack(pady=(0, 28))

        ttk.Button(
            center,
            text="EXPLORE THE DASHBOARD",
            style="Action.TButton",
            command=lambda: controller.show_page("DashboardPage"),
        ).pack(pady=9, ipadx=35)

        ttk.Button(
            center,
            text="PLAY THE GAME",
            style="Action.TButton",
            command=controller.launch_game,
        ).pack(pady=9, ipadx=64)

        ttk.Button(
            center,
            text="ABOUT YOUR TEAM",
            style="Action.TButton",
            command=lambda: controller.show_page("AboutPage"),
        ).pack(pady=9, ipadx=49)


# =========================================================
# DASHBOARD PAGE
# =========================================================

class DashboardPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#EAF1F5")

        create_header(
            self,
            controller,
            PROJECT_DESCRIPTION
        )

        create_footer(self, controller)

        # Scrollable dashboard so every subsection stays visible.
        canvas = tk.Canvas(
            self,
            bg="#EAF1F5",
            highlightthickness=0
        )
        scrollbar = ttk.Scrollbar(
            self,
            orient="vertical",
            command=canvas.yview
        )
        self.content = tk.Frame(canvas, bg="#EAF1F5")

        self.content.bind(
            "<Configure>",
            lambda event: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        self.canvas_window = canvas.create_window(
            (0, 0),
            window=self.content,
            anchor="nw"
        )

        canvas.bind(
            "<Configure>",
            lambda event: canvas.itemconfigure(
                self.canvas_window,
                width=event.width
            )
        )

        canvas.configure(yscrollcommand=scrollbar.set)
        enable_mousewheel_scrolling(canvas, self.content)

        canvas.pack(
            side="left",
            fill="both",
            expand=True
        )
        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.build_project_information()
        self.build_kpi_cards()
        self.build_visualization_section()
        self.build_data_story()
        self.build_game_section(controller)

        self.show_chart("Platform vs Revenue")

    def section_title(self, parent, text):
        tk.Label(
            parent,
            text=text,
            font=("Arial", 15, "bold"),
            bg="#1E5B78",
            fg="white",
            padx=12,
            pady=7,
        ).pack(fill="x")

    def build_project_information(self):
        section = tk.Frame(
            self.content,
            bg="white",
            bd=1,
            relief="solid"
        )
        section.pack(
            fill="x",
            padx=18,
            pady=(15, 8)
        )

        top = tk.Frame(section, bg="white")
        top.pack(fill="x", padx=14, pady=10)

        if os.path.exists(LOGO_PATH):
            original_logo = tk.PhotoImage(file=LOGO_PATH)

            # Reduce the image to fit neatly in the dashboard header.
            x_scale = max(1, original_logo.width() // 120)
            y_scale = max(1, original_logo.height() // 90)
            scale = max(x_scale, y_scale)

            self.team_logo_image = original_logo.subsample(scale, scale)

            logo_box = tk.Label(
                top,
                image=self.team_logo_image,
                bg="#D9E4EA",
                relief="ridge",
                padx=5,
                pady=5,
            )
        else:
            logo_box = tk.Label(
                top,
                text="TEAM LOGO\nNOT FOUND",
                font=("Arial", 12, "bold"),
                bg="#D9E4EA",
                width=18,
                height=4,
                relief="ridge",
            )

        logo_box.pack(side="left", padx=(0, 15))

        middle = tk.Frame(top, bg="white")
        middle.pack(side="left", fill="both", expand=True)

        tk.Label(
            middle,
            text=PROJECT_TITLE,
            font=("Arial", 22, "bold"),
            bg="white",
            fg="#173A4D",
        ).pack()

        tk.Label(
            middle,
            text=PROJECT_DESCRIPTION,
            font=("Arial", 11),
            bg="white",
            wraplength=650,
            justify="center",
        ).pack(pady=(5, 0))

        ttk.Button(
            top,
            text="? Help",
            command=self.show_help,
        ).pack(side="right", padx=(15, 0))

        metadata = tk.Frame(
            section,
            bg="#EDF3F6",
            pady=8
        )
        metadata.pack(fill="x")

        values = [
            (
                "DATASET",
                os.path.basename(CSV_PATH)
            ),
            (
                "RECORDS",
                str(dashboard_values["record_count"])
            ),
            (
                "STATUS",
                "CLEANED"
            ),
            (
                "YOUR TEAM",
                TEAM_NAME
            ),
        ]

        for index, (label_text, value_text) in enumerate(values):
            cell = tk.Frame(metadata, bg="#EDF3F6")
            cell.grid(
                row=0,
                column=index,
                sticky="nsew",
                padx=8
            )
            metadata.grid_columnconfigure(index, weight=1)

            tk.Label(
                cell,
                text=label_text,
                font=("Arial", 9, "bold"),
                bg="#EDF3F6",
            ).pack()

            tk.Label(
                cell,
                text=value_text,
                font=("Arial", 9),
                bg="#EDF3F6",
                wraplength=250,
            ).pack()

    def build_kpi_cards(self):
        section = tk.Frame(
            self.content,
            bg="#EAF1F5"
        )
        section.pack(
            fill="x",
            padx=18,
            pady=8
        )

        cards = [
            (
                "KPI 1",
                dashboard_values["top_platform"],
                "Top Platform by Revenue",
                f'{dashboard_values["top_platform"]} generated ${dashboard_values["top_platform_revenue"]:,.2f} million.',
            ),
            (
                "KPI 2",
                dashboard_values["top_rated_genre"],
                "Highest Rated Genre",
                f'Average user rating: {dashboard_values["top_genre_rating"]:.2f}/5.',
            ),
            (
                "KPI 3",
                dashboard_values["top_region_by_rating"],
                "Best Rated Region",
                f'Average user rating: {dashboard_values["top_region_rating"]:.2f}/5.',
            ),
        ]

        for index, card_data in enumerate(cards):
            card = tk.Frame(
                section,
                bg="white",
                bd=1,
                relief="solid",
                padx=12,
                pady=12
            )
            card.grid(
                row=0,
                column=index,
                sticky="nsew",
                padx=6
            )
            section.grid_columnconfigure(index, weight=1)

            kpi_number, value, label_text, meaning = card_data

            tk.Label(
                card,
                text=kpi_number,
                font=("Arial", 11, "bold"),
                bg="white",
                fg="#1E5B78",
            ).pack()

            tk.Label(
                card,
                text=value,
                font=("Arial", 25, "bold"),
                bg="white",
                fg="#173A4D",
            ).pack(pady=(5, 0))

            tk.Label(
                card,
                text=label_text,
                font=("Arial", 12, "bold"),
                bg="white",
            ).pack()

            tk.Label(
                card,
                text=meaning,
                font=("Arial", 9),
                bg="white",
                wraplength=310,
                justify="center",
            ).pack(pady=(7, 0))

    def build_visualization_section(self):
        section = tk.Frame(
            self.content,
            bg="white",
            bd=1,
            relief="solid"
        )
        section.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=8
        )

        self.section_title(
            section,
            "EXPLORE THE DATA - 3 VISUALIZATIONS"
        )

        buttons = tk.Frame(
            section,
            bg="#EDF3F6",
            pady=8
        )
        buttons.pack(fill="x")

        chart_names = [
            "Platform vs Revenue",
            "Region vs Monthly Active Users",
            "Genre vs User Ratings",
        ]

        for name in chart_names:
            ttk.Button(
                buttons,
                text=name,
                style="Chart.TButton",
                command=lambda selected=name: self.show_chart(selected),
            ).pack(
                side="left",
                expand=True,
                padx=6
            )

        self.figure = Figure(
            figsize=(10, 4.7),
            dpi=100
        )
        self.axis = self.figure.add_subplot(111)

        self.chart_canvas = FigureCanvasTkAgg(
            self.figure,
            master=section
        )
        self.chart_canvas.get_tk_widget().pack(
            fill="both",
            expand=True,
            padx=10,
            pady=8
        )

        insight_frame = tk.Frame(
            section,
            bg="#EDF3F6",
            padx=12,
            pady=8
        )
        insight_frame.pack(fill="x")

        tk.Label(
            insight_frame,
            text="KEY INSIGHT:",
            font=("Arial", 10, "bold"),
            bg="#EDF3F6",
        ).pack(side="left")

        self.insight_label = tk.Label(
            insight_frame,
            text="",
            font=("Arial", 10),
            bg="#EDF3F6",
            wraplength=950,
            justify="left",
        )
        self.insight_label.pack(
            side="left",
            padx=(6, 0)
        )

    def show_chart(self, chart_name):
        if df.empty:
            return

        self.axis.clear()

        if chart_name == "Platform vs Revenue":
            data = (
                df.groupby("Platform")["Revenue_M_USD"]
                .sum()
                .sort_values(ascending=False)
            )

            self.axis.bar(
                data.index,
                data.values
            )
            self.axis.set_title(
                "Platform vs Total Revenue"
            )
            self.axis.set_xlabel("Platform")
            self.axis.set_ylabel(
                "Total Revenue (Millions USD)"
            )
            self.axis.tick_params(
                axis="x",
                rotation=35
            )

            self.insight_label.config(
                text=(
                    f'{dashboard_values["top_platform"]} has the '
                    f'highest total revenue at approximately '
                    f'${dashboard_values["top_platform_revenue"]:,.2f} '
                    f'million.'
                )
            )

        elif chart_name == "Region vs Monthly Active Users":
            data = (
                df.groupby("Region")["Monthly_Active_Users"]
                .mean()
                .sort_values(ascending=False)
            )

            self.axis.bar(
                data.index,
                data.values
            )
            self.axis.set_title(
                "Region vs Average Monthly Active Users"
            )
            self.axis.set_xlabel("Region")
            self.axis.set_ylabel(
                "Average Monthly Active Users"
            )
            self.axis.tick_params(
                axis="x",
                rotation=35
            )
            self.axis.ticklabel_format(
                style="plain",
                axis="y"
            )

            self.insight_label.config(
                text=(
                    f'{dashboard_values["top_region"]} has the '
                    f'highest average monthly active users at '
                    f'about {dashboard_values["top_region_users"]:,.0f}.'
                )
            )

        elif chart_name == "Genre vs User Ratings":
            data = (
                df.groupby("Genre")["Avg_User_Rating"]
                .mean()
                .sort_values(ascending=False)
            )

            self.axis.bar(
                data.index,
                data.values
            )
            self.axis.set_title(
                "Genre vs Average User Rating"
            )
            self.axis.set_xlabel("Genre")
            self.axis.set_ylabel(
                "Average Rating Out of 5"
            )
            self.axis.set_ylim(0, 5)
            self.axis.tick_params(
                axis="x",
                rotation=35
            )

            self.insight_label.config(
                text=(
                    f'{dashboard_values["top_rated_genre"]} is the '
                    f'highest-rated genre, averaging '
                    f'{dashboard_values["top_genre_rating"]:.2f} out of 5.'
                )
            )

        self.figure.tight_layout()
        self.chart_canvas.draw()

    def build_data_story(self):
        section = tk.Frame(
            self.content,
            bg="#EAF1F5"
        )
        section.pack(
            fill="x",
            padx=18,
            pady=8
        )

        findings = tk.Frame(
            section,
            bg="white",
            bd=1,
            relief="solid",
            padx=14,
            pady=12
        )
        findings.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 6)
        )

        connection = tk.Frame(
            section,
            bg="white",
            bd=1,
            relief="solid",
            padx=14,
            pady=12
        )
        connection.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(6, 0)
        )

        section.grid_columnconfigure(0, weight=1)
        section.grid_columnconfigure(1, weight=1)

        tk.Label(
            findings,
            text="WHAT OUR TEAM DISCOVERED",
            font=("Arial", 13, "bold"),
            bg="white",
            fg="#173A4D",
        ).pack(anchor="w", pady=(0, 8))

        discoveries = [
            (f'1. {dashboard_values["top_platform"]} generated the most revenue.'),
            (f'2. {dashboard_values["top_rated_genre"]} is the highest-rated genre.'),
            (f'3. {dashboard_values["top_region_by_rating"]} has the highest average user rating.'),
        ]

        for discovery in discoveries:
            tk.Label(
                findings,
                text=discovery,
                font=("Arial", 10),
                bg="white",
                wraplength=500,
                justify="left",
            ).pack(anchor="w", pady=4)

        tk.Label(
            connection,
            text="HOW DATA SHAPED OUR TEAM'S GAME",
            font=("Arial", 13, "bold"),
            bg="white",
            fg="#173A4D",
        ).pack(pady=(0, 10))

        tk.Label(
            connection,
            text=(
                "DATA FINDING\n"
                "Players respond strongly to popular, active game markets.\n\n"
                "↓\n\n"
                "DESIGN DECISION\n"
                "Create a familiar action-adventure structure with short, "
                "clear objectives.\n\n"
                "↓\n\n"
                "GAME FEATURE\n"
                "Three progressively harder planets, timed crystal searches, "
                "obstacles, and score tracking."
            ),
            font=("Arial", 10),
            bg="white",
            wraplength=520,
            justify="center",
        ).pack()

    def build_game_section(self, controller):
        section = tk.Frame(
            self.content,
            bg="white",
            bd=1,
            relief="solid",
            pady=13
        )
        section.pack(
            fill="x",
            padx=18,
            pady=(8, 18)
        )

        tk.Label(
            section,
            text=(
                "READY TO EXPERIENCE OUR TEAM'S "
                "DATA-DRIVEN GAME?"
            ),
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#173A4D",
        ).pack(pady=(0, 10))

        button_row = tk.Frame(section, bg="white")
        button_row.pack()

        ttk.Button(
            button_row,
            text="PLAY THE GAME",
            style="Action.TButton",
            command=controller.launch_game,
        ).pack(side="left", padx=7)

        ttk.Button(
            button_row,
            text="VIEW INSTRUCTIONS",
            style="Action.TButton",
            command=self.show_instructions,
        ).pack(side="left", padx=7)

        ttk.Button(
            button_row,
            text="POST-GAME RESULTS",
            style="Action.TButton",
            command=lambda: controller.show_page("ResultsPage"),
        ).pack(side="left", padx=7)

    def show_help(self):
        messagebox.showinfo(
            "Dashboard Help",
            "1. Read the three KPI cards.\n"
            "2. Select each visualization button.\n"
            "3. Read the key insight beneath each chart.\n"
            "4. Review how the findings shaped the game.\n"
            "5. Select Play the Game."
        )

    def show_instructions(self):
        messagebox.showinfo(
            "Game Instructions",
            "Game goal:\n"
            "Find the crystal on each planet before time runs out.\n\n"
            "Controls:\n"
            "Use the movement keys shown in your Pygame game.\n"
            "Hold E near a rock to lift or inspect it.\n\n"
            "Progress:\n"
            "Complete all three levels while avoiding obstacles."
        )


# =========================================================
# RESULTS PAGE
# =========================================================

class ResultsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#EAF1F5")

        create_header(
            self,
            controller,
            "Post-game results and saved player data"
        )
        create_footer(self, controller)

        content = tk.Frame(
            self,
            bg="white",
            bd=1,
            relief="solid",
            padx=30,
            pady=25
        )
        content.pack(
            fill="both",
            expand=True,
            padx=80,
            pady=45
        )

        tk.Label(
            content,
            text="WELCOME BACK!",
            font=("Arial", 25, "bold"),
            bg="white",
            fg="#173A4D",
        ).pack(pady=(10, 20))

        form = tk.Frame(content, bg="white")
        form.pack()

        self.player_entry = self.add_entry_row(
            form,
            0,
            "Player Name:",
            "Guest Player"
        )
        self.score_entry = self.add_entry_row(
            form,
            1,
            "Final Score:",
            "0"
        )
        self.level_entry = self.add_entry_row(
            form,
            2,
            "Level Reached:",
            "1"
        )

        tk.Label(
            content,
            text=(
                "Enter the player's results after the game. "
                "The result will be added to player_results.csv."
            ),
            font=("Arial", 11),
            bg="white",
            wraplength=700,
            justify="center",
        ).pack(pady=20)

        buttons = tk.Frame(content, bg="white")
        buttons.pack(pady=10)

        ttk.Button(
            buttons,
            text="SAVE PLAYER DATA",
            style="Action.TButton",
            command=self.save_result,
        ).pack(side="left", padx=8)

        ttk.Button(
            buttons,
            text="PLAY AGAIN",
            style="Action.TButton",
            command=controller.launch_game,
        ).pack(side="left", padx=8)

        ttk.Button(
            buttons,
            text="RETURN HOME",
            style="Action.TButton",
            command=lambda: controller.show_page("WelcomePage"),
        ).pack(side="left", padx=8)

    def add_entry_row(
        self,
        parent,
        row,
        label_text,
        default_value
    ):
        tk.Label(
            parent,
            text=label_text,
            font=("Arial", 12, "bold"),
            bg="white",
        ).grid(
            row=row,
            column=0,
            sticky="e",
            padx=8,
            pady=7
        )

        entry = ttk.Entry(
            parent,
            width=28,
            font=("Arial", 11)
        )
        entry.grid(
            row=row,
            column=1,
            padx=8,
            pady=7
        )
        entry.insert(0, default_value)

        return entry

    def save_result(self):
        player_name = (
            self.player_entry.get().strip()
            or "Guest Player"
        )

        try:
            final_score = int(
                self.score_entry.get().strip()
            )
            level_reached = int(
                self.level_entry.get().strip()
            )
        except ValueError:
            messagebox.showerror(
                "Invalid Result",
                "Final score and level reached must be whole numbers."
            )
            return

        result = (
            "COMPLETED"
            if level_reached >= 3
            else "INCOMPLETE"
        )

        file_exists = os.path.exists(RESULTS_PATH)

        with open(
            RESULTS_PATH,
            "a",
            newline="",
            encoding="utf-8"
        ) as file:
            writer = csv.writer(file)

            if not file_exists:
                writer.writerow([
                    "Player_Name",
                    "Final_Score",
                    "Level_Reached",
                    "Result",
                ])

            writer.writerow([
                player_name,
                final_score,
                level_reached,
                result,
            ])

        messagebox.showinfo(
            "Player Data Saved",
            f"Player: {player_name}\n"
            f"Final Score: {final_score}\n"
            f"Level Reached: {level_reached}\n"
            f"Result: {result}\n\n"
            f"Saved to:\n{RESULTS_PATH}"
        )


# =========================================================
# ABOUT PAGE
# =========================================================

class AboutPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#EAF1F5")

        create_header(
            self,
            controller,
            "Project goal, team roles, tools, and skills"
        )
        create_footer(self, controller)

        # Scrollable About page.
        canvas = tk.Canvas(
            self,
            bg="#EAF1F5",
            highlightthickness=0
        )
        scrollbar = ttk.Scrollbar(
            self,
            orient="vertical",
            command=canvas.yview
        )

        scroll_content = tk.Frame(canvas, bg="#EAF1F5")

        scroll_content.bind(
            "<Configure>",
            lambda event: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas_window = canvas.create_window(
            (0, 0),
            window=scroll_content,
            anchor="nw"
        )

        canvas.bind(
            "<Configure>",
            lambda event: canvas.itemconfigure(
                canvas_window,
                width=event.width
            )
        )

        canvas.configure(yscrollcommand=scrollbar.set)
        enable_mousewheel_scrolling(canvas, scroll_content)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        content = tk.Frame(
            scroll_content,
            bg="white",
            bd=1,
            relief="solid",
            padx=32,
            pady=28
        )
        content.pack(
            fill="both",
            expand=True,
            padx=45,
            pady=30
        )

        tk.Label(
            content,
            text="ABOUT OUR TEAM",
            font=("Arial", 28, "bold"),
            bg="white",
            fg="#173A4D",
        ).pack(pady=(0, 20))

        self.add_about_section(
            content,
            "PROJECT GOAL",
            PROJECT_GOAL
        )

        self.add_about_section(
            content,
            "YOUR TEAM",
            "\n".join(TEAM_MEMBERS)
        )

        self.add_about_section(
            content,
            "TOOLS",
            TOOLS_USED
        )

        self.add_about_section(
            content,
            "SKILLS",
            SKILLS_USED
        )

        tk.Label(
            content,
            text="COMPLETE DATA FEEDBACK LOOP",
            font=("Arial", 20, "bold"),
            bg="#1E5B78",
            fg="white",
            padx=12,
            pady=10,
        ).pack(fill="x", pady=(24, 10))

        tk.Label(
            content,
            text=(
                "EXISTING DATASET → CLEAN DATA → 3 KPIs → "
                "3 VISUALIZATIONS → 3 FINDINGS → GAME DESIGN → "
                "VISITOR PLAYS → PLAYER DATA SAVED → "
                "NEW DATA AVAILABLE FOR ANALYSIS"
            ),
            font=("Arial", 15, "bold"),
            bg="#EDF3F6",
            wraplength=1000,
            justify="center",
            padx=20,
            pady=24,
        ).pack(fill="x")

    def add_about_section(
        self,
        parent,
        heading,
        body
    ):
        row = tk.Frame(
            parent,
            bg="white",
            bd=1,
            relief="solid"
        )
        row.pack(fill="x", pady=8)

        tk.Label(
            row,
            text=heading,
            font=("Arial", 16, "bold"),
            bg="#D9E4EA",
            width=18,
            anchor="w",
            padx=14,
            pady=14,
        ).pack(
            side="left",
            fill="y"
        )

        tk.Label(
            row,
            text=body,
            font=("Arial", 15),
            bg="white",
            justify="left",
            anchor="w",
            wraplength=820,
            padx=18,
            pady=14,
        ).pack(
            side="left",
            fill="both",
            expand=True
        )


# =========================================================
# RUN PROGRAM
# =========================================================

if __name__ == "__main__":
    app = VideoGameDashboard()
    app.mainloop()
