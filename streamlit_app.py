import streamlit as st
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from pasta_database import PastaDatabase
from timer import TimerManager, NotificationManager, TimerObserver
from models import TimerEvent, PastaInfo
from validators import CustomPastaValidator

# Configure Streamlit page
st.set_page_config(
    page_title="🍝 Pasta Timer",
    page_icon="🍝",
    layout="wide",
    initial_sidebar_state="expanded"
)

class StreamlitTimerObserver(TimerObserver):
    """Observer for Streamlit GUI updates"""
    
    def __init__(self):
        self.events = []
        self.lock = threading.Lock()
    
    def on_timer_tick(self, event: TimerEvent) -> None:
        with self.lock:
            self.events.append(("tick", event))
    
    def on_timer_finished(self, event: TimerEvent) -> None:
        with self.lock:
            self.events.append(("finished", event))
    
    def on_timer_cancelled(self, event: TimerEvent) -> None:
        with self.lock:
            self.events.append(("cancelled", event))
    
    def on_timer_paused(self, event: TimerEvent) -> None:
        with self.lock:
            self.events.append(("paused", event))
    
    def on_timer_resumed(self, event: TimerEvent) -> None:
        with self.lock:
            self.events.append(("resumed", event))
    
    def get_and_clear_events(self):
        with self.lock:
            events = self.events.copy()
            self.events.clear()
            return events

# Initialize session state
def init_session_state():
    if 'pasta_db' not in st.session_state:
        st.session_state.pasta_db = PastaDatabase()
    
    if 'timer_manager' not in st.session_state:
        st.session_state.timer_manager = TimerManager()
    
    if 'notification_manager' not in st.session_state:
        st.session_state.notification_manager = NotificationManager()
    
    if 'observer' not in st.session_state:
        st.session_state.observer = StreamlitTimerObserver()
    
    if 'debug_mode' not in st.session_state:
        st.session_state.debug_mode = False
    
    if 'current_facts' not in st.session_state:
        st.session_state.current_facts = {}
    
    if 'sidebar_fact' not in st.session_state:
        st.session_state.sidebar_fact = st.session_state.pasta_db.get_random_fact()

def render_header():
    """Render the main header"""
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <h1>🍝 Pasta Timer</h1>
        <p style="font-size: 1.2em; color: #666;">Never overcook your pasta again!</p>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Render the sidebar with debug mode and info"""
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Debug mode toggle
        debug_mode = st.checkbox(
            "🔧 Debug Mode", 
            value=st.session_state.debug_mode,
            help="All timers will run for 6 seconds only"
        )
        if debug_mode != st.session_state.debug_mode:
            st.session_state.debug_mode = debug_mode
            if debug_mode:
                st.success("Debug mode enabled! All timers will run for 6 seconds.")
        
        st.divider()
        
        # Timer statistics
        st.header("📊 Statistics")
        active_timers = st.session_state.timer_manager.get_active_timers()
        running_count = len([t for t in active_timers if t['status'] == 'running'])
        paused_count = len([t for t in active_timers if t['status'] == 'paused'])
        finished_count = len([t for t in active_timers if t['status'] == 'finished'])
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("🔥 Running", running_count)
            st.metric("⏸️ Paused", paused_count)
        with col2:
            st.metric("✅ Finished", finished_count)
            st.metric("📝 Custom Pasta", st.session_state.pasta_db.get_custom_pasta_count())
        
        st.divider()
        
        # Random pasta fact
        st.header("💡 Pasta Fact")
        if st.button("🎲 New Fact"):
            st.session_state.sidebar_fact = st.session_state.pasta_db.get_random_fact()
        
        st.info(st.session_state.sidebar_fact)

def render_pasta_selection():
    """Render pasta type selection"""
    st.header("🍝 Select Pasta Type")
    
    built_in = st.session_state.pasta_db.get_built_in_pasta_types()
    custom = st.session_state.pasta_db.get_custom_pasta_types()
    
    # Organize pasta types
    pasta_options = {}
    for pasta in built_in:
        pasta_options[f"{pasta.name.title()} ({pasta.min_time}-{pasta.max_time} min)"] = pasta
    
    for pasta in custom:
        usage_text = f" - Used {pasta.usage_count}x" if pasta.usage_count > 0 else ""
        pasta_options[f"⭐ {pasta.name.title()} ({pasta.min_time}-{pasta.max_time} min){usage_text}"] = pasta
    
    if not pasta_options:
        st.error("No pasta types available!")
        return None
    
    selected_option = st.selectbox(
        "Choose your pasta type:",
        list(pasta_options.keys()),
        help="Built-in types and custom types (marked with ⭐) are available"
    )
    
    if selected_option:
        return pasta_options[selected_option]
    return None

def render_timer_creation(pasta_info: PastaInfo):
    """Render timer creation form"""
    st.header("⏰ Set Cooking Time")
    
    # Show pasta info
    st.info(f"**{pasta_info.name.title()}**: Recommended cooking time is {pasta_info.min_time}-{pasta_info.max_time} minutes")
    
    # Time selection
    if pasta_info.min_time == pasta_info.max_time:
        cooking_time = pasta_info.min_time
        st.success(f"Using standard cooking time: {cooking_time} minutes")
    else:
        cooking_time = st.slider(
            "Cooking time (minutes)",
            min_value=float(pasta_info.min_time),
            max_value=float(pasta_info.max_time),
            value=float((pasta_info.min_time + pasta_info.max_time) / 2),
            step=0.5,
            help=f"Recommended range: {pasta_info.min_time}-{pasta_info.max_time} minutes"
        )
    
    if st.session_state.debug_mode:
        st.warning("⚠️ Debug mode: Timer will run for 6 seconds regardless of selected time")
    
    # Start timer button
    if st.button("🔥 Start Timer", type="primary", use_container_width=True):
        timer_id = st.session_state.timer_manager.add_timer(
            pasta_info.name, 
            cooking_time, 
            st.session_state.debug_mode
        )
        
        # Store pasta fact for this timer
        st.session_state.current_facts[timer_id] = st.session_state.pasta_db.get_random_fact()
        
        # Start the timer
        if st.session_state.timer_manager.start_timer(timer_id, st.session_state.observer):
            # Increment usage for custom pasta
            if pasta_info.is_custom:
                st.session_state.pasta_db.increment_pasta_usage(pasta_info.name)
            
            # Show notification
            time_text = f"{int(cooking_time)} minute{'s' if cooking_time != 1 else ''}"
            if cooking_time != int(cooking_time):
                time_text = f"{cooking_time:.1f} minutes"
            
            st.session_state.notification_manager.show_notification(
                title="🍝 Pasta Timer - Started",
                message=f"{pasta_info.name.title()} timer started ({time_text})",
                pasta_type=pasta_info.name,
                play_sound=False
            )
            
            st.success(f"✅ Timer started for {pasta_info.name.title()}! (ID: {timer_id})")
            st.rerun()
        else:
            st.error("❌ Failed to start timer")

def render_active_timers():
    """Render active timers display"""
    active_timers = st.session_state.timer_manager.get_active_timers()
    
    if not active_timers:
        st.info("📭 No active timers")
        return
    
    st.header("🕐 Active Timers")
    
    # Clean up finished timers
    st.session_state.timer_manager.cleanup_finished_timers()
    
    for timer in active_timers:
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            
            with col1:
                status_emoji = {
                    'running': '🔥',
                    'paused': '⏸️',
                    'finished': '✅',
                    'cancelled': '❌',
                    'error': '⚠️'
                }.get(timer['status'], '❓')
                
                st.markdown(f"**{status_emoji} {timer['pasta_type'].title()}**")
                st.caption(f"Timer ID: {timer['id']}")
            
            with col2:
                if timer['status'] in ['running', 'paused']:
                    # For active timers, show remaining time
                    remaining_seconds = max(0, timer['remaining_seconds'])
                    remaining_time = timedelta(seconds=remaining_seconds)
                    st.metric("Time Remaining", str(remaining_time))
                else:
                    elapsed = datetime.now() - timer['start_time']
                    st.metric("Total Time", str(elapsed).split('.')[0])
            
            with col3:
                if timer['status'] in ['running', 'paused']:
                    # Calculate progress
                    total_seconds = timer['total_seconds']
                    remaining_seconds = timer['remaining_seconds']
                    progress = max(0, (total_seconds - remaining_seconds) / total_seconds)
                    st.progress(progress)
                    
                    # Show pasta fact if available
                    if timer['id'] in st.session_state.current_facts:
                        with st.expander("💡 Pasta Fact"):
                            st.write(st.session_state.current_facts[timer['id']])
            
            with col4:
                if timer['status'] == 'running':
                    if st.button("⏸️", key=f"pause_{timer['id']}", help="Pause timer"):
                        st.session_state.timer_manager.pause_timer(timer['id'])
                        st.rerun()
                elif timer['status'] == 'paused':
                    if st.button("▶️", key=f"resume_{timer['id']}", help="Resume timer"):
                        st.session_state.timer_manager.resume_timer(timer['id'])
                        st.rerun()
                
                if timer['status'] in ['running', 'paused']:
                    if st.button("❌", key=f"cancel_{timer['id']}", help="Cancel timer"):
                        st.session_state.timer_manager.cancel_timer(timer['id'])
                        st.rerun()
            
            st.divider()

def render_custom_pasta_management():
    """Render custom pasta management"""
    st.header("⭐ Manage Custom Pasta Types")
    
    tab1, tab2 = st.tabs(["➕ Add New", "📝 Manage Existing"])
    
    with tab1:
        st.subheader("Add New Custom Pasta Type")
        
        with st.form("add_custom_pasta"):
            pasta_name = st.text_input(
                "Pasta Name",
                placeholder="e.g., Gnocchi, Tortellini",
                help="Enter the name of your custom pasta type"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                min_time = st.number_input(
                    "Minimum Cooking Time (minutes)",
                    min_value=1,
                    max_value=30,
                    value=8,
                    help="Minimum recommended cooking time"
                )
            
            with col2:
                max_time = st.number_input(
                    "Maximum Cooking Time (minutes)",
                    min_value=1,
                    max_value=30,
                    value=10,
                    help="Maximum recommended cooking time"
                )
            
            submitted = st.form_submit_button("➕ Add Pasta Type", type="primary")
            
            if submitted:
                try:
                    if st.session_state.pasta_db.add_custom_pasta(pasta_name, min_time, max_time):
                        st.success(f"✅ Added {pasta_name.title()} to your custom pasta types!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to add pasta type")
                except ValueError as e:
                    st.error(f"❌ {str(e)}")
    
    with tab2:
        st.subheader("Existing Custom Pasta Types")
        
        custom_pasta = st.session_state.pasta_db.get_custom_pasta_types()
        
        if not custom_pasta:
            st.info("📭 No custom pasta types yet. Add some in the 'Add New' tab!")
        else:
            for pasta in custom_pasta:
                with st.container():
                    col1, col2, col3 = st.columns([3, 2, 1])
                    
                    with col1:
                        st.markdown(f"**{pasta.name.title()}**")
                        st.caption(f"Cooking time: {pasta.min_time}-{pasta.max_time} minutes")
                    
                    with col2:
                        usage_text = "Never used" if pasta.usage_count == 0 else f"Used {pasta.usage_count} time{'s' if pasta.usage_count != 1 else ''}"
                        st.caption(usage_text)
                        if hasattr(pasta, 'created_date'):
                            created_date = datetime.fromisoformat(pasta.created_date).strftime("%Y-%m-%d")
                            st.caption(f"Created: {created_date}")
                    
                    with col3:
                        if st.button("🗑️", key=f"delete_{pasta.name}", help=f"Delete {pasta.name}"):
                            if st.session_state.pasta_db.remove_custom_pasta(pasta.name):
                                st.success(f"✅ Deleted {pasta.name.title()}")
                                st.rerun()
                            else:
                                st.error(f"❌ Failed to delete {pasta.name}")
                    
                    st.divider()

def process_timer_events():
    """Process timer events from the observer"""
    events = st.session_state.observer.get_and_clear_events()
    
    for event_type, event in events:
        if event_type == "finished":
            # Show completion notification
            st.session_state.notification_manager.show_notification(
                title="🍝 Pasta Timer - Finished!",
                message=f"{event.pasta_type.title()} is ready! Time to eat!",
                pasta_type=event.pasta_type,
                play_sound=True
            )
            
            # Show in-app notification
            st.success(f"🍝 **{event.pasta_type.title()} is ready!** Time to eat!")
            st.balloons()

def main():
    """Main Streamlit application"""
    init_session_state()
    
    # Process any timer events
    process_timer_events()
    
    # Render UI
    render_header()
    render_sidebar()
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["🔥 Start Timer", "🕐 Active Timers", "⭐ Custom Pasta"])
    
    with tab1:
        pasta_info = render_pasta_selection()
        if pasta_info:
            render_timer_creation(pasta_info)
    
    with tab2:
        render_active_timers()
    
    with tab3:
        render_custom_pasta_management()
    
    # Auto-refresh for timer updates (only if we have active timers)
    active_timers = st.session_state.timer_manager.get_active_timers()
    if any(t['status'] in ['running', 'paused'] for t in active_timers):
        time.sleep(1)
        st.rerun()

if __name__ == "__main__":
    main() 