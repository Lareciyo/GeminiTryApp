import streamlit as st
import psycopg2
import os
from datetime import datetime

# Render automatically provides DATABASE_URL if you set it in Environment
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

# Initialize the Database Table
def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            task TEXT NOT NULL,
            priority TEXT DEFAULT 'Low',
            due TEXT,
            done BOOLEAN DEFAULT FALSE
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

st.set_page_config(page_title="GeminiTry To-Do", page_icon="✅")
init_db()

st.title("🚀 GeminiTry Pro To-Do")

# --- UI: Add Task ---
with st.expander("➕ Add New Task"):
    with st.form("task_form", clear_on_submit=True):
        task_name = st.text_input("Task Description")
        col1, col2 = st.columns(2)
        priority = col1.selectbox("Priority", ["Low", "Medium", "High"])
        due_date = col2.date_input("Due Date")
        
        if st.form_submit_button("Add Task"):
            if task_name:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO tasks (task, priority, due) VALUES (%s, %s, %s)",
                    (task_name, priority, str(due_date))
                )
                conn.commit()
                st.success("Task added!")
                st.rerun()

# --- UI: Display Tasks ---
st.subheader("Your Tasks")
conn = get_connection()
cur = conn.cursor()
cur.execute("SELECT id, task, priority, due, done FROM tasks ORDER BY done ASC, id DESC")
rows = cur.fetchall()

for row in rows:
    tid, text, prio, due, is_done = row
    cols = st.columns([0.5, 3, 1, 1])
    
    # Toggle Done
    if cols[0].checkbox("", value=is_done, key=f"check_{tid}"):
        if not is_done:
            cur.execute("UPDATE tasks SET done = True WHERE id = %s", (tid,))
            conn.commit()
            st.rerun()
    elif is_done:
        cur.execute("UPDATE tasks SET done = False WHERE id = %s", (tid,))
        conn.commit()
        st.rerun()

    # Display Text
    task_style = f"~~{text}~~" if is_done else f"**{text}**"
    cols[1].markdown(task_style)
    cols[2].write(f"prio: {prio}")
    
    # Delete Button
    if cols[3].button("🗑️", key=f"del_{tid}"):
        cur.execute("DELETE FROM tasks WHERE id = %s", (tid,))
        conn.commit()
        st.rerun()

cur.close()
conn.close()
