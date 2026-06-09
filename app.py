import gradio as gr
from query import ask

def handle_query(question):
    if not question.strip():
        return "Please enter a question.", ""
    result = ask(question)
    sources = "\n".join(f"• {s}" for s in result["sources"])
    return result["answer"], sources

with gr.Blocks(title="USC CS Unofficial Guide") as demo:
    gr.Markdown("# USC CS Unofficial Guide")
    gr.Markdown("Ask questions about USC CS courses and professors. Answers are grounded in real student reviews.")
    with gr.Row():
        inp = gr.Textbox(label="Your question", placeholder='e.g. "What do students say about Saty?"', lines=2)
        btn = gr.Button("Ask", variant="primary")
    answer = gr.Textbox(label="Answer", lines=10)
    sources = gr.Textbox(label="Sources", lines=3)
    gr.Examples(
        examples=[
            ["What do students say about Saty Raghavachary's teaching style?"],
            ["How difficult do students think CSCI 572 is?"],
            ["What concerns were raised about CSCI 571?"],
            ["What do students say about the workload in DSCI 552?"],
            ["How do students compare CSCI 526 and CSCI 538?"],
            ["What is the best restaurant near USC?"],
        ],
        inputs=inp,
    )
    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])

if __name__ == "__main__":
    demo.launch()
