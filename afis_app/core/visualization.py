import plotly.express as px

def create_interactive_image(image, title=""):
    # Detecta si es una imagen BGR/RGB a color o en escala de grises/binaria
    if len(image.shape) == 3:
        fig = px.imshow(image)
    else:
        fig = px.imshow(image, binary_string=True)
    
    fig.update_layout(
        title=dict(text=title, font=dict(color="white", size=16)),
        margin=dict(l=0, r=0, t=30, b=0),
        coloraxis_showscale=False,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        dragmode="pan",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        autosize=True
    )
    
    fig.update_yaxes(scaleanchor="x", scaleratio=1, autorange="reversed")
    fig.update_xaxes(fixedrange=False)
    fig.update_yaxes(fixedrange=False)
    
    return fig