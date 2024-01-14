# **AI Data Analyzer for WhatsApp Chats Report**
## **Project Overview**
Our project, the WhatsApp Conversation Analyzer, was conceived as a tool to interpret and analyze the subtleties of daily WhatsApp chats. The primary objective was to provide users with a deeper understanding of their conversations, identifying patterns, feelings, and topics. To achieve this, we developed a Python based application with a user-friendly web interface utilizing Streamlit. Central to our analysis process was the integration of the Replicate API with the advanced Large Language Model (LLM) meta2-70B-chat, a decision driven by the model's exceptional capabilities in understanding and generating human-like text.

## **Evaluation**
The evaluation phase involved assessing the analyzer's ability to interpret and provide meaningful insights into WhatsApp conversations. We focused on the accuracy of the analysis, the relevance of the insights provided, and the user experience offered by the Streamlit interface.

## **Troubles and Solutions**
Initially, we faced a significant challenge regarding data processing. The team, inspired by Maciej's suggestion, initially attempted to "vectorize" the chat data for analysis. This approach seemed promising as it's commonly used in **machine learning training** for transforming text, images, or videos into a numerical vector format. However, we discovered that LLMs,like the meta2-70B-chat model we were using, require plain text inputs rather than vectorized data. This revelation necessitated a strategic pivot.

Our revised approach involved filtering chat data by date (specifically by day) and passing these segmented conversations to the chatbot. This method proved to be more aligned with the LLM's operational framework. Implementing this solution required additional coding effort to ensure efficient data filtering and handling, but it significantly improved the model's ability to analyze and interpret the chats meaningfully.

## **Conclusion**
The project culminated in the successful development of a WhatsApp conversation analyzer that could provide insightful analyses of daily conversations. Despite encountering initial methodological challenges, the team adapted and found an effective solution that leveraged the capabilities of the LLM meta2-70B-chat model. The final product not only meets the initial project objectives but also offers an intuitive and user-friendly way for individuals to gain deeper insights into their WhatsApp chats.a