Run ChromaDB (or other) locally
Ingest latest General Conference text
    Use download_gc_talks.py to get the text
    Consider using ingest_folder in chroma_demo.py to ingest into your db
Build chatbot that answers doctrinal questions using GC content
    Consider using query_whole_documents from chroma_demo.py
    Chat UX should expect one question per user input, with a single response (no back-and-forth on a topic)
    Consider the system prompt—how will the agent know how to use the extra content?

The first step was to build my Chat Bot. I used similar code from unit 1 to format my chatbot. As I created a response, I first added the user query into the chat history, then called the rag system, then added the rag results into the chat history. 