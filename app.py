import streamlit as st
import requests

from evaluation import run_evaluation, create_graphs

st.set_page_config(
    page_title="LLM Router",
    page_icon="",
    layout="wide"
)

st.markdown("""
<h1 style='text-align: center; color: #4CAF50;'>
Smart LLM Router with Semantic Caching
</h1>
<p style='text-align: center; color: gray;'>
Optimize cost & latency using intelligent routing + caching
</p>
""", unsafe_allow_html=True)

st.divider()

if "last_result" not in st.session_state:
    st.session_state.last_result = None

chat_tab, evaluation_tab = st.tabs(["Chat", "Evaluation"])

with chat_tab:
    query = st.text_input("Enter your question")

    if st.button("Submit", use_container_width=True):
        if query:
            with st.spinner("Thinking..."):
                try:
                    res = requests.post(
                        "http://127.0.0.1:8000/route",
                        json={"query": query}
                    )

                    st.session_state.last_result = res.json()
                    data = st.session_state.last_result

                    st.success("Response received!")

                    st.markdown("### Answer")
                    st.markdown(f"""
                    <div style="
                        background-color:#1e1e1e;
                        padding:20px;
                        border-radius:10px;
                        border:1px solid #444;
                        font-size:18px;
                        line-height:1.7;
                        min-height:180px;">
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
                        st.markdown(metric_box("Model", data.get("model")), unsafe_allow_html=True)

                    with col2:
                        st.markdown(metric_box("Latency", f"{data.get('latency')} sec"), unsafe_allow_html=True)

                    with col3:
                        st.markdown(metric_box("Cost", f"${data.get('cost')}"), unsafe_allow_html=True)

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

    if st.session_state.last_result:
        st.caption("Your latest question is kept in cache now you can browse the evaluation tab.")

with evaluation_tab:
    st.markdown("### Evaluation Dashboard")
    st.caption("Run workload tests at the cache threshold of 0.55")

    if st.button("Generate Evaluation Report", use_container_width=True):
        with st.spinner("Running evaluation (this may take a minute)..."):
            try:
                repetition_df = run_evaluation(size=4)
                graphs = create_graphs(repetition_df)

                st.success("✓ Evaluation complete!")
                
                st.markdown("#### Key Insights at Threshold 0.55")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**1️⃣ Cache Hit Rate vs Repetition Rate**")
                    st.caption("Shows cache usage at the fixed threshold of 0.55")
                    st.pyplot(graphs["1. Hit Rate at 0.55"], use_container_width=True)

                with col2:
                    st.markdown("**2️⃣ Cost Savings vs Repetition Rate**")
                    st.caption("Proves your system reduces cost with more repeated queries")
                    st.pyplot(graphs["2. Cost Savings vs Repetition"], use_container_width=True)

                col3, col4 = st.columns(2)
                with col3:
                    st.markdown("**3️⃣ False Positives vs Repetition Rate**")
                    st.caption("Shows wrong cached answers at the fixed threshold of 0.55")
                    st.pyplot(graphs["3. False Positives at 0.55"], use_container_width=True)

                with col4:
                    st.markdown("**4️⃣ Average Latency vs Repetition Rate(With Cache)**")
                    st.caption("Shows performance improvement (faster responses with caching)")
                    st.pyplot(graphs["4. Latency vs Repetition"], use_container_width=True)

                st.divider()
                st.markdown("#### Results Data")
                st.dataframe(repetition_df, use_container_width=True)

            except Exception as e:
                st.error(f"Evaluation error: {e}")
