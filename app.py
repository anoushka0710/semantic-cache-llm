import streamlit as st
import requests

from evaluation import run_evaluation, create_graphs

st.set_page_config(
    page_title="LLM Router",
    page_icon="",
    layout="centered"
)

st.markdown("""
<h1 style='text-align: center; color: #4CAF50;'>
Smart LLM Router
</h1>
<p style='text-align: center; color: gray;'>
Optimize cost & latency using intelligent routing + caching
</p>
""", unsafe_allow_html=True)

st.divider()

query = st.text_input("Enter your question")

if st.button("Submit", use_container_width=True):
    if query:
        with st.spinner("Thinking..."):
            try:
                res = requests.post(
                    "http://127.0.0.1:8000/route",
                    json={"query": query}
                )

                data = res.json()

                st.success("Response received!")

                st.markdown("### Answer")
                st.markdown(f"""
                <div style="
                    background-color:#1e1e1e;
                    padding:15px;
                    border-radius:10px;
                    border:1px solid #444;">
                    {data.get("response")}
                </div>
                """, unsafe_allow_html=True)

                st.divider()

                st.markdown("### System Decision")
                st.info(data.get("reason"))

                st.markdown("### Performance")

                col1, col2, col3 = st.columns(3)

                def metric_box(title, value):
                    return f"""
                    <div style="
                        background-color:#1f2937;
                        padding:18px;
                        border-radius:12px;
                        border:1px solid #374151;
                        text-align:center;">
                        <div style="color:gray; font-size:14px;">{title}</div>
                        <div style="font-size:20px; font-weight:bold; color:white;">
                            {value}
                        </div>
                    </div>
                    """

                with col1:
                    st.markdown(
                        metric_box("Model", data.get("model")),
                        unsafe_allow_html=True
                    )

                with col2:
                    st.markdown(
                        metric_box("Latency", f"{data.get('latency')} sec"),
                        unsafe_allow_html=True
                    )

                with col3:
                    st.markdown(
                        metric_box("Cost", f"${data.get('cost')}"),
                        unsafe_allow_html=True
                    )

                st.markdown("### Cache Status")

                if data.get("cache_hit"):
                    st.success("Cache HIT - response reused, no LLM cost")
                elif data.get("cache_status") == "DISABLED":
                    st.info("Cache disabled for this request")
                else:
                    st.warning("Cache MISS - response saved for next time")

            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("Please enter a question first.")


st.divider()

st.markdown("### Evaluation Graphs")

with st.expander("Run cache evaluation", expanded=True):
    st.info("This quick test uses size = 4 to keep API calls low.")

    if st.button("Generate Graphs", use_container_width=True):
        with st.spinner("Running evaluation with size=4..."):
            try:
                results_df = run_evaluation(size=2)
                graphs = create_graphs(results_df)

                st.markdown("#### Evaluation Results")
                st.dataframe(results_df, use_container_width=True)

                for title, fig in graphs.items():
                    st.markdown(f"#### {title}")
                    st.pyplot(fig)

            except Exception as e:
                st.error(f"Evaluation error: {e}")
