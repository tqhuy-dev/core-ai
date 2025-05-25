import gradio as gr
import os

def process_file(file_obj):
    """
    Process the uploaded file and return a message.
    This function is called when a file is uploaded.
    """
    if file_obj is None:
        return None, gr.update(visible=False), gr.update(visible=False)

    # Get the file name
    file_name = os.path.basename(file_obj.name)

    # Here you would typically process the file
    # For demonstration, we'll just return the file name

    # Make the text input visible and hide the file input
    return f"File '{file_name}' uploaded successfully. Please enter your text:", gr.update(visible=True), gr.update(visible=False)

def process_text(text):
    """
    Process the entered text.
    This function is called when text is submitted.
    """
    if not text:
        return "No text entered."

    # Here you would typically process the text
    # For demonstration, we'll just return the text

    return f"You entered: {text}"

def reset_interface():
    """
    Reset the interface to its initial state.
    """
    return None, gr.update(value="", visible=False), gr.update(visible=True)

# Create the Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("# Dynamic Form Application")

    # Output area for messages
    output_message = gr.Markdown()

    # Text input (initially hidden)
    text_input = gr.Textbox(
        label="Enter your text",
        placeholder="Type here...",
        visible=False
    )

    # File input (initially visible)
    file_input = gr.File(
        label="Upload a file",
    )

    # Submit buttons
    with gr.Row():
        file_submit = gr.Button("Submit File")
        text_submit = gr.Button("Submit Text", visible=False)
        reset_button = gr.Button("Reset")

    # Set up event handlers
    file_submit.click(
        fn=process_file,
        inputs=[file_input],
        outputs=[output_message, text_input, file_input]
    ).then(
        fn=lambda: gr.update(visible=True),
        outputs=[text_submit]
    )

    text_submit.click(
        fn=process_text,
        inputs=[text_input],
        outputs=[output_message]
    )

    reset_button.click(
        fn=reset_interface,
        outputs=[output_message, text_input, file_input]
    ).then(
        fn=lambda: [gr.update(visible=False), gr.update(visible=True)],
        outputs=[text_submit, file_submit]
    )

# Launch the app
if __name__ == "__main__":
    demo.launch()
