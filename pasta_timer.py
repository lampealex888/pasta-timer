import time
import os
import random
try:
    from playsound3 import playsound
    SOUND_AVAILABLE = True
except ImportError:
    SOUND_AVAILABLE = False

# Debug mode: set to True to make all timers last only 6 seconds
DEBUG_MODE = False  # Change to True for testing

# Dictionary with pasta types and cooking time ranges (in minutes)
pasta_times = {
    "spaghetti": (8, 10),
    "penne": (11, 13),
    "fusilli": (9, 11),
    "rigatoni": (12, 14),
    "linguine": (8, 10),
    "farfalle": (10, 12),
    "angel hair": (3, 5),
    "fettuccine": (9, 11)
}

# List of fun pasta facts or tips
fun_facts = [
    "Did you know? The word 'pasta' comes from the Italian word for 'paste.'",
    "Tip: Always salt your pasta water for better flavor!",
    "Fact: There are over 600 shapes of pasta worldwide.",
    "Tip: Don't rinse your pasta after cooking; the starch helps sauce stick!",
    "Fact: Al dente means 'to the tooth' in Italian, describing pasta's ideal texture.",
    "Tip: Save a cup of pasta water to help thicken your sauce.",
    "Fact: Pasta was first referenced in Sicily in 1154.",
    "Tip: Stir pasta occasionally to prevent sticking.",
    "Fact: The average Italian eats 51 pounds of pasta per year!",
    "Tip: Pair pasta shapes with the right sauce for best results."
]

def display_pasta_options():
    """Display all available pasta types and their cooking time ranges"""
    print("\n🍝 Available Pasta Types:")
    print("-" * 30)
    for i, (pasta, (min_time, max_time)) in enumerate(pasta_times.items(), 1):
        print(f"{i}. {pasta.title()} - {min_time}-{max_time} minutes")
    print("-" * 30)

def get_user_choice():
    """Get user's pasta selection"""
    pasta_list = list(pasta_times.keys())
    while True:
        try:
            choice = int(input("Enter the number of your pasta choice: "))
            if 1 <= choice <= len(pasta_list):
                return pasta_list[choice - 1]
            else:
                print(f"Please enter a number between 1 and {len(pasta_list)}")
        except ValueError:
            print("Please enter a valid number!")

def get_cooking_time(pasta_type):
    """Prompt user to select a time within the range for the chosen pasta type"""
    min_time, max_time = pasta_times[pasta_type]
    if DEBUG_MODE:
        return 0.1  # 6 seconds in minutes
    if min_time == max_time:
        return min_time
    print(f"\nThe recommended cooking time for {pasta_type.title()} is between {min_time} and {max_time} minutes.")
    while True:
        try:
            user_time = float(input(f"Enter your desired cooking time in minutes ({min_time}-{max_time}): "))
            if min_time <= user_time <= max_time:
                return user_time
            else:
                print(f"Please enter a time between {min_time} and {max_time} minutes.")
        except ValueError:
            print("Please enter a valid number!")

def run_timer(pasta_type, minutes):
    """Run the countdown timer with fun facts and sound notification"""
    print(f"\n🔥 Starting timer for {pasta_type.title()}")
    print(f"⏰ Cooking time: {minutes} minutes")
    print("Timer starting in 3 seconds...")
    time.sleep(3)
    total_seconds = int(minutes * 60)
    fact = random.choice(fun_facts)
    for remaining in range(total_seconds, 0, -1):
        mins, secs = divmod(remaining, 60)
        timer_display = f"{mins:02d}:{secs:02d}"
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"🍝 Cooking {pasta_type.title()}")
        print(f"⏰ Time remaining: {timer_display}")
        print(f"💡 {fact}")
        print("Press Ctrl+C to cancel")
        time.sleep(1)
    os.system('cls' if os.name == 'nt' else 'clear')
    print("🎉 TIME'S UP! 🎉")
    print(f"Your {pasta_type} is ready!")
    print("Remember to taste test before serving! 👨‍🍳")
    # Play sound notification if available
    if SOUND_AVAILABLE:
        try:
            playsound('alarm.mp3')
        except Exception:
            print("(Sound notification failed.")
    else:
        print("(Install 'playsound' for sound notification.)")

def prompt_restart():
    """Ask the user if they want to restart or exit."""
    while True:
        answer = input("\nWould you like to start another timer? (y/n): ").strip().lower()
        if answer in ("y", "yes"):
            return True
        elif answer in ("n", "no"):
            print("Goodbye! 👋")
            return False
        else:
            print("Please enter 'y' or 'n'.")

def main():
    """Main program function with restart option"""
    print("🍝 Welcome to the Pasta Timer! 🍝")
    while True:
        try:
            display_pasta_options()
            selected_pasta = get_user_choice()
            cooking_time = get_cooking_time(selected_pasta)
            run_timer(selected_pasta, cooking_time)
            if not prompt_restart():
                break
        except KeyboardInterrupt:
            print("\n\n⏹️  Timer cancelled. Happy cooking! 👋")
            break
        except Exception as e:
            print(f"\nSomething went wrong: {e}")

if __name__ == "__main__":
    main()