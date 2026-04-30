import streamlit as st
import requests

st.set_page_config(
    page_title="LLM Router",
    page_icon="",
    layout="centered"
)

# Header
st.markdown("""
<h1 style='text-align: center; color: #4CAF50;'>
Smart LLM Router
</h1>
<p style='text-align: center; color: gray;'>
Optimize cost & latency using intelligent routing + caching
</p>
""", unsafe_allow_html=True)

st.divider()

# Input
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

                st.success(" Response received!")

                # Answer box
                st.markdown("###  Answer")
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

                #  Decision
                st.markdown("###  System Decision")
                st.info(data.get("reason"))

                #  Metrics
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

                #  Cache placeholder
                st.markdown("###  Cache Status")
                st.warning("Cache module will be integrated soon")

            except Exception as e:
                st.error(f"Error: {e}")