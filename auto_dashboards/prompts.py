def streamlit_prompt(code: str):
    prompt = "Translate the following Python code to Streamlit dashboard:\n\n"
    prompt += "```python\n"
    prompt += code
    prompt += "```\n"
    prompt += "Only output the Streamlit code and no comments or explanations."

    return prompt

def solara_prompt(code: str):
    prompt = "Translate the following Python code to Solara dashboard:\n\n"
    prompt += """For example, here is how sliders are created in Solara:
```python
import solara

int_value = solara.reactive(42)


@solara.component
def Page():
    solara.SliderInt("Some integer", value=int_value, min=-10, max=120)
    solara.Markdown(f"**Int value**: {int_value.value}")
    with solara.Row():
        solara.Button("Reset", on_click=lambda: int_value.set(42))
```
"""
    prompt += "```python\n"
    prompt += code
    prompt += "```\n"
    prompt += "Only output the Solara code and no comments or explanations."

    return prompt