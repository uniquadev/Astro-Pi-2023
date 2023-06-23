import plotly.graph_objects as go

VCI_VALUE = "20.08%"
VALUE = ["90-100%", "80-90%", "70-80%", "60-70%", "50-60%", "40-50%", "30-40%", "20-30%", "10-20%", "0-10%"]
CATEGORY = ["No drought", "No drought", "No drought", "No drought", "No drought", "No drought", "Light drought", "Moderate drought", "Severe drought", "Extreme drought"]
GREEN_TO_RED_COLOR = ["#027148", "#027148", "#027148", "#027148", "#027148", "#027148", "#FFA500", "#FFA500", "#FF0000", "#FF0000"]

fig = go.Figure(
    data = [
        go.Table(
            columnwidth = [30, 100],
            header=dict(
                line_color='white',
                fill_color='azure',
                font=dict(color='black', size=14, family='Arial'),
                values=['<b>Value</b>', '<b>Category</b>']
            ),
            cells=dict(
                font=dict(color=['black', 'white'], size=12),
                line_color='white',
                fill=dict(
                    color=['azure', GREEN_TO_RED_COLOR]  # Color only the first cell
                ),
                values=[VALUE, CATEGORY],
                # Apply HTML table styling to adjust the size of the left column
                height=30,
            )
        )    
    ]
)

# Update the layout
fig.update_layout(
    autosize=True,
    margin=dict(l=200, r=200, t=150, b=0),
    title=dict(
        text=f"<b>Vegetation Condition Index (VCI={VCI_VALUE})</b>",
        font=dict(size=20, color='black'),
    )
)

fig.show()