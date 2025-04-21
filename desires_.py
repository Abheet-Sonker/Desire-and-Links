import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import networkx as nx
import os

st.set_page_config(page_title="Desire Reflection App", layout="centered")
st.title("💭 Desire Reflection and Clarity Tool")

# --- 1. User Info ---
user_name = st.text_input("👤 What is your name?")

# --- 2. Main Desire ---
main_desire = st.text_input("✨ What is your main desire?")

# --- 3. Sub-Desires ---
st.subheader("🔍 Sub-Desires")
sub_desires = []
sub_outcomes = []
link_types = []

for i in range(1, 4):
    sd = st.text_input(f"Sub-Desire {i}")
    sub_desires.append(sd)
    outcome = st.text_input(f"What do you hope to get from Sub-Desire {i}?")
    sub_outcomes.append(outcome)
    link = st.selectbox(
        f"Is this link to your main desire Real, Spurious, or Unclear?",
        ["Real", "Spurious", "Unclear"],
        key=f"link_{i}"
    )
    link_types.append(link)

# --- 4. Summary Visualization ---
if st.button("🔎 Analyze and Show Summary"):
    if not user_name or not main_desire or any(not sd for sd in sub_desires):
        st.warning("Please fill in all fields before analyzing.")
    else:
        st.subheader("🧠 Desire Tree Chart")

        # Build the directed graph
        G = nx.DiGraph()
        G.add_node(main_desire)

        for i, (sd, oc, lt) in enumerate(zip(sub_desires, sub_outcomes, link_types)):
            G.add_node(sd)
            G.add_node(oc)
            G.add_edge(main_desire, sd, color=lt)
            G.add_edge(sd, oc, color='gray')

        pos = nx.spring_layout(G, seed=42)

        # Edge color mapping
        color_map = {"Real": "green", "Spurious": "red", "Unclear": "orange", "gray": "gray"}
        edge_traces = []

        # Draw edges from main desire to sub-desires with link type
        for edge in G.edges(data=True):
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            color = color_map.get(edge[2]['color'], "gray")
            label = edge[2]['color'] if edge[2]['color'] in color_map else "Other"
            # Only show legend for the three link types, not for gray outcome links
            show_legend = label in ["Real", "Spurious", "Unclear"]
            edge_traces.append(
                go.Scatter(
                    x=[x0, x1],
                    y=[y0, y1],
                    line=dict(width=2, color=color),
                    hoverinfo='text',
                    mode='lines',
                    name=label if show_legend else None,
                    text=[f"Link: {label}"],
                    showlegend=show_legend
                )
            )

        # Draw nodes
        node_x = []
        node_y = []
        text = []
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            text.append(node)

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            text=text,
            textposition="top center",
            marker=dict(
                showscale=False,
                color='skyblue',
                size=20,
                line_width=2
            ),
            hoverinfo='text'
        )

        # Create figure with all edge traces and node trace
        fig = go.Figure(
            data=edge_traces + [node_trace],
            layout=go.Layout(
                title=dict(text=f"Reflection Tree for {user_name}", font=dict(size=20)),
                showlegend=True,
                hovermode='closest',
                margin=dict(b=20, l=5, r=5, t=40),
                xaxis=dict(showgrid=False, zeroline=False, visible=False),
                yaxis=dict(showgrid=False, zeroline=False, visible=False)
            )
        )

        st.plotly_chart(fig)

        # --- 5. Save Data to Excel ---
        st.subheader("📁 Save Your Reflection")
        data = {
            "Name": user_name,
            "Main Desire": main_desire
        }
        for i in range(3):
            data[f"Sub-Desire {i+1}"] = sub_desires[i]
            data[f"Outcome {i+1}"] = sub_outcomes[i]
            data[f"Link Type {i+1}"] = link_types[i]

        new_df = pd.DataFrame([data])
        excel_file = "all_reflections.xlsx"

        if os.path.exists(excel_file):
            existing_df = pd.read_excel(excel_file)
            updated_df = pd.concat([existing_df, new_df], ignore_index=True)
        else:
            updated_df = new_df

        # Save to Excel (requires openpyxl installed)
        updated_df.to_excel(excel_file, index=False)
        st.success("Your reflection has been saved.")

# --- 6. Admin Option to Download All Reflections ---
st.sidebar.title("Admin")
if st.sidebar.button("📥 Download All Reflections"):
    if os.path.exists("all_reflections.xlsx"):
        with open("all_reflections.xlsx", "rb") as f:
            st.download_button("Download Excel File", f, file_name="all_reflections.xlsx")
    else:
        st.sidebar.warning("No data available yet.")
