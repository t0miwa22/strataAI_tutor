# strataAI_tutor

Welcome to the strataAI Tutor repository. This project is developed to provide an AI-powered tutoring experience for StrataScratch users. Leveraging the capabilities of OpenAI's GPT-3.5 Turbo model, this tutor is designed to be intuitive, responsive, and adaptive to various user queries.

Files Description:
📜 ai_tutor_backend.py
Description: The core backend component of the strataAI Tutor.
Features:
Houses the logic and functions integral to the AI tutor's operation.
Interacts seamlessly with the OpenAI API.
Handles and processes user queries efficiently.

📊 ai_tutor_faqs.xlsx
Description: A comprehensive Excel database.
Features:
Compiles frequently asked questions alongside their respective answers.
Serves as the tutor's primary data reference before leveraging AI-driven responses.

📄 ai_tutor_sys_content
Description: Textual context repository.
Features:
Provides necessary context to enhance AI model understanding and accuracy.

🔧 tool_bot_sts_content
Description: Bot prompt toolkit.
Features:
Contains prompts tailored for addressing non-programming-related inquiries.

🌐 geckodriver
Description: Driver for browser interfacing.
Features:
Acts as the Firefox driver essential for the HTML parser's smooth functioning.

📚 final_updated_clean_ss_questions
Description: Sample question database.

Getting Started:
Ensure you have Python and all necessary libraries installed.
Set up an environment variable for your OpenAI API key or modify the backend script to include it directly.
Run the main application (ensure you have Streamlit or the respective frontend library installed).

Usage:
Once the application is up and running:

Users can type in their questions or select from a dropdown of FAQs.
The AI tutor will process the query and provide a relevant response based on the context.


Collaborators: Tomiwa Adeyemo, Matt Ogbuehi, Vy Nguyen
